"""Add meal plan item source metadata."""

from alembic import op
import sqlalchemy as sa


revision = "20260510_01_meal_item_src"
down_revision = "20260509_01_recipe_template_tags"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("meal_plan_items", sa.Column("source_recipe_id", sa.String(length=36), nullable=True))
    op.add_column("meal_plan_items", sa.Column("source_template_id", sa.String(length=36), nullable=True))
    op.add_column("meal_plan_items", sa.Column("source_recipe_name", sa.String(length=255), nullable=True))
    op.add_column("meal_plan_items", sa.Column("source_template_name", sa.String(length=255), nullable=True))
    op.add_column("meal_plan_items", sa.Column("source_generation_type", sa.String(length=50), nullable=True))
    op.create_index("ix_meal_plan_items_source_recipe_id", "meal_plan_items", ["source_recipe_id"])
    op.create_index("ix_meal_plan_items_source_template_id", "meal_plan_items", ["source_template_id"])
    op.create_foreign_key(
        "fk_meal_plan_items_source_recipe_id_recipes",
        "meal_plan_items",
        "recipes",
        ["source_recipe_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_meal_plan_items_source_template_id_meal_templates",
        "meal_plan_items",
        "meal_templates",
        ["source_template_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_meal_plan_items_source_template_id_meal_templates", "meal_plan_items", type_="foreignkey")
    op.drop_constraint("fk_meal_plan_items_source_recipe_id_recipes", "meal_plan_items", type_="foreignkey")
    op.drop_index("ix_meal_plan_items_source_template_id", table_name="meal_plan_items")
    op.drop_index("ix_meal_plan_items_source_recipe_id", table_name="meal_plan_items")
    op.drop_column("meal_plan_items", "source_generation_type")
    op.drop_column("meal_plan_items", "source_template_name")
    op.drop_column("meal_plan_items", "source_recipe_name")
    op.drop_column("meal_plan_items", "source_template_id")
    op.drop_column("meal_plan_items", "source_recipe_id")
