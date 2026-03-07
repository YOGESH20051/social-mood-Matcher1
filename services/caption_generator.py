"""
Caption generation service for Social Mood Matcher.
Generates engaging social media captions based on sentiment and style.
"""

import random
from typing import List, Dict
from config.settings import CAPTION_STYLES


class CaptionGenerator:
    """Generates social media captions with various styles."""
    
    def __init__(self):
        """Initialize caption generator with templates."""
        
        # Caption templates organized by sentiment and style
        self.caption_templates = {
            "happy": {
                "casual": [
                    "Feeling absolutely amazing! ☀️",
                    "This just made my day! 😊",
                    "Can't stop smiling! 💛",
                    "Pure happiness right here!",
                    "Living my best life! ✨",
                    "This is what joy looks like! 🌟",
                ],
                "aesthetic": [
                    "Radiating pure bliss",
                    "Moments of golden happiness",
                    "Where joy meets beauty",
                    "Capturing the essence of delight",
                    "A symphony of cheerful moments",
                ],
                "professional": [
                    "Celebrating life's beautiful moments.",
                    "Finding joy in the simple things.",
                    "A perfect example of happiness.",
                    "Embracing positivity and light.",
                ],
                "playful": [
                    "Happiness overload! 🎉😄",
                    "Smiles for miles! 😁✨",
                    "Too much joy to handle! 💫🌈",
                    "Happy vibes only! 🌟💛",
                ],
            },
            "calm": {
                "casual": [
                    "Finding peace in the moment 🌊",
                    "Just what I needed to relax",
                    "Peaceful vibes all around",
                    "Taking it slow and easy",
                    "Calm and collected ✨",
                ],
                "aesthetic": [
                    "Serenity in its purest form",
                    "Where tranquility resides",
                    "Whispers of peaceful moments",
                    "Embracing the quiet beauty",
                    "A meditation in stillness",
                ],
                "professional": [
                    "Discovering moments of tranquility.",
                    "The art of peaceful living.",
                    "Finding balance and serenity.",
                    "Cultivating inner calm.",
                ],
                "playful": [
                    "Chill mode: activated! 😌✨",
                    "Peace out, stress! ☮️💙",
                    "Zen vibes incoming! 🧘‍♀️",
                ],
            },
            "cozy": {
                "casual": [
                    "Cozy vibes all day long ☕",
                    "This is my happy place 🏡",
                    "Wrapped in comfort and warmth",
                    "Nothing beats this cozy feeling",
                    "Home is where the heart is ❤️",
                ],
                "aesthetic": [
                    "Wrapped in warmth and wonder",
                    "The art of cozy living",
                    "Where comfort meets beauty",
                    "Sanctuary of soft moments",
                    "Embracing the gentle warmth",
                ],
                "professional": [
                    "Creating spaces of comfort and warmth.",
                    "The essence of cozy living.",
                    "Finding comfort in simplicity.",
                ],
                "playful": [
                    "Cozy corner activated! 🛋️☕",
                    "Snuggle season is here! 🧸💕",
                    "Maximum coziness achieved! ✨",
                ],
            },
            "aesthetic": {
                "casual": [
                    "Aesthetic goals right here ✨",
                    "This is so visually pleasing!",
                    "Can't get over how beautiful this is",
                    "Picture perfect moment",
                ],
                "aesthetic": [
                    "A study in visual harmony",
                    "Where art meets everyday life",
                    "Curated moments of beauty",
                    "Aesthetic perfection captured",
                    "The poetry of visual design",
                ],
                "professional": [
                    "Exemplifying visual excellence.",
                    "A masterclass in aesthetic design.",
                    "Where form meets function beautifully.",
                ],
                "playful": [
                    "Aesthetic overload! 🎨✨",
                    "Too pretty to handle! 💫",
                    "Visual candy alert! 🍬",
                ],
            },
            "adventurous": {
                "casual": [
                    "Adventure is calling! 🏔️",
                    "Living for these wild moments",
                    "Exploring and loving it!",
                    "This is what adventure looks like",
                    "Ready for the next journey! ✈️",
                ],
                "aesthetic": [
                    "Where wanderlust meets wonder",
                    "Chronicles of adventure",
                    "Embracing the wild unknown",
                    "Journey into the extraordinary",
                ],
                "professional": [
                    "Embracing the spirit of exploration.",
                    "Adventure awaits those who seek.",
                    "Discovering new horizons.",
                ],
                "playful": [
                    "Adventure mode: ON! 🚀🌍",
                    "Let's get wild! 🏕️⛰️",
                    "Exploring like there's no tomorrow! 🗺️",
                ],
            },
            "luxury": {
                "casual": [
                    "Treating myself right ✨",
                    "Living the luxury life",
                    "This is what dreams are made of",
                    "Indulging in the finer things",
                ],
                "aesthetic": [
                    "Elegance in every detail",
                    "The art of refined living",
                    "Where luxury meets sophistication",
                    "Curated excellence",
                    "Timeless elegance captured",
                ],
                "professional": [
                    "Exemplifying refined taste and quality.",
                    "The epitome of sophisticated living.",
                    "Where excellence is standard.",
                ],
                "playful": [
                    "Fancy vibes only! 💎✨",
                    "Living that luxe life! 🥂",
                    "Treat yourself energy! 👑",
                ],
            },
            "energetic": {
                "casual": [
                    "Energy levels through the roof! ⚡",
                    "Feeling so alive right now!",
                    "Can't contain this energy!",
                    "Vibing on a whole new level",
                ],
                "aesthetic": [
                    "Pulsing with vibrant energy",
                    "Where dynamism meets beauty",
                    "Capturing electric moments",
                    "The rhythm of life intensified",
                ],
                "professional": [
                    "Channeling dynamic energy.",
                    "Embracing vitality and vigor.",
                    "Where passion meets action.",
                ],
                "playful": [
                    "Energy overload! ⚡🔥",
                    "Too much energy to handle! 💥",
                    "Let's gooo! 🚀💪",
                ],
            },
            "peaceful": {
                "casual": [
                    "Peace and quiet at its finest 🕊️",
                    "This is pure tranquility",
                    "Finding my zen moment",
                    "Peaceful vibes only",
                ],
                "aesthetic": [
                    "Sanctuary of stillness",
                    "Where peace dwells eternally",
                    "Meditation in visual form",
                    "The quietude of beauty",
                ],
                "professional": [
                    "Cultivating inner peace.",
                    "The essence of tranquility.",
                    "Finding harmony in stillness.",
                ],
                "playful": [
                    "Peace mode activated! ☮️✨",
                    "Zen master vibes! 🧘‍♀️",
                ],
            },
            "romantic": {
                "casual": [
                    "Love is in the air 💕",
                    "Feeling all the romantic vibes",
                    "This moment is pure magic",
                    "Dreamy and lovely ✨",
                ],
                "aesthetic": [
                    "Where romance blooms eternal",
                    "Poetry in visual form",
                    "Capturing tender moments",
                    "The language of love",
                ],
                "professional": [
                    "Celebrating moments of romance.",
                    "The art of romantic expression.",
                    "Where beauty meets emotion.",
                ],
                "playful": [
                    "Love vibes everywhere! 💖✨",
                    "Feeling the love! 💕💫",
                    "Romance overload! 🌹",
                ],
            },
            "nostalgic": {
                "casual": [
                    "Taking a trip down memory lane",
                    "This brings back so many memories",
                    "Vintage vibes all the way",
                    "Reminds me of the good old days",
                ],
                "aesthetic": [
                    "Echoes of timeless beauty",
                    "Where past meets present",
                    "Vintage soul, modern heart",
                    "Memories woven in time",
                ],
                "professional": [
                    "Honoring timeless traditions.",
                    "Classic elegance revisited.",
                    "Where heritage meets modernity.",
                ],
                "playful": [
                    "Throwback vibes! 📼✨",
                    "Retro and loving it! 🕰️",
                    "Old school cool! 📻",
                ],
            },
        }
        
        # Context-aware additions based on image caption
        self.context_additions = {
            "food": [
                "Foodie dreams come true!",
                "Taste the moment",
                "Culinary perfection",
                "Food for the soul",
            ],
            "nature": [
                "Nature's masterpiece",
                "Mother Earth showing off",
                "Natural beauty at its finest",
                "Earth's canvas",
            ],
            "travel": [
                "Wanderlust satisfied",
                "Travel tales",
                "Destination perfection",
                "Journey of a lifetime",
            ],
        }
    
    def generate_caption(
        self,
        sentiment: str,
        style: str = "casual",
        image_caption: str = "",
        category: str = "lifestyle"
    ) -> str:
        """
        Generate caption based on sentiment and style.
        
        Args:
            sentiment: Detected sentiment (happy, calm, cozy, etc.)
            style: Caption style (casual, aesthetic, professional, playful)
            image_caption: Optional image description for context
            category: Image category (food, travel, nature, lifestyle)
            
        Returns:
            Generated caption string
        """
        # Get templates for sentiment and style
        if sentiment in self.caption_templates and style in self.caption_templates[sentiment]:
            templates = self.caption_templates[sentiment][style]
            base_caption = random.choice(templates)
        else:
            # Fallback to casual happy
            base_caption = random.choice(self.caption_templates["happy"]["casual"])
        
        # Optionally add context-aware addition
        if category in self.context_additions and random.random() > 0.5:
            context_add = random.choice(self.context_additions[category])
            base_caption = f"{base_caption} {context_add}"
        
        return base_caption
    
    def generate_multiple_captions(
        self,
        sentiment: str,
        image_caption: str = "",
        category: str = "lifestyle",
        count: int = 3
    ) -> Dict[str, str]:
        """
        Generate multiple caption variants in different styles.
        
        Args:
            sentiment: Detected sentiment
            image_caption: Image description
            category: Image category
            count: Number of variants (max 4, one per style)
            
        Returns:
            Dictionary of style: caption pairs
        """
        styles = list(CAPTION_STYLES.keys())[:count]
        captions = {}
        
        for style in styles:
            captions[style] = self.generate_caption(
                sentiment=sentiment,
                style=style,
                image_caption=image_caption,
                category=category
            )
        
        return captions


# Singleton instance
_generator_instance = None

def get_caption_generator() -> CaptionGenerator:
    """Get or create singleton caption generator instance."""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = CaptionGenerator()
    return _generator_instance
