"""
Hashtag engine service for Social Mood Matcher.
Generates trending 2024 hashtags based on sentiment and category.
"""

import random
from typing import List, Dict
from config.settings import TRENDING_HASHTAGS_2024, FALLBACK_HASHTAGS, HASHTAG_CONFIG


class HashtagEngine:
    """Generates trending hashtags based on sentiment and category."""
    
    def __init__(self):
        """Initialize hashtag engine with 2024 trending data."""
        self.hashtag_db = TRENDING_HASHTAGS_2024
        self.fallback_hashtags = FALLBACK_HASHTAGS
        self.max_hashtags = HASHTAG_CONFIG["max_hashtags"]
        self.min_hashtags = HASHTAG_CONFIG["min_hashtags"]
    
    def get_hashtags(
        self,
        category: str,
        sentiment: str,
        count: int = None
    ) -> List[str]:
        """
        Get trending hashtags based on category and sentiment.
        
        Args:
            category: Image category (food, travel, nature, lifestyle)
            sentiment: Detected sentiment (happy, calm, cozy, etc.)
            count: Number of hashtags to return (uses config default if None)
            
        Returns:
            List of hashtag strings
        """
        if count is None:
            count = random.randint(self.min_hashtags, self.max_hashtags)
        
        hashtags = []
        
        try:
            # Get category-specific hashtags
            if category in self.hashtag_db:
                category_tags = self.hashtag_db[category]
                
                # Try to get sentiment-specific hashtags first
                if sentiment in category_tags:
                    sentiment_tags = category_tags[sentiment]
                    hashtags.extend(random.sample(sentiment_tags, min(3, len(sentiment_tags))))
                
                # Add general category hashtags
                if "general" in category_tags:
                    general_tags = category_tags["general"]
                    remaining = count - len(hashtags)
                    if remaining > 0:
                        hashtags.extend(random.sample(general_tags, min(remaining, len(general_tags))))
            
            # Add general trending 2024 hashtags
            if len(hashtags) < count and "general" in self.hashtag_db:
                trending_tags = self.hashtag_db["general"]["2024_trending"]
                remaining = count - len(hashtags)
                available_tags = [tag for tag in trending_tags if tag not in hashtags]
                if available_tags:
                    hashtags.extend(random.sample(available_tags, min(remaining, len(available_tags))))
            
            # If still not enough, use fallback
            if len(hashtags) < self.min_hashtags:
                remaining = self.min_hashtags - len(hashtags)
                available_fallback = [tag for tag in self.fallback_hashtags if tag not in hashtags]
                hashtags.extend(random.sample(available_fallback, min(remaining, len(available_fallback))))
            
        except Exception as e:
            print(f"Error generating hashtags: {str(e)}")
            # Use fallback hashtags
            hashtags = random.sample(self.fallback_hashtags, min(count, len(self.fallback_hashtags)))
        
        # Ensure unique and limit to count
        hashtags = list(dict.fromkeys(hashtags))[:count]
        
        return hashtags
    
    def get_hashtags_by_priority(
        self,
        category: str,
        sentiment: str,
        all_sentiments: Dict[str, float] = None
    ) -> List[str]:
        """
        Get hashtags with priority based on sentiment confidence scores.
        
        Args:
            category: Image category
            sentiment: Primary sentiment
            all_sentiments: Dictionary of all sentiment scores
            
        Returns:
            List of prioritized hashtags
        """
        hashtags = []
        
        # Primary sentiment hashtags (40% of total)
        primary_count = max(3, int(self.max_hashtags * 0.4))
        primary_tags = self.get_hashtags(category, sentiment, primary_count)
        hashtags.extend(primary_tags)
        
        # Secondary sentiment hashtags if available (20% of total)
        if all_sentiments:
            # Sort sentiments by score
            sorted_sentiments = sorted(
                all_sentiments.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Get second highest sentiment
            if len(sorted_sentiments) > 1:
                secondary_sentiment = sorted_sentiments[1][0]
                secondary_count = max(1, int(self.max_hashtags * 0.2))
                
                try:
                    if category in self.hashtag_db and secondary_sentiment in self.hashtag_db[category]:
                        secondary_tags = self.hashtag_db[category][secondary_sentiment]
                        available_tags = [tag for tag in secondary_tags if tag not in hashtags]
                        if available_tags:
                            hashtags.extend(random.sample(available_tags, min(secondary_count, len(available_tags))))
                except:
                    pass
        
        # Fill remaining with general category and trending hashtags
        remaining = self.max_hashtags - len(hashtags)
        if remaining > 0:
            general_tags = self.get_hashtags(category, "general", remaining)
            available_tags = [tag for tag in general_tags if tag not in hashtags]
            hashtags.extend(available_tags[:remaining])
        
        # Ensure we have at least minimum hashtags
        if len(hashtags) < self.min_hashtags:
            remaining = self.min_hashtags - len(hashtags)
            available_fallback = [tag for tag in self.fallback_hashtags if tag not in hashtags]
            hashtags.extend(random.sample(available_fallback, min(remaining, len(available_fallback))))
        
        return hashtags[:self.max_hashtags]
    
    def get_category_hashtags(self, category: str, count: int = 5) -> List[str]:
        """
        Get general hashtags for a category.
        
        Args:
            category: Image category
            count: Number of hashtags
            
        Returns:
            List of hashtags
        """
        if category in self.hashtag_db and "general" in self.hashtag_db[category]:
            tags = self.hashtag_db[category]["general"]
            return random.sample(tags, min(count, len(tags)))
        return random.sample(self.fallback_hashtags, min(count, len(self.fallback_hashtags)))
    
    def get_trending_hashtags(self, count: int = 5) -> List[str]:
        """
        Get general trending 2024 hashtags.
        
        Args:
            count: Number of hashtags
            
        Returns:
            List of trending hashtags
        """
        if "general" in self.hashtag_db and "2024_trending" in self.hashtag_db["general"]:
            tags = self.hashtag_db["general"]["2024_trending"]
            return random.sample(tags, min(count, len(tags)))
        return random.sample(self.fallback_hashtags, min(count, len(self.fallback_hashtags)))
    
    def filter_hashtags_by_length(self, hashtags: List[str], max_length: int = None) -> List[str]:
        """
        Filter hashtags by maximum character length.
        
        Args:
            hashtags: List of hashtags
            max_length: Maximum length per hashtag
            
        Returns:
            Filtered list of hashtags
        """
        if max_length is None:
            max_length = HASHTAG_CONFIG["max_hashtag_length"]
        
        return [tag for tag in hashtags if len(tag) <= max_length]
    
    def calculate_trending_score(self, hashtag: str, category: str, sentiment: str) -> float:
        """
        Calculate trending score for a hashtag (for future ranking features).
        
        Args:
            hashtag: Hashtag string
            category: Image category
            sentiment: Sentiment
            
        Returns:
            Trending score (0-1)
        """
        score = 0.5  # Base score
        
        # Check if in trending 2024
        if "general" in self.hashtag_db and "2024_trending" in self.hashtag_db["general"]:
            if hashtag in self.hashtag_db["general"]["2024_trending"]:
                score += 0.3
        
        # Check if category-specific
        if category in self.hashtag_db:
            if "general" in self.hashtag_db[category] and hashtag in self.hashtag_db[category]["general"]:
                score += 0.1
            
            # Check if sentiment-specific
            if sentiment in self.hashtag_db[category] and hashtag in self.hashtag_db[category][sentiment]:
                score += 0.1
        
        return min(score, 1.0)


# Singleton instance
_engine_instance = None

def get_hashtag_engine() -> HashtagEngine:
    """Get or create singleton hashtag engine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = HashtagEngine()
    return _engine_instance
