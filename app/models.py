from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class IngredientInput(BaseModel):
    name: str
    quantity: float = Field(gt=0)
    unit: str


class RecipeInput(BaseModel):
    title: str
    ingredients: list[IngredientInput]
    servings: int = Field(default=1, ge=1)
    cooking_method: str = "gas stove"
    cooking_time_minutes: int = Field(default=30, ge=1)


class CarbonBreakdownItem(BaseModel):
    ingredient: str
    normalized_ingredient: str
    quantity_kg: float
    carbon_kg: float
    percentage: float


class RecipeCarbonResponse(BaseModel):
    recipe_title: str
    total_carbon_kg: float
    carbon_per_serving_kg: float
    ingredient_carbon_kg: float
    cooking_carbon_kg: float
    carbon_intensity: Literal["Low", "Medium", "High"]
    breakdown: list[CarbonBreakdownItem]


class SubstitutionSuggestion(BaseModel):
    original_ingredient: str
    substitute_ingredient: str
    carbon_reduction_percent: float
    flavor_similarity_score: float


class OptimizationVariant(BaseModel):
    variant_label: str
    target_reduction_percent: float
    original_carbon_kg: float
    optimized_carbon_kg: float
    achieved_reduction_percent: float
    substitutions: list[SubstitutionSuggestion]


class MenuAnalysisInput(BaseModel):
    restaurant_name: str
    recipes: list[RecipeInput]


class MenuAnalysisResponse(BaseModel):
    restaurant_name: str
    total_menu_carbon_kg: float
    average_carbon_per_dish_kg: float
    top_hotspots: list[dict]
    optimization_potential_percent: float
