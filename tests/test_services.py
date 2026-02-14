from app.models import IngredientInput, RecipeInput
from app.services import calculate_recipe_carbon, find_substitutions, normalize_ingredient_name


def test_recipe_carbon_calculation_has_breakdown():
    recipe = RecipeInput(
        title="Test Bolognese",
        servings=4,
        cooking_method="gas stove",
        cooking_time_minutes=40,
        ingredients=[
            IngredientInput(name="beef mince", quantity=500, unit="g"),
            IngredientInput(name="tomato", quantity=400, unit="g"),
        ],
    )

    result = calculate_recipe_carbon(recipe)

    assert result.total_carbon_kg > 10
    assert result.breakdown[0].normalized_ingredient in {"ground beef", "beef"}


def test_find_substitutions_for_beef_returns_low_carbon_options():
    suggestions = find_substitutions("beef", target_reduction=0.4)
    assert suggestions
    assert all(item["reduction_percent"] >= 40 for item in suggestions[:3])


def test_normalize_aliases():
    assert normalize_ingredient_name("beef mince") == "ground beef"
