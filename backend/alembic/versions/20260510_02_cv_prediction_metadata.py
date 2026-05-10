"""Add structured CV inference metadata to photo predictions."""

from alembic import op
import sqlalchemy as sa


revision = "20260510_02_cv_pred_meta"
down_revision = "20260510_01_meal_item_src"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "photo_predictions",
        sa.Column("inference_metadata_json", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("photo_predictions", "inference_metadata_json")
