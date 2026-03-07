"""
Text processing utilities for Social Mood Matcher.
Handles text cleaning, formatting, and manipulation.
"""

import re
from typing import List, Tuple


class TextProcessor:
    """Handles all text processing operations."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Input text string
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters (except basic punctuation and emojis)
        # Keep alphanumeric, spaces, basic punctuation, and emoji ranges
        text = re.sub(r'[^\w\s\.,!?\'\"#@\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF-]', '', text)
        
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        
        return text.strip()
    
    @staticmethod
    def format_hashtags(hashtags: List[str]) -> str:
        """
        Format list of hashtags into a single string.
        
        Args:
            hashtags: List of hashtag strings
            
        Returns:
            Formatted hashtag string
        """
        # Ensure hashtags start with #
        formatted = []
        for tag in hashtags:
            tag = tag.strip()
            if not tag.startswith('#'):
                tag = f"#{tag}"
            formatted.append(tag)
        
        return ' '.join(formatted)
    
    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """
        Extract hashtags from text.
        
        Args:
            text: Input text containing hashtags
            
        Returns:
            List of extracted hashtags
        """
        hashtags = re.findall(r'#\w+', text)
        return hashtags
    
    @staticmethod
    def remove_hashtags(text: str) -> str:
        """
        Remove hashtags from text.
        
        Args:
            text: Input text
            
        Returns:
            Text without hashtags
        """
        return re.sub(r'#\w+', '', text).strip()
    
    @staticmethod
    def truncate_text(text: str, max_length: int, preserve_words: bool = True) -> str:
        """
        Truncate text to maximum length.
        
        Args:
            text: Input text
            max_length: Maximum character length
            preserve_words: If True, avoid breaking words
            
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        
        if not preserve_words:
            return text[:max_length].strip()
        
        # Truncate at word boundary
        truncated = text[:max_length]
        
        # Find last space
        last_space = truncated.rfind(' ')
        
        if last_space > 0:
            truncated = truncated[:last_space]
        
        return truncated.strip()
    
    @staticmethod
    def smart_truncate_with_hashtags(caption: str, hashtags: str, max_length: int) -> Tuple[str, str]:
        """
        Smart truncation that prioritizes caption over hashtags.
        
        Args:
            caption: Caption text
            hashtags: Hashtag string
            max_length: Maximum total character length
            
        Returns:
            Tuple of (truncated_caption, truncated_hashtags)
        """
        # Calculate space needed
        space_between = 2  # Two spaces between caption and hashtags
        
        # If both fit, return as is
        total_length = len(caption) + space_between + len(hashtags)
        if total_length <= max_length:
            return caption, hashtags
        
        # Priority: Keep full caption if possible
        if len(caption) + space_between <= max_length:
            # Truncate hashtags
            remaining_space = max_length - len(caption) - space_between
            hashtag_list = hashtags.split()
            
            truncated_hashtags = []
            current_length = 0
            
            for tag in hashtag_list:
                if current_length + len(tag) + 1 <= remaining_space:  # +1 for space
                    truncated_hashtags.append(tag)
                    current_length += len(tag) + 1
                else:
                    break
            
            return caption, ' '.join(truncated_hashtags)
        
        # If caption alone is too long, truncate caption and skip hashtags
        if len(caption) > max_length:
            truncated_caption = TextProcessor.truncate_text(caption, max_length - 3, preserve_words=True) + "..."
            return truncated_caption, ""
        
        # Truncate both caption and hashtags
        caption_space = int(max_length * 0.7)  # Give 70% to caption
        hashtag_space = max_length - caption_space - space_between
        
        truncated_caption = TextProcessor.truncate_text(caption, caption_space, preserve_words=True)
        
        # Truncate hashtags
        hashtag_list = hashtags.split()
        truncated_hashtags = []
        current_length = 0
        
        for tag in hashtag_list:
            if current_length + len(tag) + 1 <= hashtag_space:
                truncated_hashtags.append(tag)
                current_length += len(tag) + 1
            else:
                break
        
        return truncated_caption, ' '.join(truncated_hashtags)
    
    @staticmethod
    def count_characters(text: str) -> int:
        """
        Count characters in text.
        
        Args:
            text: Input text
            
        Returns:
            Character count
        """
        return len(text)
    
    @staticmethod
    def add_emoji(text: str, emoji: str, position: str = "end") -> str:
        """
        Add emoji to text.
        
        Args:
            text: Input text
            emoji: Emoji to add
            position: "start" or "end"
            
        Returns:
            Text with emoji
        """
        if position == "start":
            return f"{emoji} {text}"
        else:
            return f"{text} {emoji}"
    
    @staticmethod
    def validate_hashtag(hashtag: str) -> bool:
        """
        Validate hashtag format.
        
        Args:
            hashtag: Hashtag string
            
        Returns:
            True if valid, False otherwise
        """
        # Hashtag should start with # and contain only alphanumeric and underscores
        pattern = r'^#[A-Za-z0-9_]+$'
        return bool(re.match(pattern, hashtag))


def combine_caption_and_hashtags(caption: str, hashtags: List[str], max_length: int = 280) -> str:
    """
    Combine caption and hashtags with smart truncation.
    
    Args:
        caption: Caption text
        hashtags: List of hashtags
        max_length: Maximum character length (default: Twitter limit)
        
    Returns:
        Combined text with caption and hashtags
    """
    processor = TextProcessor()
    
    # Format hashtags
    hashtag_string = processor.format_hashtags(hashtags)
    
    # Smart truncate
    final_caption, final_hashtags = processor.smart_truncate_with_hashtags(
        caption, hashtag_string, max_length
    )
    
    # Combine
    if final_hashtags:
        return f"{final_caption}\n\n{final_hashtags}"
    else:
        return final_caption
