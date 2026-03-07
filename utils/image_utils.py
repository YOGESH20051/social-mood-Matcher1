"""
Image processing utilities for Social Mood Matcher.
Handles image validation, conversion, and preprocessing.
"""

from PIL import Image
import io
from typing import Optional, Tuple
from config.settings import IMAGE_CONFIG, UI_CONFIG


class ImageProcessor:
    """Handles all image processing operations."""
    
    def __init__(self):
        self.max_dimension = IMAGE_CONFIG["max_dimension"]
        self.thumbnail_size = IMAGE_CONFIG["thumbnail_size"]
        self.quality = IMAGE_CONFIG["quality"]
        self.supported_formats = UI_CONFIG["supported_formats"]
    
    def validate_image(self, uploaded_file) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded image file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if uploaded_file is None:
            return False, "No file uploaded"
        
        # Check file size
        max_size = UI_CONFIG["max_upload_size_mb"] * 1024 * 1024  # Convert to bytes
        if uploaded_file.size > max_size:
            return False, f"File size exceeds {UI_CONFIG['max_upload_size_mb']}MB limit"
        
        # Check file extension
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension not in self.supported_formats:
            return False, f"Unsupported format. Please upload: {', '.join(self.supported_formats)}"
        
        return True, None
    
    def load_image(self, uploaded_file) -> Optional[Image.Image]:
        """
        Load and convert uploaded file to PIL Image.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            PIL Image object or None if loading fails
        """
        try:
            # Read file bytes
            image_bytes = uploaded_file.read()
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return image
            
        except Exception as e:
            print(f"Error loading image: {str(e)}")
            return None
    
    def resize_image(self, image: Image.Image, max_dimension: Optional[int] = None) -> Image.Image:
        """
        Resize image while maintaining aspect ratio.
        
        Args:
            image: PIL Image object
            max_dimension: Maximum width or height (uses config default if None)
            
        Returns:
            Resized PIL Image
        """
        if max_dimension is None:
            max_dimension = self.max_dimension
        
        # Get current dimensions
        width, height = image.size
        
        # Check if resizing is needed
        if width <= max_dimension and height <= max_dimension:
            return image
        
        # Calculate new dimensions maintaining aspect ratio
        if width > height:
            new_width = max_dimension
            new_height = int((max_dimension / width) * height)
        else:
            new_height = max_dimension
            new_width = int((max_dimension / height) * width)
        
        # Resize image
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return resized_image
    
    def create_thumbnail(self, image: Image.Image) -> Image.Image:
        """
        Create thumbnail version of image.
        
        Args:
            image: PIL Image object
            
        Returns:
            Thumbnail PIL Image
        """
        thumbnail = image.copy()
        thumbnail.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
        return thumbnail
    
    def preprocess_for_model(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for model input.
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image
        """
        # Ensure RGB mode
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to reasonable dimensions for model
        image = self.resize_image(image, max_dimension=512)
        
        return image
    
    def get_image_info(self, image: Image.Image) -> dict:
        """
        Get image metadata and information.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary with image information
        """
        return {
            "width": image.size[0],
            "height": image.size[1],
            "mode": image.mode,
            "format": image.format,
            "aspect_ratio": round(image.size[0] / image.size[1], 2)
        }


def validate_and_load_image(uploaded_file) -> Tuple[Optional[Image.Image], Optional[str]]:
    """
    Convenience function to validate and load image in one step.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        Tuple of (PIL Image or None, error_message or None)
    """
    processor = ImageProcessor()
    
    # Validate
    is_valid, error_msg = processor.validate_image(uploaded_file)
    if not is_valid:
        return None, error_msg
    
    # Load
    image = processor.load_image(uploaded_file)
    if image is None:
        return None, "Failed to load image. The file may be corrupted."
    
    return image, None
