"""
Run with:  python seed.py
From:      backend/
"""

from app.database import SessionLocal
from app.models.taxonomy import Taxonomy
from app.seeds.taxonomy_seed import TAXONOMY


def seed_taxonomies() -> None:
    db = SessionLocal()
    created = skipped = 0
    try:
        for category, terms in TAXONOMY.items():
            for entry in terms:
                exists = (
                    db.query(Taxonomy)
                    .filter_by(category=category, term=entry["term"])
                    .first()
                )
                if exists:
                    skipped += 1
                    continue
                db.add(
                    Taxonomy(
                        category=category,
                        term=entry["term"],
                        aliases=entry.get("aliases", []),
                    )
                )
                created += 1
        db.commit()
        print(f"Seed complete: {created} terms created, {skipped} already existed.")
    except Exception as exc:
        db.rollback()
        print(f"Seed failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_taxonomies()
