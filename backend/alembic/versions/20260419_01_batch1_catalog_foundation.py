"""Batch 1 catalog + prediction mapping foundation.

Notes:
- The current repo still initializes databases with Base.metadata.create_all().
- If you already have an Alembic head revision in your local repo, replace
  down_revision=None with that revision id before applying.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260419_01_batch1"
down_revision = "627bccfabb5f"
branch_labels = None
depends_on = None


VALID_PREDICTION_STATUSES = (
    "pending",
    "completed",
    "failed",
    "confirmed",
    "corrected",
    "rejected",
)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "classifier_labels",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "label_set_name",
            sa.String(length=100),
            nullable=False,
            server_default="food101",
        ),
        sa.Column("raw_label", sa.String(length=255), nullable=False),
        sa.Column("normalized_label", sa.String(length=255), nullable=False),
        sa.Column("display_label", sa.String(length=255), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_classifier_labels")),
    )
    op.create_index(
        op.f("ix_classifier_labels_normalized_label"),
        "classifier_labels",
        ["normalized_label"],
        unique=False,
    )

    op.create_table(
        "food_aliases",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("food_item_id", sa.String(length=36), nullable=False),
        sa.Column("alias_text", sa.String(length=255), nullable=False),
        sa.Column("normalized_alias", sa.String(length=255), nullable=False),
        sa.Column(
            "alias_type",
            sa.String(length=30),
            nullable=False,
            server_default="synonym",
        ),
        sa.Column(
            "language_code",
            sa.String(length=10),
            nullable=True,
            server_default="en",
        ),
        sa.Column(
            "confidence_score",
            sa.Float(),
            nullable=False,
            server_default="1",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["food_item_id"],
            ["food_items.id"],
            ondelete="CASCADE",
            name=op.f("fk_food_aliases_food_item_id_food_items"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_food_aliases")),
    )
    op.create_index(
        op.f("ix_food_aliases_food_item_id"),
        "food_aliases",
        ["food_item_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_food_aliases_normalized_alias"),
        "food_aliases",
        ["normalized_alias"],
        unique=False,
    )

    op.create_table(
        "classifier_label_food_maps",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("classifier_label_id", sa.String(length=36), nullable=False),
        sa.Column("food_item_id", sa.String(length=36), nullable=False),
        sa.Column(
            "map_type",
            sa.String(length=30),
            nullable=False,
            server_default="exact",
        ),
        sa.Column("ranking", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "match_confidence",
            sa.Float(),
            nullable=False,
            server_default="1",
        ),
        sa.Column(
            "requires_user_confirmation",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["classifier_label_id"],
            ["classifier_labels.id"],
            ondelete="CASCADE",
            name=op.f(
                "fk_classifier_label_food_maps_classifier_label_id_classifier_labels"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["food_item_id"],
            ["food_items.id"],
            ondelete="CASCADE",
            name=op.f("fk_classifier_label_food_maps_food_item_id_food_items"),
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_classifier_label_food_maps"),
        ),
    )
    op.create_index(
        op.f("ix_classifier_label_food_maps_classifier_label_id"),
        "classifier_label_food_maps",
        ["classifier_label_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_classifier_label_food_maps_food_item_id"),
        "classifier_label_food_maps",
        ["food_item_id"],
        unique=False,
    )

    op.add_column(
        "food_items",
        sa.Column("normalized_name", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "food_items",
        sa.Column("display_name", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "food_items",
        sa.Column("search_name", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "food_items",
        sa.Column("search_tsv", postgresql.TSVECTOR(), nullable=True),
    )
    op.add_column(
        "food_items",
        sa.Column("usage_count", sa.BigInteger(), nullable=False, server_default="0"),
    )
    op.add_column(
        "food_items",
        sa.Column(
            "popularity_score",
            sa.Numeric(10, 4),
            nullable=False,
            server_default="0",
        ),
    )

    op.create_index("ix_food_items_display_name", "food_items", ["display_name"], unique=False)
    op.create_index(
        "ix_food_items_normalized_name",
        "food_items",
        ["normalized_name"],
        unique=False,
    )

    op.execute(
        """
        UPDATE food_items
        SET
            normalized_name = lower(trim(regexp_replace(name, '\\s+', ' ', 'g'))),
            display_name = coalesce(nullif(name, ''), slug),
            search_name = coalesce(nullif(name, ''), slug)
        WHERE normalized_name IS NULL
           OR display_name IS NULL
           OR search_name IS NULL
        """
    )

    op.alter_column("food_items", "normalized_name", nullable=False)
    op.alter_column("food_items", "display_name", nullable=False)
    op.alter_column("food_items", "search_name", nullable=False)

    op.execute(
        """
        UPDATE food_items
        SET search_tsv = to_tsvector(
            'simple',
            trim(concat_ws(' ', coalesce(display_name, ''), coalesce(normalized_name, ''), coalesce(search_name, '')))
        )
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_food_items_search_tsv() RETURNS trigger AS $$
        BEGIN
            NEW.search_tsv := to_tsvector(
                'simple',
                trim(concat_ws(' ', coalesce(NEW.display_name, ''), coalesce(NEW.normalized_name, ''), coalesce(NEW.search_name, '')))
            );
            RETURN NEW;
        END
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_food_items_search_tsv_update
        BEFORE INSERT OR UPDATE OF display_name, normalized_name, search_name
        ON food_items
        FOR EACH ROW
        EXECUTE FUNCTION update_food_items_search_tsv()
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_food_items_search_tsv ON food_items USING gin (search_tsv)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_food_items_display_name_trgm ON food_items USING gin (display_name gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_food_items_normalized_name_trgm ON food_items USING gin (normalized_name gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_food_aliases_normalized_alias_trgm ON food_aliases USING gin (normalized_alias gin_trgm_ops)"
    )

    op.add_column(
        "nutrition_facts",
        sa.Column("micronutrients_json", sa.JSON(), nullable=True),
    )
    op.add_column(
        "nutrition_facts",
        sa.Column("source_quality", sa.String(length=30), nullable=True),
    )

    op.add_column(
        "food_logs",
        sa.Column(
            "source_type",
            sa.String(length=30),
            nullable=True,
            server_default="manual",
        ),
    )
    op.execute("UPDATE food_logs SET source_type = 'manual' WHERE source_type IS NULL")
    op.alter_column("food_logs", "source_type", nullable=False)

    op.add_column(
        "food_log_items",
        sa.Column("photo_prediction_id", sa.String(length=36), nullable=True),
    )
    op.add_column(
        "food_log_items",
        sa.Column("serving_name", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "food_log_items",
        sa.Column("source_snapshot", sa.JSON(), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_food_log_items_photo_prediction_id_photo_predictions"),
        "food_log_items",
        "photo_predictions",
        ["photo_prediction_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        op.f("ix_food_log_items_photo_prediction_id"),
        "food_log_items",
        ["photo_prediction_id"],
        unique=False,
    )

    op.add_column(
        "photo_predictions",
        sa.Column("selected_classifier_label_id", sa.String(length=36), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_photo_predictions_selected_classifier_label_id_classifier_labels"),
        "photo_predictions",
        "classifier_labels",
        ["selected_classifier_label_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        op.f("ix_photo_predictions_selected_classifier_label_id"),
        "photo_predictions",
        ["selected_classifier_label_id"],
        unique=False,
    )

    op.execute(
        f"""
        UPDATE photo_predictions
        SET prediction_status = 'completed'
        WHERE prediction_status IS NULL
           OR prediction_status NOT IN {VALID_PREDICTION_STATUSES}
        """
    )
    op.create_check_constraint(
        "ck_photo_predictions_prediction_status_valid",
        "photo_predictions",
        "prediction_status IN ('pending', 'completed', 'failed', 'confirmed', 'corrected', 'rejected')",
    )

    op.create_table(
        "photo_prediction_candidates",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("photo_prediction_id", sa.String(length=36), nullable=False),
        sa.Column("candidate_rank", sa.Integer(), nullable=False),
        sa.Column("classifier_label_id", sa.String(length=36), nullable=True),
        sa.Column("food_item_id", sa.String(length=36), nullable=True),
        sa.Column("vision_confidence", sa.Float(), nullable=False),
        sa.Column("mapping_confidence", sa.Float(), nullable=True),
        sa.Column("combined_confidence", sa.Float(), nullable=False),
        sa.Column("explanation_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["classifier_label_id"],
            ["classifier_labels.id"],
            ondelete="SET NULL",
            name=op.f(
                "fk_photo_prediction_candidates_classifier_label_id_classifier_labels"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["food_item_id"],
            ["food_items.id"],
            ondelete="SET NULL",
            name=op.f("fk_photo_prediction_candidates_food_item_id_food_items"),
        ),
        sa.ForeignKeyConstraint(
            ["photo_prediction_id"],
            ["photo_predictions.id"],
            ondelete="CASCADE",
            name=op.f(
                "fk_photo_prediction_candidates_photo_prediction_id_photo_predictions"
            ),
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_photo_prediction_candidates"),
        ),
    )
    op.create_index(
        op.f("ix_photo_prediction_candidates_photo_prediction_id"),
        "photo_prediction_candidates",
        ["photo_prediction_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_photo_prediction_candidates_classifier_label_id"),
        "photo_prediction_candidates",
        ["classifier_label_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_photo_prediction_candidates_food_item_id"),
        "photo_prediction_candidates",
        ["food_item_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_photo_prediction_candidates_food_item_id"),
        table_name="photo_prediction_candidates",
    )
    op.drop_index(
        op.f("ix_photo_prediction_candidates_classifier_label_id"),
        table_name="photo_prediction_candidates",
    )
    op.drop_index(
        op.f("ix_photo_prediction_candidates_photo_prediction_id"),
        table_name="photo_prediction_candidates",
    )
    op.drop_table("photo_prediction_candidates")

    op.drop_constraint(
        "ck_photo_predictions_prediction_status_valid",
        "photo_predictions",
        type_="check",
    )
    op.drop_index(
        op.f("ix_photo_predictions_selected_classifier_label_id"),
        table_name="photo_predictions",
    )
    op.drop_constraint(
        op.f("fk_photo_predictions_selected_classifier_label_id_classifier_labels"),
        "photo_predictions",
        type_="foreignkey",
    )
    op.drop_column("photo_predictions", "selected_classifier_label_id")

    op.drop_index(
        op.f("ix_food_log_items_photo_prediction_id"),
        table_name="food_log_items",
    )
    op.drop_constraint(
        op.f("fk_food_log_items_photo_prediction_id_photo_predictions"),
        "food_log_items",
        type_="foreignkey",
    )
    op.drop_column("food_log_items", "source_snapshot")
    op.drop_column("food_log_items", "serving_name")
    op.drop_column("food_log_items", "photo_prediction_id")

    op.drop_column("food_logs", "source_type")
    op.drop_column("nutrition_facts", "source_quality")
    op.drop_column("nutrition_facts", "micronutrients_json")

    op.execute("DROP TRIGGER IF EXISTS trg_food_items_search_tsv_update ON food_items")
    op.execute("DROP FUNCTION IF EXISTS update_food_items_search_tsv()")
    op.execute("DROP INDEX IF EXISTS ix_food_aliases_normalized_alias_trgm")
    op.execute("DROP INDEX IF EXISTS ix_food_items_normalized_name_trgm")
    op.execute("DROP INDEX IF EXISTS ix_food_items_display_name_trgm")
    op.execute("DROP INDEX IF EXISTS ix_food_items_search_tsv")

    op.drop_index("ix_food_items_normalized_name", table_name="food_items")
    op.drop_index("ix_food_items_display_name", table_name="food_items")
    op.drop_column("food_items", "popularity_score")
    op.drop_column("food_items", "usage_count")
    op.drop_column("food_items", "search_tsv")
    op.drop_column("food_items", "search_name")
    op.drop_column("food_items", "display_name")
    op.drop_column("food_items", "normalized_name")

    op.drop_index(
        op.f("ix_classifier_label_food_maps_food_item_id"),
        table_name="classifier_label_food_maps",
    )
    op.drop_index(
        op.f("ix_classifier_label_food_maps_classifier_label_id"),
        table_name="classifier_label_food_maps",
    )
    op.drop_table("classifier_label_food_maps")

    op.drop_index(op.f("ix_food_aliases_normalized_alias"), table_name="food_aliases")
    op.drop_index(op.f("ix_food_aliases_food_item_id"), table_name="food_aliases")
    op.drop_table("food_aliases")

    op.drop_index(
        op.f("ix_classifier_labels_normalized_label"),
        table_name="classifier_labels",
    )
    op.drop_table("classifier_labels")