from __future__ import annotations

from difflib import SequenceMatcher

from app.carbon_data import (
    CARBON_INTENSITY_BANDS,
    COOKING_METHOD_CARBON_COEFFICIENTS,
    DEFAULT_COOKING_METHOD_CARBON,
    DEFAULT_INGREDIENT_CARBON,
    FLAVOR_PROFILES,
    INGREDIENT_ALIASES,
    INGREDIENT_CARBON_COEFFICIENTS,
)
from app.models import (
    OptimizationVariant,
    RecipeCarbonResponse,
    RecipeInput,
    SubstitutionSuggestion,
)

UNIT_CONVERSIONS_TO_KG = {
    "kg": 1.0,
    "g": 0.001,
    "mg": 0.000001,
    "lb": 0.453592,
    "oz": 0.0283495,
    "cup": 0.24,
    "cups": 0.24,
    "tbsp": 0.015,
    "tsp": 0.005,
    "ml": 0.001,
    "l": 1.0,
}

CATEGORY_DEFAULTS = {
    "vegetable": 0.4,
    "fruit": 0.7,
    "grain": 1.6,
    "legume": 0.9,
}


def convert_to_kg(quantity: float, unit: str) -> float:
    factor = UNIT_CONVERSIONS_TO_KG.get(unit.strip().lower())
    if factor is None:
        return quantity * 0.001
    return quantity * factor


def normalize_ingredient_name(name: str) -> str:
    candidate = name.strip().lower()
    if candidate in INGREDIENT_ALIASES:
        return INGREDIENT_ALIASES[candidate]
    if candidate in INGREDIENT_CARBON_COEFFICIENTS:
        return candidate

    matches = sorted(
        INGREDIENT_CARBON_COEFFICIENTS.keys(),
        key=lambda k: SequenceMatcher(None, candidate, k).ratio(),
        reverse=True,
    )
    best = matches[0] if matches else candidate
    if SequenceMatcher(None, candidate, best).ratio() >= 0.72:
        return best
    return candidate


def get_ingredient_carbon_coefficient(name: str) -> float:
    normalized = normalize_ingredient_name(name)
    if normalized in INGREDIENT_CARBON_COEFFICIENTS:
        return INGREDIENT_CARBON_COEFFICIENTS[normalized]

    fallback_rules = {
        "bean": CATEGORY_DEFAULTS["legume"],
        "lentil": CATEGORY_DEFAULTS["legume"],
        "pea": CATEGORY_DEFAULTS["legume"],
        "tomato": CATEGORY_DEFAULTS["vegetable"],
        "pepper": CATEGORY_DEFAULTS["vegetable"],
        "apple": CATEGORY_DEFAULTS["fruit"],
        "berry": CATEGORY_DEFAULTS["fruit"],
        "wheat": CATEGORY_DEFAULTS["grain"],
        "oat": CATEGORY_DEFAULTS["grain"],
    }
    for token, value in fallback_rules.items():
        if token in normalized:
            return value

    return DEFAULT_INGREDIENT_CARBON


def jaccard_similarity(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def calculate_recipe_carbon(recipe: RecipeInput) -> RecipeCarbonResponse:
    breakdown: list[dict] = []
    ingredient_carbon_total = 0.0

    for ingredient in recipe.ingredients:
        normalized = normalize_ingredient_name(ingredient.name)
        quantity_kg = convert_to_kg(ingredient.quantity, ingredient.unit)
        carbon_coef = get_ingredient_carbon_coefficient(normalized)
        carbon_kg = quantity_kg * carbon_coef
        ingredient_carbon_total += carbon_kg
        breakdown.append(
            {
                "ingredient": ingredient.name,
                "normalized_ingredient": normalized,
                "quantity_kg": round(quantity_kg, 4),
                "carbon_kg": round(carbon_kg, 4),
            }
        )

    cooking_rate = COOKING_METHOD_CARBON_COEFFICIENTS.get(
        recipe.cooking_method.lower(), DEFAULT_COOKING_METHOD_CARBON
    )
    cooking_carbon = (recipe.cooking_time_minutes / 60.0) * cooking_rate
    total = ingredient_carbon_total + cooking_carbon

    for row in breakdown:
        row["percentage"] = round(((row["carbon_kg"] / total) * 100) if total else 0, 2)

    breakdown = sorted(breakdown, key=lambda item: item["carbon_kg"], reverse=True)

    intensity = "High"
    per_serving = total / recipe.servings
    for band in CARBON_INTENSITY_BANDS:
        if band.min_value <= per_serving < band.max_value:
            intensity = band.label
            break

    return RecipeCarbonResponse(
        recipe_title=recipe.title,
        total_carbon_kg=round(total, 4),
        carbon_per_serving_kg=round(per_serving, 4),
        ingredient_carbon_kg=round(ingredient_carbon_total, 4),
        cooking_carbon_kg=round(cooking_carbon, 4),
        carbon_intensity=intensity,
        breakdown=breakdown,
    )


def find_substitutions(ingredient_name: str, target_reduction: float = 0.2) -> list[dict]:
    normalized = normalize_ingredient_name(ingredient_name)
    original_carbon = get_ingredient_carbon_coefficient(normalized)
    original_flavors = FLAVOR_PROFILES.get(normalized, set())
    target_max = original_carbon * (1 - target_reduction)

    results = []
    for candidate, candidate_carbon in INGREDIENT_CARBON_COEFFICIENTS.items():
        if candidate == normalized or candidate_carbon > target_max:
            continue
        similarity = jaccard_similarity(original_flavors, FLAVOR_PROFILES.get(candidate, set()))
        reduction_pct = ((original_carbon - candidate_carbon) / original_carbon) * 100 if original_carbon else 0
        score = (similarity * 0.6) + ((reduction_pct / 100) * 0.4)
        results.append(
            {
                "ingredient": candidate,
                "carbon": round(candidate_carbon, 3),
                "reduction_percent": round(reduction_pct, 2),
                "flavor_similarity": round(similarity * 100, 2),
                "score": round(score, 4),
            }
        )

    return sorted(results, key=lambda x: x["score"], reverse=True)[:10]


def generate_optimization_variants(recipe: RecipeInput) -> list[OptimizationVariant]:
    baseline = calculate_recipe_carbon(recipe)
    targets = [20.0, 40.0, 60.0]
    variants: list[OptimizationVariant] = []

    for target in targets:
        new_recipe = recipe.model_copy(deep=True)
        substitutions: list[SubstitutionSuggestion] = []

        for ingredient in new_recipe.ingredients:
            options = find_substitutions(ingredient.name, target_reduction=target / 100)
            if options and get_ingredient_carbon_coefficient(ingredient.name) > 3.0:
                best = options[0]
                substitutions.append(
                    SubstitutionSuggestion(
                        original_ingredient=ingredient.name,
                        substitute_ingredient=best["ingredient"],
                        carbon_reduction_percent=best["reduction_percent"],
                        flavor_similarity_score=best["flavor_similarity"],
                    )
                )
                ingredient.name = best["ingredient"]

        if new_recipe.cooking_method.lower().startswith("gas"):
            new_recipe.cooking_method = new_recipe.cooking_method.lower().replace("gas", "electric")

        optimized = calculate_recipe_carbon(new_recipe)
        achieved = (
            ((baseline.total_carbon_kg - optimized.total_carbon_kg) / baseline.total_carbon_kg) * 100
            if baseline.total_carbon_kg
            else 0
        )
        variants.append(
            OptimizationVariant(
                variant_label=(
                    "Conservative -20%" if target == 20 else "Moderate -40%" if target == 40 else "Aggressive -60%"
                ),
                target_reduction_percent=target,
                original_carbon_kg=baseline.total_carbon_kg,
                optimized_carbon_kg=optimized.total_carbon_kg,
                achieved_reduction_percent=round(achieved, 2),
                substitutions=substitutions,
            )
        )

    return variants
