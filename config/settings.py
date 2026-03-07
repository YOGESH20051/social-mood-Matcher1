"""
Configuration settings for Social Mood Matcher application.
Centralized configuration management for models, limits, and UI settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Model Configuration
MODEL_CONFIG = {
    "image_captioning": {
        "model_name": "Salesforce/blip-image-captioning-base",
        "cache_dir": os.getenv("MODEL_CACHE_DIR", "./models_cache"),
        "device": "cpu",  # Change to "cuda" if GPU available
    },
    "sentiment": {
        "model_name": "distilbert-base-uncased-finetuned-sst-2-english",
        "cache_dir": os.getenv("MODEL_CACHE_DIR", "./models_cache"),
    },
    "caption_generation": {
        "model_name": "gpt2",
        "cache_dir": os.getenv("MODEL_CACHE_DIR", "./models_cache"),
        "max_length": 100,
        "temperature": 0.8,
    }
}

# Character Limits
CHARACTER_LIMITS = {
    "twitter": 280,
    "instagram": 2200,
    "facebook": 63206,
    "default": 280,  # Using Twitter as default
}

# Hashtag Configuration
HASHTAG_CONFIG = {
    "max_hashtags": 8,
    "min_hashtags": 3,
    "max_hashtag_length": 30,
}

# Sentiment Categories
SENTIMENT_CATEGORIES = [
    "happy",
    "calm",
    "cozy",
    "aesthetic",
    "adventurous",
    "luxury",
    "energetic",
    "peaceful",
    "romantic",
    "nostalgic",
]

# Caption Styles
CAPTION_STYLES = {
    "casual": {
        "tone": "friendly and relaxed",
        "emoji_usage": "moderate",
        "formality": "low",
    },
    "aesthetic": {
        "tone": "artistic and poetic",
        "emoji_usage": "minimal",
        "formality": "medium",
    },
    "professional": {
        "tone": "polished and informative",
        "emoji_usage": "none",
        "formality": "high",
    },
    "playful": {
        "tone": "fun and energetic",
        "emoji_usage": "high",
        "formality": "low",
    },
}

# UI Configuration
UI_CONFIG = {
    "page_title": "Social Mood Matcher",
    "page_icon": "camera",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "max_upload_size_mb": 10,
    "supported_formats": ["jpg", "jpeg", "png", "webp"],
}

# Image Processing
IMAGE_CONFIG = {
    "max_dimension": 1024,
    "thumbnail_size": (512, 512),
    "quality": 85,
}

# Caching Configuration
CACHE_CONFIG = {
    "enable_model_cache": True,
    "enable_result_cache": True,
    "cache_ttl": 3600,  # 1 hour in seconds
}

# Debug Settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# API Keys
API_KEYS = {
    "gemini": os.getenv("GEMINI_API_KEY"),
    "openai": os.getenv("OPENAI_API_KEY"),
    "huggingface": os.getenv("HUGGINGFACE_API_KEY"),
    "twitter": os.getenv("TWITTER_API_KEY"),
}

# AI Model Selection
AI_MODEL_PREFERENCE = os.getenv("AI_MODEL", "local")  # 'local' or 'gemini'
USE_GEMINI = AI_MODEL_PREFERENCE.lower() == "gemini" and API_KEYS.get("gemini") is not None

# Trending Hashtags Database (2024)
TRENDING_HASHTAGS_2024 = {
    "food": {
        "general": ["#Foodie", "#FoodPhotography", "#InstaFood", "#FoodLover", "#Delicious", 
                   "#FoodGram", "#Yummy", "#FoodBlogger", "#Tasty", "#FoodPorn"],
        "happy": ["#FoodJoy", "#HappyEating", "#FoodVibes", "#GoodFood", "#FoodHappiness"],
        "luxury": ["#FineDining", "#GourmetFood", "#LuxuryDining", "#FoodieLife", "#ChefSpecial"],
        "cozy": ["#ComfortFood", "#CozyMeal", "#HomeCooking", "#WarmFood", "#CozyVibes"],
        "aesthetic": ["#FoodArt", "#BeautifulFood", "#FoodStyling", "#AestheticFood", "#FoodDesign"],
    },
    "travel": {
        "general": ["#Travel", "#Wanderlust", "#TravelPhotography", "#Explore", "#Adventure",
                   "#TravelGram", "#Vacation", "#TravelBlogger", "#Traveling", "#WorldTravel"],
        "adventurous": ["#AdventureTravel", "#ExploreMore", "#TravelAdventure", "#Wanderer", "#AdventureTime"],
        "calm": ["#PeacefulTravel", "#TranquilPlaces", "#RelaxingViews", "#CalmTravel", "#SerenityNow"],
        "luxury": ["#LuxuryTravel", "#TravelInStyle", "#LuxuryVacation", "#LuxeLife", "#TravelGoals"],
        "aesthetic": ["#TravelAesthetic", "#BeautifulDestinations", "#ScenicViews", "#TravelInspiration", "#PicturePerfect"],
    },
    "nature": {
        "general": ["#Nature", "#NaturePhotography", "#NatureLover", "#Outdoors", "#NatureBeauty",
                   "#Landscape", "#NatureGram", "#Wildlife", "#NaturePerfection", "#EarthPix"],
        "peaceful": ["#PeacefulNature", "#Tranquility", "#NatureCalm", "#Serenity", "#QuietMoments"],
        "adventurous": ["#NatureAdventure", "#Hiking", "#OutdoorAdventure", "#ExploreNature", "#WildernessAdventure"],
        "aesthetic": ["#NatureAesthetic", "#NaturalBeauty", "#ScenicNature", "#NatureArt", "#BeautifulNature"],
        "energetic": ["#NatureEnergy", "#ActiveOutdoors", "#NatureVibes", "#OutdoorLife", "#NatureExplorer"],
    },
    "lifestyle": {
        "general": ["#Lifestyle", "#LifestyleBlogger", "#DailyLife", "#LifestylePhotography", "#Living",
                   "#LifestyleGoals", "#MyLife", "#LifestyleInspo", "#Vibes", "#Mood"],
        "happy": ["#HappyLife", "#GoodVibes", "#PositiveVibes", "#JoyfulLiving", "#HappyMoments"],
        "cozy": ["#CozyLife", "#CozyVibes", "#HomeSweetHome", "#CozyLiving", "#ComfortZone"],
        "aesthetic": ["#AestheticLife", "#AestheticVibes", "#MinimalLiving", "#AestheticGoals", "#VisualVibes"],
        "luxury": ["#LuxuryLifestyle", "#LuxeLife", "#LifestyleGoals", "#LivingWell", "#LuxuryLiving"],
    },
    "general": {
        "2024_trending": ["#2024Vibes", "#InstaGood", "#PhotoOfTheDay", "#InstaDaily", "#PicOfTheDay",
                         "#Beautiful", "#Love", "#Instagood", "#Follow", "#Like4Like"],
    }
}

# Fallback Hashtags (if category detection fails)
FALLBACK_HASHTAGS = [
    "#PhotoOfTheDay", "#InstaGood", "#Beautiful", "#Love", "#Instagood",
    "#Photography", "#Art", "#Nature", "#Happy", "#Life"
]
