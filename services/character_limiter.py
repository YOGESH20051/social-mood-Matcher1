"""
Character limiter service for Social Mood Matcher.
Ensures output text fits within platform character limits (Twitter/X, etc.).
"""

from typing import Tuple, Dict
from config.settings import CHARACTER_LIMITS
from utils.text_utils import TextProcessor


class CharacterLimiter:
    """Handles character limiting for various social media platforms."""
    
    def __init__(self):
        """Initialize character limiter with platform limits."""
        self.limits = CHARACTER_LIMITS
        self.text_processor = TextProcessor()
    
    def get_limit(self, platform: str = "twitter") -> int:
        """
        Get character limit for platform.
        
        Args:
            platform: Platform name (twitter, instagram, facebook)
            
        Returns:
            Character limit
        """
        return self.limits.get(platform, self.limits["default"])
    
    def check_limit(self, text: str, platform: str = "twitter") -> Tuple[bool, int, int]:
        """
        Check if text fits within platform limit.
        
        Args:
            text: Text to check
            platform: Platform name
            
        Returns:
            Tuple of (fits_limit, character_count, limit)
        """
        limit = self.get_limit(platform)
        count = len(text)
        fits = count <= limit
        
        return fits, count, limit
    
    def limit_text(
        self,
        caption: str,
        hashtags: str,
        platform: str = "twitter"
    ) -> Tuple[str, str, Dict]:
        """
        Limit caption and hashtags to fit platform character limit.
        
        Args:
            caption: Caption text
            hashtags: Hashtag string
            platform: Platform name
            
        Returns:
            Tuple of (limited_caption, limited_hashtags, metadata)
        """
        limit = self.get_limit(platform)
        
        # Combine to check total length
        combined = f"{caption}\n\n{hashtags}" if hashtags else caption
        
        # Check if already fits
        if len(combined) <= limit:
            return caption, hashtags, {
                "truncated": False,
                "original_length": len(combined),
                "final_length": len(combined),
                "limit": limit,
                "platform": platform
            }
        
        # Need to truncate - use smart truncation
        limited_caption, limited_hashtags = self.text_processor.smart_truncate_with_hashtags(
            caption, hashtags, limit
        )
        
        # Recombine
        final_combined = f"{limited_caption}\n\n{limited_hashtags}" if limited_hashtags else limited_caption
        
        return limited_caption, limited_hashtags, {
            "truncated": True,
            "original_length": len(combined),
            "final_length": len(final_combined),
            "limit": limit,
            "platform": platform,
            "caption_truncated": len(limited_caption) < len(caption),
            "hashtags_truncated": len(limited_hashtags) < len(hashtags)
        }
    
    def format_for_platform(
        self,
        caption: str,
        hashtags: str,
        platform: str = "twitter",
        include_newlines: bool = True
    ) -> str:
        """
        Format caption and hashtags for specific platform.
        
        Args:
            caption: Caption text
            hashtags: Hashtag string
            platform: Platform name
            include_newlines: Whether to include newlines between caption and hashtags
            
        Returns:
            Formatted text string
        """
        # Limit text first
        limited_caption, limited_hashtags, _ = self.limit_text(caption, hashtags, platform)
        
        # Format based on platform preferences
        if platform == "twitter":
            # Twitter: Caption + double newline + hashtags
            if limited_hashtags and include_newlines:
                return f"{limited_caption}\n\n{limited_hashtags}"
            elif limited_hashtags:
                return f"{limited_caption} {limited_hashtags}"
            else:
                return limited_caption
        
        elif platform == "instagram":
            # Instagram: Caption + newline + hashtags
            if limited_hashtags and include_newlines:
                return f"{limited_caption}\n{limited_hashtags}"
            elif limited_hashtags:
                return f"{limited_caption} {limited_hashtags}"
            else:
                return limited_caption
        
        else:
            # Default format
            if limited_hashtags and include_newlines:
                return f"{limited_caption}\n\n{limited_hashtags}"
            elif limited_hashtags:
                return f"{limited_caption} {limited_hashtags}"
            else:
                return limited_caption
    
    def get_character_stats(self, text: str, platform: str = "twitter") -> Dict:
        """
        Get detailed character statistics for text.
        
        Args:
            text: Text to analyze
            platform: Platform name
            
        Returns:
            Dictionary with character statistics
        """
        limit = self.get_limit(platform)
        count = len(text)
        remaining = limit - count
        percentage = (count / limit) * 100
        
        return {
            "character_count": count,
            "character_limit": limit,
            "characters_remaining": remaining,
            "percentage_used": round(percentage, 1),
            "fits_limit": count <= limit,
            "platform": platform
        }
    
    def suggest_truncation(
        self,
        caption: str,
        hashtags: str,
        platform: str = "twitter"
    ) -> Dict:
        """
        Suggest how to truncate text if it exceeds limit.
        
        Args:
            caption: Caption text
            hashtags: Hashtag string
            platform: Platform name
            
        Returns:
            Dictionary with truncation suggestions
        """
        limit = self.get_limit(platform)
        combined = f"{caption}\n\n{hashtags}" if hashtags else caption
        
        if len(combined) <= limit:
            return {
                "needs_truncation": False,
                "message": "Text fits within limit"
            }
        
        # Calculate how much to remove
        excess = len(combined) - limit
        
        # Suggest options
        suggestions = {
            "needs_truncation": True,
            "excess_characters": excess,
            "suggestions": []
        }
        
        # Option 1: Remove some hashtags
        hashtag_list = hashtags.split()
        if len(hashtag_list) > 3:
            suggestions["suggestions"].append({
                "option": "Remove some hashtags",
                "description": f"Remove {len(hashtag_list) - 3} hashtags to fit"
            })
        
        # Option 2: Shorten caption
        if len(caption) > 100:
            suggestions["suggestions"].append({
                "option": "Shorten caption",
                "description": f"Reduce caption by ~{excess} characters"
            })
        
        # Option 3: Remove all hashtags
        if len(hashtags) > 0:
            suggestions["suggestions"].append({
                "option": "Remove all hashtags",
                "description": "Focus on caption only"
            })
        
        return suggestions


# Singleton instance
_limiter_instance = None

def get_character_limiter() -> CharacterLimiter:
    """Get or create singleton character limiter instance."""
    global _limiter_instance
    if _limiter_instance is None:
        _limiter_instance = CharacterLimiter()
    return _limiter_instance
