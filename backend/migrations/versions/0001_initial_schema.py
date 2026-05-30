"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-30

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # import_runs — must exist before reddit_records (FK target)
    # ------------------------------------------------------------------
    op.create_table(
        "import_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_format", sa.String(16), nullable=False),
        sa.Column("total_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("imported_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("skipped_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("error_detail", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_import_runs_id", "import_runs", ["id"])
    op.create_index("ix_import_runs_status", "import_runs", ["status"])
    op.create_index("ix_import_runs_created_at", "import_runs", ["created_at"])

    # ------------------------------------------------------------------
    # taxonomies — must exist before record_tags (FK target)
    # ------------------------------------------------------------------
    op.create_table(
        "taxonomies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("term", sa.String(128), nullable=False),
        sa.Column("aliases", JSONB(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("category", "term", name="uq_taxonomy_category_term"),
    )
    op.create_index("ix_taxonomies_id", "taxonomies", ["id"])
    op.create_index("ix_taxonomies_category", "taxonomies", ["category"])
    op.create_index("ix_taxonomies_is_active", "taxonomies", ["is_active"])

    # ------------------------------------------------------------------
    # reddit_records — core table
    # ------------------------------------------------------------------
    op.create_table(
        "reddit_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "import_run_id",
            sa.Integer(),
            sa.ForeignKey("import_runs.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("source_id", sa.String(128), nullable=False),
        sa.Column("source_type", sa.String(32), nullable=False),
        sa.Column("subreddit", sa.String(128), nullable=True),
        sa.Column("author", sa.String(128), nullable=True),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("created_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reddit_score", sa.Integer(), nullable=True),
        sa.Column("num_comments", sa.Integer(), nullable=True),
        sa.Column(
            "imported_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # Denormalized tags (JSONB arrays for fast containment queries)
        sa.Column("industries", JSONB(), nullable=True),
        sa.Column("buyer_roles", JSONB(), nullable=True),
        sa.Column("pain_points", JSONB(), nullable=True),
        sa.Column("competitors", JSONB(), nullable=True),
        sa.Column("intent_stage", sa.String(64), nullable=True),
        # Denormalized scores (floats for range queries without joins)
        sa.Column("icp_fit_score", sa.Float(), nullable=True),
        sa.Column("pain_severity_score", sa.Float(), nullable=True),
        sa.Column("purchase_intent_score", sa.Float(), nullable=True),
        sa.Column("abm_priority_score", sa.Float(), nullable=True),
        sa.Column("score_reasons", JSONB(), nullable=True),
    )
    op.create_index("ix_reddit_records_id", "reddit_records", ["id"])
    op.create_index(
        "ix_reddit_records_source_id", "reddit_records", ["source_id"], unique=True
    )
    op.create_index("ix_reddit_records_import_run_id", "reddit_records", ["import_run_id"])
    op.create_index("ix_reddit_records_subreddit", "reddit_records", ["subreddit"])
    op.create_index("ix_reddit_records_intent_stage", "reddit_records", ["intent_stage"])
    op.create_index("ix_reddit_records_icp_fit_score", "reddit_records", ["icp_fit_score"])
    op.create_index(
        "ix_reddit_records_purchase_intent_score",
        "reddit_records",
        ["purchase_intent_score"],
    )
    op.create_index(
        "ix_reddit_records_abm_priority_score", "reddit_records", ["abm_priority_score"]
    )
    # Composite: the most common dashboard filter pair
    op.create_index(
        "ix_records_intent_abm",
        "reddit_records",
        ["intent_stage", "abm_priority_score"],
    )
    op.create_index("ix_records_imported_at", "reddit_records", ["imported_at"])

    # ------------------------------------------------------------------
    # record_tags — join table (depends on reddit_records + taxonomies)
    # ------------------------------------------------------------------
    op.create_table(
        "record_tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "record_id",
            sa.Integer(),
            sa.ForeignKey("reddit_records.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "taxonomy_id",
            sa.Integer(),
            sa.ForeignKey("taxonomies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("matched_text", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("record_id", "taxonomy_id", name="uq_record_tag"),
    )
    op.create_index("ix_record_tags_id", "record_tags", ["id"])
    op.create_index("ix_record_tags_record_id", "record_tags", ["record_id"])
    op.create_index("ix_record_tags_taxonomy_id", "record_tags", ["taxonomy_id"])

    # ------------------------------------------------------------------
    # scores — 1-to-1 with reddit_records (depends on reddit_records)
    # ------------------------------------------------------------------
    op.create_table(
        "scores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "record_id",
            sa.Integer(),
            sa.ForeignKey("reddit_records.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("icp_fit_score", sa.Float(), nullable=True),
        sa.Column("pain_severity_score", sa.Float(), nullable=True),
        sa.Column("purchase_intent_score", sa.Float(), nullable=True),
        sa.Column("abm_priority_score", sa.Float(), nullable=True),
        sa.Column("icp_fit_reasons", JSONB(), nullable=True),
        sa.Column("pain_severity_reasons", JSONB(), nullable=True),
        sa.Column("purchase_intent_reasons", JSONB(), nullable=True),
        sa.Column("abm_priority_reasons", JSONB(), nullable=True),
        sa.Column(
            "score_version", sa.String(32), nullable=False, server_default="v1"
        ),
        sa.Column(
            "scored_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_scores_id", "scores", ["id"])
    op.create_index("ix_scores_record_id", "scores", ["record_id"], unique=True)
    op.create_index("ix_scores_score_version", "scores", ["score_version"])
    op.create_index("ix_scores_scored_at", "scores", ["scored_at"])

    # ------------------------------------------------------------------
    # search_runs — standalone audit log
    # ------------------------------------------------------------------
    op.create_table(
        "search_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filters", JSONB(), nullable=False),
        sa.Column("result_count", sa.Integer(), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_search_runs_id", "search_runs", ["id"])
    op.create_index("ix_search_runs_created_at", "search_runs", ["created_at"])

    # ------------------------------------------------------------------
    # export_logs — standalone audit log
    # ------------------------------------------------------------------
    op.create_table(
        "export_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filters", JSONB(), nullable=False),
        sa.Column("row_count", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_export_logs_id", "export_logs", ["id"])
    op.create_index("ix_export_logs_created_at", "export_logs", ["created_at"])


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table("export_logs")
    op.drop_table("search_runs")
    op.drop_table("scores")
    op.drop_table("record_tags")
    op.drop_table("reddit_records")
    op.drop_table("taxonomies")
    op.drop_table("import_runs")
