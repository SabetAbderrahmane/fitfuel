"""Batch 2 source provenance and ingestion scaffolding."""

from alembic import op
import sqlalchemy as sa


revision = "20260420_batch2_sources_seed"
down_revision = "20260419_01_batch1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "data_sources",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("source_code", sa.String(length=50), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("license_name", sa.String(length=255), nullable=True),
        sa.Column("homepage_url", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_data_sources")),
        sa.UniqueConstraint("source_code", name=op.f("uq_data_sources_source_code")),
    )
    op.create_index(op.f("ix_data_sources_source_code"), "data_sources", ["source_code"], unique=False)

    op.create_table(
        "ingestion_releases",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("data_source_id", sa.String(length=36), nullable=False),
        sa.Column("source_version", sa.String(length=100), nullable=False),
        sa.Column("release_date", sa.Date(), nullable=True),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="draft"),
        sa.Column("raw_record_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("normalized_record_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["data_source_id"],
            ["data_sources.id"],
            ondelete="CASCADE",
            name=op.f("fk_ingestion_releases_data_source_id_data_sources"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ingestion_releases")),
        sa.UniqueConstraint(
            "data_source_id",
            "source_version",
            name=op.f("uq_ingestion_releases_data_source_id"),
        ),
    )
    op.create_index(
        op.f("ix_ingestion_releases_data_source_id"),
        "ingestion_releases",
        ["data_source_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ingestion_releases_published_at"),
        "ingestion_releases",
        ["published_at"],
        unique=False,
    )

    op.create_table(
        "source_food_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("ingestion_release_id", sa.String(length=36), nullable=False),
        sa.Column("source_record_key", sa.String(length=100), nullable=False),
        sa.Column("source_food_name", sa.String(length=255), nullable=False),
        sa.Column("brand_name", sa.String(length=255), nullable=True),
        sa.Column("payload_json", sa.JSON(), nullable=True),
        sa.Column("normalized_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["ingestion_release_id"],
            ["ingestion_releases.id"],
            ondelete="CASCADE",
            name=op.f("fk_source_food_records_ingestion_release_id_ingestion_releases"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_source_food_records")),
        sa.UniqueConstraint(
            "ingestion_release_id",
            "source_record_key",
            name=op.f("uq_source_food_records_ingestion_release_id"),
        ),
    )
    op.create_index(
        op.f("ix_source_food_records_ingestion_release_id"),
        "source_food_records",
        ["ingestion_release_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_source_food_records_normalized_hash"),
        "source_food_records",
        ["normalized_hash"],
        unique=False,
    )

    op.create_table(
        "source_nutrient_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("source_food_record_id", sa.String(length=36), nullable=False),
        sa.Column("nutrient_code", sa.String(length=50), nullable=True),
        sa.Column("nutrient_name", sa.String(length=255), nullable=True),
        sa.Column("amount", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(length=30), nullable=True),
        sa.Column("payload_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["source_food_record_id"],
            ["source_food_records.id"],
            ondelete="CASCADE",
            name=op.f("fk_source_nutrient_records_source_food_record_id_source_food_records"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_source_nutrient_records")),
    )
    op.create_index(
        op.f("ix_source_nutrient_records_source_food_record_id"),
        "source_nutrient_records",
        ["source_food_record_id"],
        unique=False,
    )

    op.create_table(
        "food_source_links",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("food_item_id", sa.String(length=36), nullable=False),
        sa.Column("data_source_id", sa.String(length=36), nullable=False),
        sa.Column("ingestion_release_id", sa.String(length=36), nullable=False),
        sa.Column("source_record_key", sa.String(length=100), nullable=False),
        sa.Column("source_priority", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["food_item_id"],
            ["food_items.id"],
            ondelete="CASCADE",
            name=op.f("fk_food_source_links_food_item_id_food_items"),
        ),
        sa.ForeignKeyConstraint(
            ["data_source_id"],
            ["data_sources.id"],
            ondelete="CASCADE",
            name=op.f("fk_food_source_links_data_source_id_data_sources"),
        ),
        sa.ForeignKeyConstraint(
            ["ingestion_release_id"],
            ["ingestion_releases.id"],
            ondelete="CASCADE",
            name=op.f("fk_food_source_links_ingestion_release_id_ingestion_releases"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_food_source_links")),
        sa.UniqueConstraint(
            "food_item_id",
            "data_source_id",
            "ingestion_release_id",
            "source_record_key",
            name=op.f("uq_food_source_links_food_item_id"),
        ),
    )
    op.create_index(
        op.f("ix_food_source_links_food_item_id"),
        "food_source_links",
        ["food_item_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_food_source_links_data_source_id"),
        "food_source_links",
        ["data_source_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_food_source_links_ingestion_release_id"),
        "food_source_links",
        ["ingestion_release_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_food_source_links_ingestion_release_id"), table_name="food_source_links")
    op.drop_index(op.f("ix_food_source_links_data_source_id"), table_name="food_source_links")
    op.drop_index(op.f("ix_food_source_links_food_item_id"), table_name="food_source_links")
    op.drop_table("food_source_links")

    op.drop_index(
        op.f("ix_source_nutrient_records_source_food_record_id"),
        table_name="source_nutrient_records",
    )
    op.drop_table("source_nutrient_records")

    op.drop_index(op.f("ix_source_food_records_normalized_hash"), table_name="source_food_records")
    op.drop_index(
        op.f("ix_source_food_records_ingestion_release_id"),
        table_name="source_food_records",
    )
    op.drop_table("source_food_records")

    op.drop_index(op.f("ix_ingestion_releases_published_at"), table_name="ingestion_releases")
    op.drop_index(
        op.f("ix_ingestion_releases_data_source_id"),
        table_name="ingestion_releases",
    )
    op.drop_table("ingestion_releases")

    op.drop_index(op.f("ix_data_sources_source_code"), table_name="data_sources")
    op.drop_table("data_sources")