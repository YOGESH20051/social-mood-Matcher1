"""
Google Gemini API integration for Social Mood Matcher.
Provides enhanced image analysis and caption generation using Gemini models.
"""

import os
import google.generativeai as genai
from PIL import Image
from typing import Dict, Optional
from config.settings import API_KEYS, SENTIMENT_CATEGORIES


class GeminiVisionAnalyzer:
    """Analyzes images using Google Gemini Vision API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini API client.
        
        Args:
            api_key: Google Gemini API key (uses env var if not provided)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or API_KEYS.get("gemini")
        
        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. Please set GEMINI_API_KEY in .env file or environment variables."
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("Gemini API initialized successfully")
    
    def analyze_image_sentiment(self, image: Image.Image) -> Dict:
        """
        Analyze image sentiment using Gemini Vision.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary with sentiment analysis results
        """
        try:
            # Create prompt for sentiment analysis
            prompt = f"""Analyze this image and provide:
1. A brief description of what you see (1-2 sentences)
2. The primary mood/vibe from these options: {', '.join(SENTIMENT_CATEGORIES)}
3. A confidence score (0-1) for your mood assessment
4. The image category: food, travel, nature, or lifestyle

Respond in this exact format:
Description: [your description]
Mood: [mood from the list]
Confidence: [0.0-1.0]
Category: [food/travel/nature/lifestyle]"""

            # Generate response
            response = self.model.generate_content([prompt, image])
            
            # Parse response
            result = self._parse_gemini_response(response.text)
            
            return {
                "sentiment": result.get("mood", "happy"),
                "confidence": result.get("confidence", 0.8),
                "caption": result.get("description", "A beautiful scene"),
                "category": result.get("category", "lifestyle"),
                "all_sentiments": {result.get("mood", "happy"): result.get("confidence", 0.8)},
                "success": True,
                "source": "gemini"
            }
            
        except Exception as e:
            print(f"Gemini API error: {str(e)}")
            return {
                "sentiment": "happy",
                "confidence": 0.5,
                "caption": "Unable to analyze image",
                "category": "lifestyle",
                "all_sentiments": {},
                "success": False,
                "error": str(e),
                "source": "gemini"
            }
    
    def generate_caption_variants(
        self,
        image: Image.Image,
        sentiment: str,
        category: str
    ) -> Dict[str, str]:
        """
        Generate multiple engagement-focused caption variants.
        
        Args:
            image: PIL Image object
            sentiment: Detected sentiment
            category: Image category
            
        Returns:
            Dictionary of caption variants (punchy, aesthetic, engagement)
        """
        try:
            prompt = f"""Break down this {category} image with a {sentiment} vibe into 3 distinct social media caption variants.

Requirements:
1. **Punchy**: Short, high-impact (under 10 words).
2. **Aesthetic**: Poetic, vibe-focused, "Instagrammable".
3. **Engagement**: Interactive, ending with a question to followers.

Don't include the hashtags. Respond in this exact format:
Punchy: [variant]
Aesthetic: [variant]
Engagement: [variant]"""

            response = self.model.generate_content([prompt, image])
            text = response.text.strip()
            
            variants = {"punchy": "", "aesthetic": "", "engagement": ""}
            lines = text.split('\n')
            for line in lines:
                if line.startswith("Punchy:"): variants["punchy"] = line.replace("Punchy:", "").strip()
                elif line.startswith("Aesthetic:"): variants["aesthetic"] = line.replace("Aesthetic:", "").strip()
                elif line.startswith("Engagement:"): variants["engagement"] = line.replace("Engagement:", "").strip()
            
            # Fallbacks if parsing fails
            if not variants["punchy"]: variants["punchy"] = f"Classic {sentiment} {category} vibes."
            
            return variants
            
        except Exception as e:
            print(f"Gemini variants error: {str(e)}")
            return {"punchy": f"Beautiful {category}!", "aesthetic": "", "engagement": ""}

    def get_visual_intelligence(self, image: Image.Image) -> Dict:
        """
        Extract professional visual insights: colors, objects, and composition.
        """
        try:
            prompt = """Analyze this image like a professional photographer and return:
1. Dominant Colors: List 3 main colors with their HEX codes and approximate names.
2. Detected Objects: List visible items.
3. Composition Tip: One tip on why this photo works or how to improve it.

Format:
Colors: [Color1] (HEX), [Color2] (HEX)...
Objects: [item1], [item2]...
Tip: [Your tip]"""

            response = self.model.generate_content([prompt, image])
            text = response.text.strip()
            
            analysis = {"colors": [], "objects": [], "tip": ""}
            lines = text.split('\n')
            for line in lines:
                if line.startswith("Colors:"): analysis["colors"] = line.replace("Colors:", "").strip()
                elif line.startswith("Objects:"): analysis["objects"] = line.replace("Objects:", "").strip()
                elif line.startswith("Tip:"): analysis["tip"] = line.replace("Tip:", "").strip()
                
            return analysis
        except Exception as e:
            return {"colors": "Analysis failed", "objects": "Unknown", "tip": "Keep shooting!"}

    
    def _parse_gemini_response(self, response_text: str) -> Dict:
        """
        Parse Gemini's structured response.
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            Parsed dictionary
        """
        result = {
            "description": "",
            "mood": "happy",
            "confidence": 0.8,
            "category": "lifestyle"
        }
        
        try:
            lines = response_text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                
                if line.startswith("Description:"):
                    result["description"] = line.replace("Description:", "").strip()
                elif line.startswith("Mood:"):
                    mood = line.replace("Mood:", "").strip().lower()
                    # Validate mood is in our categories
                    if mood in SENTIMENT_CATEGORIES:
                        result["mood"] = mood
                elif line.startswith("Confidence:"):
                    try:
                        conf = float(line.replace("Confidence:", "").strip())
                        result["confidence"] = max(0.0, min(1.0, conf))
                    except:
                        pass
                elif line.startswith("Category:"):
                    cat = line.replace("Category:", "").strip().lower()
                    if cat in ["food", "travel", "nature", "lifestyle"]:
                        result["category"] = cat
        
        except Exception as e:
            print(f"Warning: Error parsing Gemini response: {str(e)}")
        
        return result
    
    def get_detailed_analysis(self, image: Image.Image) -> Dict:
        """
        Get detailed image analysis including objects, colors, composition.
        
        Args:
            image: PIL Image object
            
        Returns:
            Detailed analysis dictionary
        """
        try:
            prompt = """Provide a detailed analysis of this image including:
1. Main subjects/objects
2. Dominant colors
3. Composition style
4. Lighting and atmosphere
5. Suggested hashtags (5-8 relevant hashtags)

Be concise but informative."""

            response = self.model.generate_content([prompt, image])
            
            return {
                "analysis": response.text,
                "success": True
            }
            
        except Exception as e:
            return {
                "analysis": "Unable to perform detailed analysis",
                "success": False,
                "error": str(e)
            }


# Singleton instance
_gemini_instance = None

def get_gemini_analyzer(api_key: Optional[str] = None) -> Optional[GeminiVisionAnalyzer]:
    """
    Get or create singleton Gemini analyzer instance.
    
    Args:
        api_key: Optional API key
        
    Returns:
        GeminiVisionAnalyzer instance or None if API key not available
    """
    global _gemini_instance
    
    if _gemini_instance is None:
        try:
            _gemini_instance = GeminiVisionAnalyzer(api_key)
        except ValueError as e:
            print(f"Gemini API Key warning: {str(e)}")
            return None
    
    return _gemini_instance
