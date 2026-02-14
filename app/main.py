from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.models import MenuAnalysisInput, MenuAnalysisResponse, RecipeInput
from app.services import calculate_recipe_carbon, find_substitutions, generate_optimization_variants

app = FastAPI(title="Recipe Carbon Intelligence Platform", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def home() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/calculate")
def api_calculate(recipe: RecipeInput):
    return calculate_recipe_carbon(recipe)


@app.get("/api/substitutions/{ingredient}")
def api_substitutions(ingredient: str, target_reduction: float = 0.2):
    return {
        "ingredient": ingredient,
        "target_reduction": target_reduction,
        "candidates": find_substitutions(ingredient, target_reduction=target_reduction),
    }


@app.post("/api/optimize")
def api_optimize(recipe: RecipeInput):
    return {
        "recipe_title": recipe.title,
        "variants": generate_optimization_variants(recipe),
    }


@app.post("/api/menu", response_model=MenuAnalysisResponse)
def api_menu_dashboard(payload: MenuAnalysisInput):
    dish_results = [calculate_recipe_carbon(recipe) for recipe in payload.recipes]
    total = sum(item.total_carbon_kg for item in dish_results)
    avg = total / len(dish_results) if dish_results else 0.0
    hotspots = sorted(
        [
            {
                "dish": d.recipe_title,
                "total_carbon_kg": d.total_carbon_kg,
                "intensity": d.carbon_intensity,
            }
            for d in dish_results
        ],
        key=lambda x: x["total_carbon_kg"],
        reverse=True,
    )[:10]

    optimization_candidates = sum(1 for dish in hotspots if dish["intensity"] != "Low")
    potential = round((optimization_candidates / len(dish_results)) * 35, 2) if dish_results else 0.0

    return MenuAnalysisResponse(
        restaurant_name=payload.restaurant_name,
        total_menu_carbon_kg=round(total, 4),
        average_carbon_per_dish_kg=round(avg, 4),
        top_hotspots=hotspots,
        optimization_potential_percent=potential,
    )


@app.post("/api/reports/compliance")
def api_report(payload: MenuAnalysisInput):
    menu_analysis = api_menu_dashboard(payload)
    return {
        "title": f"Compliance report for {payload.restaurant_name}",
        "methodology": [
            "Ingredient carbon = quantity_kg × carbon coefficient.",
            "Cooking carbon = time_hours × method emission rate.",
            "Totals are normalized to kg CO2e and per serving values.",
        ],
        "menu_summary": menu_analysis,
        "disclosure_note": "Formatted for EU Eco-label and Carbon Trust style submissions.",
    }
