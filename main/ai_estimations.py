import base64
from typing import Dict, Optional, Union
from io import BytesIO
from django.conf import settings
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def analyze_floorplan_image(image_file, event_type: str = "wedding", pax: int = 100) -> Optional[str]:
    """
    Analyze uploaded floorplan image using OpenAI Vision API
    and provide estimations for tables, chairs, and booths.
    
    Args:
        image_file: Django UploadedFile object or base64 string
        event_type: Type of event (wedding, birthday, etc.)
        pax: Expected number of people
    
    Returns:
        String containing AI estimations or None if analysis fails
    """
    try:
        # Convert image to base64 if it's not already
        if isinstance(image_file, str):
            # Already base64 encoded
            base64_image = image_file
        else:
            # Django UploadedFile object
            image_file.seek(0)
            image_data = image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Create the prompt for floor plan analysis
        prompt = f"""
        Analyze this {event_type} floorplan image for {pax} people. Estimate room dimensions and seating.
        
        Requirements:
        - Max 8 people per table (both round and rectangular)
        - Same total people capacity for round vs rectangular options
        - Minimum 1 booth with ideal dimensions based on room size
        - Consider dance floor and walkways for {event_type}
        
        Respond in this exact format:
        
        ROOM DIMENSIONS: [length]m x [width]m
        ROUND TABLES: [number] tables ({pax} people) - [chairs_per_table] chairs each
        RECTANGULAR TABLES: [number] tables ({pax} people) - [chairs_per_table] chairs each
        TOTAL CHAIRS: [number] chairs
        BOOTHS: [number] booths ([length]m x [width]m each)
        
        Numbers only - no explanations.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use gpt-4o-mini for vision capabilities
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=150
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error analyzing floorplan image: {str(e)}")
        return None


def estimate_from_dimensions(length: float, width: float, event_type: str = "wedding", pax: int = 100) -> str:
    """
    Generate estimations based on room dimensions using OpenAI API.
    
    Args:
        length: Room length in meters
        width: Room width in meters  
        event_type: Type of event (wedding, birthday, corporate, etc.)
        pax: Expected number of people
    
    Returns:
        String containing AI estimations
    """
    try:
        area_sqm = length * width
        area_sqft = area_sqm * 10.764  # Convert to square feet
        
        prompt = f"""
        {event_type} event for {pax} people in {length}m x {width}m room ({area_sqm:.1f} sqm).
        
        Requirements:
        - Max 8 people per table (both round and rectangular)
        - Same total people capacity for round vs rectangular options
        - Minimum 1 booth with ideal dimensions based on room size
        - Consider dance floor and walkways for {event_type}
        
        Respond in this exact format:
        
        ROOM DIMENSIONS: {length}m x {width}m
        ROUND TABLES: [number] tables ({pax} people) - [chairs_per_table] chairs each
        RECTANGULAR TABLES: [number] tables ({pax} people) - [chairs_per_table] chairs each
        TOTAL CHAIRS: [number] chairs
        BOOTHS: [number] booths ([length]m x [width]m each)
        
        Numbers only.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_tokens=100
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error generating dimension-based estimations: {str(e)}")
        # Calculate tables needed (max 8 people per table)
        tables_needed = max(1, (pax + 7) // 8)  # Round up division
        chairs_per_table = min(8, (pax + tables_needed - 1) // tables_needed)  # Distribute chairs evenly
        total_chairs = pax
        min_booths = max(1, tables_needed // 10)  # At least 1 booth, more for larger events
        
        # Calculate ideal booth dimensions based on room size
        # Standard booth is typically 2m x 1.2m, but scale with room size
        booth_length = min(3.0, max(2.0, length * 0.2))  # 20% of room length, between 2-3m
        booth_width = min(2.0, max(1.2, width * 0.2))    # 20% of room width, between 1.2-2m
        
        return f"""ROOM DIMENSIONS: {length}m x {width}m
ROUND TABLES: {tables_needed} tables ({pax} people) - {chairs_per_table} chairs each
RECTANGULAR TABLES: {tables_needed} tables ({pax} people) - {chairs_per_table} chairs each
TOTAL CHAIRS: {total_chairs} chairs
BOOTHS: {min_booths} {'booth' if min_booths == 1 else 'booths'} ({booth_length:.1f}m x {booth_width:.1f}m each)"""


def validate_image_file(image_file) -> tuple[bool, str]:
    """
    Validate uploaded image file for floorplan analysis.
    
    Args:
        image_file: Django UploadedFile object
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if image_file.size > max_size:
        return False, "File size too large. Maximum 10MB allowed."
    
    # Check file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if image_file.content_type not in allowed_types:
        return False, "Invalid file type. Only JPEG, PNG, GIF, and WebP images are allowed."
    
    return True, ""