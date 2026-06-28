const HOOKLAYER_URL = 'https://hooklayer.dev/api/mcp';

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { tool, params = {}, key } = req.body || {};
  const apiKey = process.env.HOOKLAYER_API_KEY || key || '';

  if (!apiKey) {
    return res.status(401).json({
      error: 'HOOKLAYER_API_KEY not configured',
      hint: 'Set HOOKLAYER_API_KEY in your environment or enter your key in app Settings.',
    });
  }

  if (!tool) return res.status(400).json({ error: 'Missing tool name' });

  try {
    const upstream = await fetch(HOOKLAYER_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: Date.now(),
        method: 'tools/call',
        params: { name: tool, arguments: params },
      }),
    });

    if (!upstream.ok) {
      const txt = await upstream.text().catch(() => '');
      return res.status(upstream.status).json({
        error: `Hooklayer returned ${upstream.status}`,
        detail: txt.substring(0, 200),
      });
    }

    const json = await upstream.json();

    if (json.error) {
      return res.status(400).json({ error: json.error.message || 'Hooklayer API error' });
    }

    // MCP wraps result in result.content[0].text as a JSON string
    let data = json.result;
    if (data?.content?.[0]?.text) {
      try { data = JSON.parse(data.content[0].text); } catch { /* keep as-is */ }
    }

    return res.status(200).json({ success: true, data });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
};
