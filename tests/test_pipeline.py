"""
Test suite for Social Mood Matcher application.
Tests all core services and utilities.
"""

import pytest
from PIL import Image
import numpy as np
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.image_sentiment import ImageSentimentDetector
from services.caption_generator import CaptionGenerator
from services.hashtag_engine import HashtagEngine
from services.character_limiter import CharacterLimiter
from utils.image_utils import ImageProcessor
from utils.text_utils import TextProcessor


class TestImageProcessor:
    """Test image processing utilities."""
    
    def test_create_dummy_image(self):
        """Test creating a dummy image for testing."""
        processor = ImageProcessor()
        
        # Create a dummy RGB image
        img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        image = Image.fromarray(img_array, 'RGB')
        
        assert image.mode == 'RGB'
        assert image.size == (100, 100)
    
    def test_resize_image(self):
        """Test image resizing."""
        processor = ImageProcessor()
        
        # Create large image
        img_array = np.random.randint(0, 255, (2000, 2000, 3), dtype=np.uint8)
        image = Image.fromarray(img_array, 'RGB')
        
        # Resize
        resized = processor.resize_image(image, max_dimension=512)
        
        assert max(resized.size) <= 512
        assert resized.mode == 'RGB'
    
    def test_preprocess_for_model(self):
        """Test image preprocessing for model."""
        processor = ImageProcessor()
        
        img_array = np.random.randint(0, 255, (1000, 1000, 3), dtype=np.uint8)
        image = Image.fromarray(img_array, 'RGB')
        
        processed = processor.preprocess_for_model(image)
        
        assert processed.mode == 'RGB'
        assert max(processed.size) <= 512


class TestTextProcessor:
    """Test text processing utilities."""
    
    def test_clean_text(self):
        """Test text cleaning."""
        processor = TextProcessor()
        
        text = "  hello   world  "
        cleaned = processor.clean_text(text)
        
        assert cleaned == "Hello world"
    
    def test_format_hashtags(self):
        """Test hashtag formatting."""
        processor = TextProcessor()
        
        hashtags = ["Foodie", "#Travel", "Nature"]
        formatted = processor.format_hashtags(hashtags)
        
        assert formatted == "#Foodie #Travel #Nature"
    
    def test_truncate_text(self):
        """Test text truncation."""
        processor = TextProcessor()
        
        text = "This is a very long text that needs to be truncated"
        truncated = processor.truncate_text(text, max_length=20, preserve_words=True)
        
        assert len(truncated) <= 20
        assert not truncated.endswith(' ')
    
    def test_smart_truncate_with_hashtags(self):
        """Test smart truncation with hashtags."""
        processor = TextProcessor()
        
        caption = "This is a beautiful sunset at the beach"
        hashtags = "#Sunset #Beach #Nature #Beautiful #Photography"
        
        truncated_caption, truncated_hashtags = processor.smart_truncate_with_hashtags(
            caption, hashtags, max_length=50
        )
        
        combined = f"{truncated_caption}\n\n{truncated_hashtags}" if truncated_hashtags else truncated_caption
        assert len(combined) <= 50


class TestCaptionGenerator:
    """Test caption generation service."""
    
    def test_generate_caption(self):
        """Test caption generation."""
        generator = CaptionGenerator()
        
        caption = generator.generate_caption(
            sentiment="happy",
            style="casual",
            category="food"
        )
        
        assert isinstance(caption, str)
        assert len(caption) > 0
    
    def test_generate_multiple_captions(self):
        """Test generating multiple caption variants."""
        generator = CaptionGenerator()
        
        captions = generator.generate_multiple_captions(
            sentiment="calm",
            category="nature",
            count=3
        )
        
        assert len(captions) == 3
        assert all(isinstance(cap, str) for cap in captions.values())
    
    def test_all_sentiments(self):
        """Test caption generation for all sentiments."""
        generator = CaptionGenerator()
        
        sentiments = ["happy", "calm", "cozy", "aesthetic", "adventurous", 
                     "luxury", "energetic", "peaceful", "romantic", "nostalgic"]
        
        for sentiment in sentiments:
            caption = generator.generate_caption(sentiment=sentiment, style="casual")
            assert isinstance(caption, str)
            assert len(caption) > 0


class TestHashtagEngine:
    """Test hashtag engine service."""
    
    def test_get_hashtags(self):
        """Test hashtag generation."""
        engine = HashtagEngine()
        
        hashtags = engine.get_hashtags(
            category="food",
            sentiment="happy",
            count=5
        )
        
        assert len(hashtags) <= 5
        assert all(tag.startswith('#') for tag in hashtags)
    
    def test_get_hashtags_by_priority(self):
        """Test priority-based hashtag generation."""
        engine = HashtagEngine()
        
        all_sentiments = {
            "happy": 0.8,
            "cozy": 0.6,
            "calm": 0.4
        }
        
        hashtags = engine.get_hashtags_by_priority(
            category="food",
            sentiment="happy",
            all_sentiments=all_sentiments
        )
        
        assert len(hashtags) >= 3
        assert all(tag.startswith('#') for tag in hashtags)
    
    def test_get_category_hashtags(self):
        """Test category-specific hashtags."""
        engine = HashtagEngine()
        
        categories = ["food", "travel", "nature", "lifestyle"]
        
        for category in categories:
            hashtags = engine.get_category_hashtags(category, count=5)
            assert len(hashtags) <= 5
            assert all(tag.startswith('#') for tag in hashtags)
    
    def test_filter_hashtags_by_length(self):
        """Test hashtag length filtering."""
        engine = HashtagEngine()
        
        hashtags = ["#Short", "#ThisIsAVeryLongHashtagThatExceedsLimit", "#Medium"]
        filtered = engine.filter_hashtags_by_length(hashtags, max_length=15)
        
        assert all(len(tag) <= 15 for tag in filtered)


class TestCharacterLimiter:
    """Test character limiter service."""
    
    def test_check_limit(self):
        """Test character limit checking."""
        limiter = CharacterLimiter()
        
        text = "This is a short text"
        fits, count, limit = limiter.check_limit(text, platform="twitter")
        
        assert fits is True
        assert count == len(text)
        assert limit == 280
    
    def test_limit_text(self):
        """Test text limiting."""
        limiter = CharacterLimiter()
        
        caption = "This is a very long caption " * 20
        hashtags = "#Test #Hashtag #Example #More #Tags"
        
        limited_caption, limited_hashtags, metadata = limiter.limit_text(
            caption, hashtags, platform="twitter"
        )
        
        combined = f"{limited_caption}\n\n{limited_hashtags}" if limited_hashtags else limited_caption
        assert len(combined) <= 280
        assert metadata['truncated'] is True
    
    def test_format_for_platform(self):
        """Test platform-specific formatting."""
        limiter = CharacterLimiter()
        
        caption = "Beautiful sunset"
        hashtags = "#Sunset #Nature"
        
        formatted = limiter.format_for_platform(caption, hashtags, platform="twitter")
        
        assert caption in formatted
        assert "#Sunset" in formatted
    
    def test_get_character_stats(self):
        """Test character statistics."""
        limiter = CharacterLimiter()
        
        text = "This is a test message"
        stats = limiter.get_character_stats(text, platform="twitter")
        
        assert stats['character_count'] == len(text)
        assert stats['character_limit'] == 280
        assert stats['fits_limit'] is True
        assert 'percentage_used' in stats


class TestIntegration:
    """Integration tests for complete pipeline."""
    
    def test_complete_pipeline(self):
        """Test complete pipeline from image to final output."""
        # Create dummy image
        img_array = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        image = Image.fromarray(img_array, 'RGB')
        
        # Note: This test requires models to be loaded
        # In a real test environment, you might want to mock the models
        
        # For now, just test that services can be instantiated
        generator = CaptionGenerator()
        hashtag_engine = HashtagEngine()
        limiter = CharacterLimiter()
        
        # Test caption generation
        caption = generator.generate_caption(
            sentiment="happy",
            style="casual",
            category="food"
        )
        
        # Test hashtag generation
        hashtags = hashtag_engine.get_hashtags(
            category="food",
            sentiment="happy",
            count=5
        )
        
        # Test character limiting
        hashtag_string = ' '.join(hashtags)
        limited_caption, limited_hashtags, metadata = limiter.limit_text(
            caption, hashtag_string, platform="twitter"
        )
        
        # Verify output
        assert isinstance(limited_caption, str)
        assert isinstance(limited_hashtags, str)
        assert metadata['final_length'] <= 280


def test_character_limit_edge_cases():
    """Test edge cases for character limiting."""
    limiter = CharacterLimiter()
    
    # Test with empty caption
    caption = ""
    hashtags = "#Test"
    limited_caption, limited_hashtags, metadata = limiter.limit_text(caption, hashtags)
    assert limited_caption == ""
    
    # Test with empty hashtags
    caption = "Test caption"
    hashtags = ""
    limited_caption, limited_hashtags, metadata = limiter.limit_text(caption, hashtags)
    assert limited_caption == caption
    
    # Test with exactly at limit
    caption = "a" * 275
    hashtags = "#Test"
    limited_caption, limited_hashtags, metadata = limiter.limit_text(caption, hashtags)
    combined = f"{limited_caption}\n\n{limited_hashtags}" if limited_hashtags else limited_caption
    assert len(combined) <= 280


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
