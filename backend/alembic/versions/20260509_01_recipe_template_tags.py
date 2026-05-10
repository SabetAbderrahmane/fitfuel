"""Add recipe and meal template classification JSON fields."""

from alembic import op
import sqlalchemy as sa


revision = "20260509_01_recipe_template_tags"
down_revision = "20260420_batch2_sources_seed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("recipes", sa.Column("diet_tags_json", sa.JSON(), nullable=True))
    op.add_column("recipes", sa.Column("allergen_flags_json", sa.JSON(), nullable=True))
    op.add_column("meal_templates", sa.Column("diet_tags_json", sa.JSON(), nullable=True))
    op.add_column("meal_templates", sa.Column("allergen_flags_json", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("meal_templates", "allergen_flags_json")
    op.drop_column("meal_templates", "diet_tags_json")
    op.drop_column("recipes", "allergen_flags_json")
    op.drop_column("recipes", "diet_tags_json")
