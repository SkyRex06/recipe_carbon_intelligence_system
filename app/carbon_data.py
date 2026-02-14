from __future__ import annotations

from dataclasses import dataclass

DEFAULT_INGREDIENT_CARBON = 2.0
DEFAULT_COOKING_METHOD_CARBON = 0.5

# kg CO2e per kg ingredient
INGREDIENT_CARBON_COEFFICIENTS: dict[str, float] = {
    "beef": 27.0,
    "ground beef": 27.0,
    "lamb": 24.0,
    "cheese": 13.5,
    "parmesan": 13.5,
    "dark chocolate": 19.0,
    "butter": 11.5,
    "cream": 10.5,
    "milk": 3.2,
    "chicken": 6.9,
    "chicken breast": 6.9,
    "pork": 7.6,
    "bacon": 8.9,
    "farmed fish": 5.1,
    "salmon": 5.1,
    "eggs": 4.8,
    "egg": 4.8,
    "rice": 4.0,
    "shrimp": 11.8,
    "tofu": 2.0,
    "tempeh": 2.4,
    "mushroom": 1.1,
    "mushrooms": 1.1,
    "lentils": 0.9,
    "beans": 0.9,
    "chickpeas": 0.9,
    "peas": 0.8,
    "potato": 0.4,
    "tomato": 0.5,
    "onion": 0.4,
    "garlic": 0.5,
    "carrot": 0.4,
    "broccoli": 0.5,
    "spinach": 0.4,
    "zucchini": 0.4,
    "pepper": 0.5,
    "cabbage": 0.4,
    "cauliflower": 0.5,
    "flour": 1.6,
    "wheat": 1.6,
    "oats": 1.6,
    "bread": 1.7,
    "pasta": 1.8,
    "quinoa": 1.7,
    "corn": 1.1,
    "apple": 0.6,
    "banana": 0.7,
    "berries": 0.8,
    "orange": 0.6,
    "avocado": 2.4,
    "almonds": 2.3,
    "walnuts": 2.3,
    "cashews": 2.3,
    "olive oil": 3.0,
    "sunflower oil": 2.9,
    "coconut milk": 2.8,
    "oat milk": 1.1,
    "soy milk": 1.0,
    "yogurt": 2.2,
    "nutritional yeast": 1.5,
    "miso": 1.7,
    "sugar": 1.5,
    "honey": 1.8,
    "salt": 0.1,
    "black pepper": 1.9,
    "basil": 0.8,
    "cilantro": 0.8,
    "parsley": 0.8,
    "lemon": 0.7,
    "lime": 0.7,
    "vinegar": 1.0,
}

# kg CO2e per hour
COOKING_METHOD_CARBON_COEFFICIENTS: dict[str, float] = {
    "gas stove": 0.5,
    "electric stove": 0.3,
    "gas oven": 1.2,
    "electric oven": 0.8,
    "slow cooker": 0.15,
    "pressure cooker": 0.2,
    "induction": 0.25,
    "air fryer": 0.4,
}

INGREDIENT_ALIASES: dict[str, str] = {
    "beef mince": "ground beef",
    "minced beef": "ground beef",
    "ground chuck": "ground beef",
    "chicken thighs": "chicken",
    "chicken thigh": "chicken",
    "baby bella mushrooms": "mushrooms",
    "portobello": "mushrooms",
    "parmigiano": "parmesan",
    "double cream": "cream",
    "heavy cream": "cream",
    "scallion": "onion",
}

# Simplified flavor vectors (category tags)
FLAVOR_PROFILES: dict[str, set[str]] = {
    "beef": {"umami", "savory", "fatty", "roasted"},
    "ground beef": {"umami", "savory", "fatty", "roasted"},
    "lamb": {"umami", "savory", "gamey", "fatty"},
    "chicken": {"savory", "mild", "umami"},
    "mushrooms": {"umami", "earthy", "savory"},
    "lentils": {"earthy", "nutty", "savory"},
    "miso": {"umami", "salty", "fermented"},
    "parmesan": {"umami", "salty", "nutty"},
    "nutritional yeast": {"umami", "nutty", "savory"},
    "cream": {"fatty", "smooth", "mild"},
    "oat milk": {"mild", "sweet", "smooth"},
    "coconut milk": {"sweet", "fatty", "smooth"},
    "cashews": {"nutty", "fatty", "mild"},
    "tofu": {"mild", "savory", "protein"},
    "beans": {"earthy", "savory", "protein"},
}


@dataclass(frozen=True)
class CarbonIntensityBand:
    label: str
    min_value: float
    max_value: float


CARBON_INTENSITY_BANDS: tuple[CarbonIntensityBand, ...] = (
    CarbonIntensityBand("Low", 0.0, 2.0),
    CarbonIntensityBand("Medium", 2.0, 8.0),
    CarbonIntensityBand("High", 8.0, 10_000.0),
)
