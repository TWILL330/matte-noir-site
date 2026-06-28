const RAPIDAPI_HOST = 'tiktok-scraper7.p.rapidapi.com';

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { tool, params = {}, rapidKey, anthropicKey } = req.body || {};
  const rKey = process.env.RAPIDAPI_KEY || rapidKey || '';
  const aKey = process.env.ANTHROPIC_API_KEY || anthropicKey || '';

  if (!tool) return res.status(400).json({ error: 'Missing tool name' });

  try {
    switch (tool) {
      case 'search_videos':       return res.json(await searchVideos(params, rKey));
      case 'find_viral_template': return res.json(await findTemplate(params, rKey));
      case 'trend_pulse':         return res.json(await trendPulse(params, aKey));
      case 'score_hook':          return res.json(await scoreHook(params, aKey));
      case 'predict_virality':    return res.json(await predictVirality(params, aKey));
      case 'analyze_account':     return res.json(await analyzeAccount(params, aKey));
      case 'match_voice':         return res.json(await matchVoice(params, aKey));
      case 'viral_remix':         return res.json(await viralRemix(params, aKey));
      default: return res.status(400).json({ error: `Unknown tool: ${tool}` });
    }
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
};

// ─── RapidAPI / TikTok ───────────────────────────────────────────────────────

async function rapidGet(path, key, params = {}) {
  if (!key) throw new Error('RapidAPI key not configured. Add it in Settings.');
  const url = new URL(`https://${RAPIDAPI_HOST}${path}`);
  Object.entries(params).forEach(([k, v]) => v != null && url.searchParams.set(k, String(v)));
  const resp = await fetch(url.toString(), {
    headers: { 'X-RapidAPI-Key': key, 'X-RapidAPI-Host': RAPIDAPI_HOST }
  });
  if (!resp.ok) throw new Error(`TikTok API error ${resp.status}. Check your RapidAPI key.`);
  return resp.json();
}

function mapVideo(v) {
  const id = v.video_id || v.id || '';
  const handle = v.author?.unique_id || v.author?.nickname || '?';
  return {
    description: v.desc || v.description || '',
    author: handle,
    views: v.statistics?.play_count || v.play_count || 0,
    likes: v.statistics?.digg_count || v.digg_count || 0,
    shares: v.statistics?.share_count || v.share_count || 0,
    url: id && handle !== '?' ? `https://www.tiktok.com/@${handle}/video/${id}` : (v.url || '#'),
    hashtags: (v.hashtag_list || []).map(h => typeof h === 'string' ? h : h.title || '').filter(Boolean),
    posted_at: v.create_time ? new Date(v.create_time * 1000).toISOString() : null,
  };
}

async function searchVideos({ query, niche, min_views = 0, window, region, limit = 12 }, key) {
  const q = [query, niche].filter(Boolean).join(' ');
  if (!q) throw new Error('query is required');
  const raw = await rapidGet('/feed/search', key, {
    keywords: q,
    count: Math.min(limit * 2, 30),
    publish_time: window === '24h' ? 1 : window === '7d' ? 7 : 0,
    sort_type: window === '24h' ? 1 : 0,
    region: region || 'US',
  });
  const videos = (raw?.data?.videos || raw?.data || [])
    .map(mapVideo)
    .filter(v => v.views >= min_views)
    .slice(0, limit);
  return { success: true, data: { videos, quality: { level: 'full' } } };
}

async function findTemplate({ niche, min_views = 5000 }, key) {
  const raw = await rapidGet('/feed/search', key, {
    keywords: `${niche} viral`,
    count: 20,
    sort_type: 0,
    region: 'US',
  });
  const templates = (raw?.data?.videos || raw?.data || [])
    .filter(v => (v.statistics?.play_count || 0) >= min_views)
    .slice(0, 8)
    .map(v => {
      const mv = mapVideo(v);
      return {
        hook_pattern: mv.description.substring(0, 100),
        format: 'TikTok',
        avg_views: mv.views,
        why_it_fits: `${Math.round(mv.views / 1000)}K views · @${mv.author}${mv.hashtags.length ? ' · ' + mv.hashtags.slice(0,2).join(' ') : ''}`,
        url: mv.url,
      };
    });
  return { success: true, data: { templates, niche, quality: { level: 'full' } } };
}

// ─── Claude ──────────────────────────────────────────────────────────────────

async function claude(key, system, user) {
  if (!key) throw new Error('Anthropic API key not configured. Add it in Settings.');
  const resp = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': key,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: 'claude-haiku-4-5-20251001',
      max_tokens: 2048,
      system,
      messages: [{ role: 'user', content: user }],
    }),
  });
  const data = await resp.json();
  if (data.error) throw new Error(data.error.message || 'Claude API error');
  const text = data.content?.[0]?.text || '';
  const match = text.match(/\{[\s\S]*\}/);
  if (!match) throw new Error('No JSON in Claude response');
  return JSON.parse(match[0]);
}

async function scoreHook({ text, platform = 'tiktok', niche }, key) {
  const data = await claude(key,
    'You are a viral content expert. Score short-form video hooks. Respond with valid JSON only, no markdown fences.',
    `Score this ${platform} hook${niche ? ` in the ${niche} niche` : ''}:\n\n"${text}"\n\nReturn ONLY this JSON:\n{"score":<0-100>,"percentile":<0-100>,"pattern_match":"<Knowledge Gap|Transformation|Controversy|Authority|Story|Shock|Relatability>","why":"<1-2 sentence verdict referencing a score anchor>","signals":[{"name":"specificity","value":<0-10>,"evidence":"<observation>"},{"name":"emotional_stake","value":<0-10>,"evidence":"<observation>"},{"name":"scroll_stop_velocity","value":<0-10>,"evidence":"<observation>"},{"name":"credibility_signal","value":<0-10>,"evidence":"<observation>"},{"name":"pattern_freshness","value":<0-10>,"evidence":"<observation>"},{"name":"share_trigger","value":<0-10>,"evidence":"<observation>"}],"rewrites":["<improved v1>","<improved v2>","<improved v3>"],"would_fail_because":"<specific counterfactual>","quality":{"level":"full"}}`
  );
  return { success: true, data };
}

async function predictVirality({ script, niche }, key) {
  const data = await claude(key,
    'You are an adversarial viral content analyst. Score scripts with both optimistic and adversarial lenses. Respond with valid JSON only, no markdown fences.',
    `Analyze this script${niche ? ` (${niche} niche)` : ''}:\n\n"${script}"\n\nReturn ONLY this JSON:\n{"virality_score":<0-100 adversarial>,"optimistic_score":<0-100 naive>,"calibration_gap":<optimistic minus virality>,"recommendation":{"verdict":"<SHIP|REWORK|NO-GO>","reason":"<one sentence>"},"signals":[{"name":"hook_strength","value":<0-10>,"evidence":"<observation>"},{"name":"structural_clarity","value":<0-10>,"evidence":"<observation>"},{"name":"retention_design","value":<0-10>,"evidence":"<observation>"},{"name":"emotional_stakes","value":<0-10>,"evidence":"<observation>"},{"name":"shareability_trigger","value":<0-10>,"evidence":"<observation>"},{"name":"specificity_density","value":<0-10>,"evidence":"<observation>"}],"would_fail_because":"<specific counterfactual>","attack_vectors":[{"vector":"<name>","severity":"<high|medium|low>","status":"<present|mitigated>","mitigation":"<how to fix>"}],"vectors_summary":{"total":<n>,"present":<n>,"mitigated":<n>},"quality":{"level":"full"}}`
  );
  return { success: true, data };
}

async function trendPulse({ niche }, key) {
  const data = await claude(key,
    'You are a viral content trend analyst. Respond with valid JSON only, no markdown fences.',
    `What are 3 rising opportunities and 2 saturated patterns right now${niche ? ` in ${niche}` : ' in short-form video'}?\n\nReturn ONLY this JSON:\n{"rising":[{"topic":"<specific trend>","hook_style":"<hook format>","why_now":"<reason>","growth":"Rising","signal_strength":<0.0-1.0>},{"topic":"<specific trend>","hook_style":"<hook format>","why_now":"<reason>","growth":"Accelerating","signal_strength":<0.0-1.0>},{"topic":"<specific trend>","hook_style":"<hook format>","why_now":"<reason>","growth":"Early signal","signal_strength":<0.0-1.0>}],"saturated":[{"pattern":"<overused pattern>","why_avoid":"<reason>"},{"pattern":"<overused pattern>","why_avoid":"<reason>"}],"niche":"${niche || 'General'}","cache_status":"fresh","quality":{"level":"full"}}`
  );
  return { success: true, data };
}

async function analyzeAccount({ handle, platform = 'tiktok' }, key) {
  const data = await claude(key,
    'You are a social media strategist specializing in viral content. Respond with valid JSON only, no markdown fences.',
    `Analyze the ${platform} creator @${handle}. Use your knowledge of this creator if known, or apply creator archetype analysis.\n\nReturn ONLY this JSON:\n{"handle":"${handle}","platform":"${platform}","viral_dna":{"viral_dna_score":<0-100>,"viral_dna_signals":["<signal>","<signal>","<signal>"],"replicability_score":<0-100>,"replicability_signals":["<signal>","<signal>"],"originality_score":<0-100>,"consistency_score":<0-100>,"hook_formula":"<their typical hook pattern>","content_pillars":["<pillar>","<pillar>","<pillar>"]},"top_videos":[{"description":"<concept>","views":<estimated>,"why_it_worked":"<reason>"},{"description":"<concept>","views":<estimated>,"why_it_worked":"<reason>"}],"content_gaps":["<opportunity>","<opportunity>","<opportunity>"],"steal_map":["<replicable tactic>","<replicable tactic>","<replicable tactic>"],"quality":{"level":"full"}}`
  );
  return { success: true, data };
}

async function matchVoice({ reference_samples, samples, draft }, key) {
  const refs = reference_samples || samples || [];
  const sampleText = Array.isArray(refs) ? refs.filter(Boolean).join('\n\n---\n\n') : String(refs);
  const data = await claude(key,
    'You are a writing coach who matches creator voice and style. Respond with valid JSON only, no markdown fences.',
    `Analyze these reference samples and rewrite the draft in the same voice.\n\nSAMPLES:\n${sampleText}\n\nDRAFT:\n${draft}\n\nReturn ONLY this JSON:\n{"voice_analysis":{"tone":"<descriptor>","sentence_length":"<short|medium|long|mixed>","key_phrases":["<phrase>","<phrase>","<phrase>"],"energy":"<descriptor>","hook_style":"<how they open>","cta_style":"<how they close>"},"rewritten_draft":"<draft rewritten in reference voice>","changes_made":["<change>","<change>","<change>"],"quality":{"level":"full"}}`
  );
  return { success: true, data };
}

async function viralRemix({ topic, niche, platform = 'tiktok' }, key) {
  const data = await claude(key,
    'You are a viral content creator. Generate scroll-stopping short-form video scripts. Respond with valid JSON only, no markdown fences.',
    `Create a viral ${platform} script about "${topic}"${niche ? ` in the ${niche} niche` : ''}.\n\nReturn ONLY this JSON:\n{"hook":"<opening line — first 3 seconds>","script":"<full script with scene beats, 60-90 seconds>","cta":"<closing call to action>","hashtags":["<tag>","<tag>","<tag>","<tag>","<tag>"],"estimated_score":<0-100>,"why_it_works":"<brief explanation>","quality":{"level":"full"}}`
  );
  return { success: true, data };
}
