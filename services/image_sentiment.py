"""
Image sentiment detection service for Social Mood Matcher.
Analyzes images to detect mood/vibe and returns sentiment with confidence score.
"""

from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from transformers import pipeline
import torch
from typing import Dict, Tuple
from config.settings import MODEL_CONFIG, SENTIMENT_CATEGORIES


class ImageSentimentDetector:
    """Detects sentiment/vibe from images using vision-language models."""
    
    def __init__(self):
        """Initialize the sentiment detection models."""
        self.device = MODEL_CONFIG["image_captioning"]["device"]
        self.cache_dir = MODEL_CONFIG["image_captioning"]["cache_dir"]
        
        # Initialize BLIP for image captioning
        print("Loading image captioning model...")
        self.caption_processor = BlipProcessor.from_pretrained(
            MODEL_CONFIG["image_captioning"]["model_name"],
            cache_dir=self.cache_dir
        )
        self.caption_model = BlipForConditionalGeneration.from_pretrained(
            MODEL_CONFIG["image_captioning"]["model_name"],
            cache_dir=self.cache_dir
        ).to(self.device)
        
        # Initialize sentiment classifier
        print("Loading sentiment analysis model...")
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model=MODEL_CONFIG["sentiment"]["model_name"],
            device=0 if self.device == "cuda" else -1
        )
        
        # Sentiment mapping keywords
        self.sentiment_keywords = {
            "happy": ["happy", "joyful", "cheerful", "bright", "colorful", "vibrant", "smiling", "fun"],
            "calm": ["calm", "peaceful", "serene", "quiet", "tranquil", "gentle", "soft", "still"],
            "cozy": ["cozy", "warm", "comfortable", "homey", "intimate", "inviting", "snug"],
            "aesthetic": ["aesthetic", "artistic", "beautiful", "elegant", "stylish", "minimalist", "clean"],
            "adventurous": ["adventure", "exciting", "wild", "outdoor", "mountain", "hiking", "exploring"],
            "luxury": ["luxury", "elegant", "premium", "sophisticated", "fine", "gourmet", "upscale"],
            "energetic": ["energetic", "dynamic", "active", "lively", "busy", "vibrant", "bold"],
            "peaceful": ["peaceful", "relaxing", "soothing", "tranquil", "zen", "meditative"],
            "romantic": ["romantic", "lovely", "dreamy", "sunset", "candlelight", "intimate"],
            "nostalgic": ["nostalgic", "vintage", "retro", "classic", "old", "traditional", "rustic"],
        }
    
    def generate_caption(self, image: Image.Image) -> str:
        """
        Generate descriptive caption for image using BLIP.
        
        Args:
            image: PIL Image object
            
        Returns:
            Generated caption string
        """
        try:
            # Preprocess image
            inputs = self.caption_processor(image, return_tensors="pt").to(self.device)
            
            # Generate caption
            with torch.no_grad():
                output = self.caption_model.generate(**inputs, max_length=50)
            
            # Decode caption
            caption = self.caption_processor.decode(output[0], skip_special_tokens=True)
            
            return caption
            
        except Exception as e:
            print(f"Error generating caption: {str(e)}")
            return "a scene"
    
    def analyze_sentiment_from_text(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment from text description.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of sentiment scores
        """
        sentiment_scores = {}
        
        # Get base sentiment (positive/negative)
        try:
            base_sentiment = self.sentiment_analyzer(text)[0]
            base_score = base_sentiment['score'] if base_sentiment['label'] == 'POSITIVE' else 1 - base_sentiment['score']
        except:
            base_score = 0.5
        
        # Analyze keywords for specific sentiments
        text_lower = text.lower()
        
        for sentiment, keywords in self.sentiment_keywords.items():
            score = 0.0
            matches = 0
            
            for keyword in keywords:
                if keyword in text_lower:
                    matches += 1
                    score += 0.2  # Each keyword match adds to score
            
            # Normalize score
            if matches > 0:
                score = min(score, 1.0)
                # Boost with base sentiment
                score = (score + base_score) / 2
            else:
                score = base_score * 0.3  # Low score if no keywords match
            
            sentiment_scores[sentiment] = round(score, 3)
        
        return sentiment_scores
    
    def detect_category(self, caption: str) -> str:
        """
        Detect image category (food, travel, nature, lifestyle).
        
        Args:
            caption: Image caption
            
        Returns:
            Category string
        """
        caption_lower = caption.lower()
        
        # Category keywords
        food_keywords = ["food", "meal", "dish", "plate", "eating", "restaurant", "kitchen", 
                        "cooking", "dessert", "drink", "coffee", "cake", "pizza", "burger"]
        travel_keywords = ["travel", "city", "building", "street", "architecture", "landmark",
                          "hotel", "airport", "beach", "vacation", "trip"]
        nature_keywords = ["nature", "tree", "forest", "mountain", "sky", "water", "ocean",
                          "lake", "river", "flower", "plant", "landscape", "sunset", "sunrise"]
        
        # Count matches
        food_score = sum(1 for kw in food_keywords if kw in caption_lower)
        travel_score = sum(1 for kw in travel_keywords if kw in caption_lower)
        nature_score = sum(1 for kw in nature_keywords if kw in caption_lower)
        
        # Determine category
        scores = {
            "food": food_score,
            "travel": travel_score,
            "nature": nature_score,
            "lifestyle": 1  # Default baseline
        }
        
        return max(scores, key=scores.get)
    
    def detect_sentiment(self, image: Image.Image) -> Dict:
        """
        Main method to detect sentiment from image.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary with sentiment, confidence, caption, and category
        """
        try:
            # Generate caption
            caption = self.generate_caption(image)
            
            # Analyze sentiment
            sentiment_scores = self.analyze_sentiment_from_text(caption)
            
            # Get top sentiment
            top_sentiment = max(sentiment_scores, key=sentiment_scores.get)
            confidence = sentiment_scores[top_sentiment]
            
            # Detect category
            category = self.detect_category(caption)
            
            return {
                "sentiment": top_sentiment,
                "confidence": confidence,
                "all_sentiments": sentiment_scores,
                "caption": caption,
                "category": category,
                "success": True
            }
            
        except Exception as e:
            print(f"Error in sentiment detection: {str(e)}")
            return {
                "sentiment": "happy",
                "confidence": 0.5,
                "all_sentiments": {},
                "caption": "Unable to analyze image",
                "category": "lifestyle",
                "success": False,
                "error": str(e)
            }


# Singleton instance for caching
_detector_instance = None

def get_sentiment_detector() -> ImageSentimentDetector:
    """Get or create singleton sentiment detector instance."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = ImageSentimentDetector()
    return _detector_instance
