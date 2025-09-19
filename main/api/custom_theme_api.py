from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
import json
from openai import OpenAI
import cloudinary
import cloudinary.uploader
from datetime import datetime
import hashlib
import requests
from io import BytesIO
import time

# Configure OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

@csrf_exempt
@require_http_methods(["POST"])
def generate_custom_theme(request):
    """
    Generate custom theme images using OpenAI DALL-E API
    """
    try:
        print(f"Request method: {request.method}")
        print(f"Request body: {request.body}")
        
        # Parse request data
        data = json.loads(request.body)
        print(f"Parsed data: {data}")
        
        description = data.get('description', '').strip()
        event_type = data.get('event_type', 'birthday')
        colors = data.get('colors', [])
        pax = data.get('pax', 50)
        
        print(f"Processing: description='{description}', event_type='{event_type}', colors={colors}, pax={pax}")
        
        # Test OpenAI client configuration
        print(f"OpenAI API key configured: {bool(settings.OPENAI_API_KEY)}")
        print(f"Client initialized: {client is not None}")
        
        # Quick test mode - return mock data for testing
        if description == 'TEST_MODE':
            print("Running in test mode - returning mock data")
            return JsonResponse({
                'success': True,
                'theme_name': 'Test Custom Theme #1234',
                'theme_images': [
                    'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757784429/chickenpastel_mgfrq5.jpg',
                    'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757784418/chickenbbq_lkpnac.jpg',
                    'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757784417/orangechicken_jo3vc3.jpg'
                ],
                'description': description
            })
        

        
        # Generate enhanced prompt using reference images and provided template
        enhanced_prompt = generate_event_entrance_prompt(event_type, colors, description, pax)
        
        # Log the selected reference style for debugging
        selected_style = select_reference_style(event_type, colors, description)
        print(f"Selected reference style: {selected_style} for event: {event_type}, colors: {colors}, description: {description}")
        
        # Generate theme name
        theme_name = generate_theme_name(description, event_type, colors)
        
        # Generate 1 image using OpenAI DALL-E
        generated_image_url = None
        
        try:
            print(f"Generating single image with prompt: {enhanced_prompt[:100]}...")
            print("Starting OpenAI DALL-E 3 image generation (may take 1-3 minutes)...")
            
            # Call OpenAI DALL-E API with proper timeout handling
            # DALL-E 3 can take up to 3-4 minutes, so we set a generous timeout
            start_time = time.time()
            
            response = client.images.generate(
                prompt=enhanced_prompt,
                n=1,
                size="1024x1024",
                quality="standard",
                model="dall-e-3",
                timeout=300  # 5 minute timeout for OpenAI API
            )
            
            generation_time = time.time() - start_time
            print(f"Image generation completed in {generation_time:.2f} seconds")
            
            # Verify we got a response
            if not response.data or len(response.data) == 0:
                raise Exception("OpenAI API returned no image data")
            
            # Get the image URL
            image_url = response.data[0].url
            print(f"Generated image URL: {image_url}")
            
            if not image_url:
                raise Exception("OpenAI API returned empty image URL")
            
            # Download and upload to Cloudinary with retry logic
            print("Uploading generated image to Cloudinary...")
            cloudinary_url = upload_to_cloudinary_with_retry(image_url, theme_name, 1)
            
            if cloudinary_url:
                generated_image_url = cloudinary_url
                print(f"Successfully uploaded to Cloudinary: {cloudinary_url}")
            else:
                raise Exception("Failed to upload image to Cloudinary after retries")
                
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Provide more specific error messages
            error_message = str(e)
            if "timeout" in error_message.lower():
                error_message = "Image generation timed out. Please try again with a shorter description."
            elif "rate limit" in error_message.lower():
                error_message = "OpenAI rate limit exceeded. Please wait a moment and try again."
            elif "cloudinary" in error_message.lower():
                error_message = "Failed to save the generated image. Please try again."
            
            return JsonResponse({
                'success': False,
                'error': f'Failed to generate image: {error_message}'
            })
        
        if not generated_image_url:
            return JsonResponse({
                'success': False,
                'error': 'Failed to generate image. Please try again.'
            })
        
        return JsonResponse({
            'success': True,
            'theme_name': theme_name,
            'theme_image': generated_image_url,  # Single image instead of array
            'description': description
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        print(f"Error in generate_custom_theme: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': f'An error occurred while generating the theme: {str(e)}'
        })


def generate_theme_name(description, event_type, colors):
    """Generate a creative theme name based on the description"""
    
    # Extract key words from description
    words = description.lower().split()
    key_words = []
    
    # Look for style/aesthetic words
    style_words = ['elegant', 'rustic', 'modern', 'vintage', 'bohemian', 'classic', 'royal', 
                   'glamorous', 'minimalist', 'tropical', 'garden', 'fairy', 'princess',
                   'superhero', 'disney', 'movie', 'gaming', 'sports', 'animal', 'floral']
    
    for word in words:
        if word in style_words:
            key_words.append(word.capitalize())
    
    # Add color information
    if colors:
        if len(colors) == 1:
            key_words.append(colors[0].capitalize())
        elif len(colors) == 2:
            key_words.append(f"{colors[0].capitalize()} & {colors[1].capitalize()}")
    
    # Create theme name
    if key_words:
        if len(key_words) >= 2:
            theme_name = f"{key_words[0]} {key_words[1]} {event_type.capitalize()}"
        else:
            theme_name = f"{key_words[0]} {event_type.capitalize()}"
    else:
        # Fallback to color-based or generic name
        if colors:
            theme_name = f"Custom {colors[0].capitalize()} {event_type.capitalize()}"
        else:
            theme_name = f"Custom AI {event_type.capitalize()}"
    
    # Add timestamp to make it unique
    timestamp = datetime.now().strftime("%m%d%H%M")
    theme_name += f" #{timestamp}"
    
    return theme_name


def enhance_prompt_for_image(base_prompt, image_index):
    """Create variations of the prompt for different images"""
    
    variations = [
        # Image 1: Overall venue view
        f"{base_prompt} Show a wide angle view of the entire party venue setup with multiple decorated tables and the main backdrop.",
        
        # Image 2: Close-up table setting
        f"{base_prompt} Focus on an elegantly decorated table with detailed place settings, centerpieces, and table decorations.",
        
        # Image 3: Backdrop/focal point
        f"{base_prompt} Show the main backdrop or focal decoration area with detailed styling and decorative elements."
    ]
    
    return variations[image_index] if image_index < len(variations) else base_prompt


def upload_to_cloudinary_with_retry(image_url, theme_name, image_number, max_retries=3):
    """Download image from OpenAI and upload to Cloudinary with retry logic"""
    for attempt in range(max_retries):
        try:
            print(f"Cloudinary upload attempt {attempt + 1}/{max_retries}")
            
            # Download image from OpenAI URL with longer timeout
            print(f"Downloading image from OpenAI URL: {image_url}")
            response = requests.get(image_url, timeout=60)  # Increased timeout
            response.raise_for_status()
            
            if len(response.content) == 0:
                raise Exception("Downloaded image is empty")
            
            print(f"Downloaded image size: {len(response.content)} bytes")
            
            # Create a unique filename
            clean_theme_name = "".join(c for c in theme_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            clean_theme_name = clean_theme_name.replace(' ', '_').lower()
            
            # Generate hash for uniqueness
            content_hash = hashlib.md5(response.content).hexdigest()[:8]
            filename = f"custom_{clean_theme_name}_{image_number}_{content_hash}"
            
            print(f"Uploading to Cloudinary with filename: {filename}")
            
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                BytesIO(response.content),
                public_id=filename,
                folder="themes",
                resource_type="image",
                format="jpg",
                quality="auto",
                fetch_format="auto",
                timeout=120  # 2 minute timeout for Cloudinary upload
            )
            
            secure_url = upload_result['secure_url']
            print(f"Cloudinary upload successful: {secure_url}")
            return secure_url
            
        except Exception as e:
            print(f"Upload attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries - 1:
                # Last attempt failed
                return None
            else:
                # Wait before retry
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                continue
    
    return None


def upload_to_cloudinary(image_url, theme_name, image_number):
    """Download image from OpenAI and upload to Cloudinary"""
    try:
        # Download image from OpenAI URL
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Create a unique filename
        clean_theme_name = "".join(c for c in theme_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_theme_name = clean_theme_name.replace(' ', '_').lower()
        
        # Generate hash for uniqueness
        content_hash = hashlib.md5(response.content).hexdigest()[:8]
        filename = f"custom_{clean_theme_name}_{image_number}_{content_hash}"
        
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            BytesIO(response.content),
            public_id=filename,
            folder="themes",
            resource_type="image",
            format="jpg",
            quality="auto",
            fetch_format="auto"
        )
        
        return upload_result['secure_url']
        
    except Exception as e:
        print(f"Error uploading to Cloudinary: {str(e)}")
        return None


def get_event_context(event_type):
    """Generate appropriate context based on event type"""
    event_contexts = {
        'birthday': 'Festive and joyful birthday party atmosphere with celebration elements, balloons, and party decorations',
        'wedding': 'Romantic and elegant wedding ceremony and reception with flowers, candles, and sophisticated decor',
        'christening': 'Gentle and peaceful christening celebration with soft, angelic elements and religious motifs',
        'kiddie': 'Fun and colorful kids party with playful elements, cartoon themes, and child-friendly decorations',
        'graduation': 'Achievement-focused graduation party with academic colors, diplomas, and celebratory elements',
        'anniversary': 'Romantic anniversary celebration with intimate lighting, flowers, and sophisticated elegance',
        'corporate': 'Professional corporate event with clean lines, company colors, and business-appropriate decor'
    }
    
    return event_contexts.get(event_type.lower(), 'Beautiful celebration with elegant decorations and festive atmosphere')


def format_color_palette(colors):
    """Format the color array into a readable palette description"""
    if not colors:
        return ""
    
    if len(colors) == 1:
        return f"elegant {colors[0]}"
    elif len(colors) == 2:
        return f"beautiful {colors[0]} and {colors[1]}"
    elif len(colors) == 3:
        return f"sophisticated {colors[0]}, {colors[1]}, and {colors[2]}"
    else:
        return f"multicolored palette featuring {', '.join(colors[:3])}"


def get_reference_venue_descriptions():
    """Get detailed descriptions of Nike's Catering Services venue styles based on reference images"""
    return {
        'elegant_traditional': {
            'venue': "Traditional Filipino event hall with high ceilings, exposed wooden beams, and professional lighting setup",
            'ceiling': "Dramatic white fabric draping radiating from center point with multiple hanging crystal chandeliers creating elegant ambiance",
            'entrance': "Grand entrance pathway with red carpet runner leading to ornate main backdrop",
            'backdrop': "Large decorative backdrop with intricate patterns, floral arrangements, and themed signage",
            'tables': "Round dining tables with crisp white linens, gold/yellow chair covers, and matching table settings",
            'catering': "Professional food display areas with elegant serving stations and ambient lighting"
        },
        'modern_balloon': {
            'venue': "Contemporary event space with industrial ceiling and modern lighting fixtures",
            'ceiling': "White fabric draping with cascading balloon ceiling installation in coordinated colors",
            'entrance': "Stunning balloon arch entrance with organic balloon clusters and themed signage",
            'backdrop': "Custom themed backdrop with balloon decorations and coordinating color scheme",
            'tables': "Modern table arrangements with colored linens matching the theme and balloon centerpieces",
            'catering': "Sleek catering stations with contemporary presentation and themed accents"
        },
        'garden_nature': {
            'venue': "Natural-themed indoor space with greenhouse-style ceiling and abundant natural light",
            'ceiling': "Clear or light-colored ceiling treatment allowing natural ambiance with hanging elements",
            'entrance': "Elegant floral arch entrance adorned with butterflies, flowers, and natural elements",
            'backdrop': "Nature-inspired backdrop with garden themes, fairy elements, and organic decorations",
            'tables': "Tables with natural linens, floral centerpieces, and garden-themed place settings",
            'catering': "Organic food presentation with natural elements and garden-style serving areas"
        },
        'rustic_elegant': {
            'venue': "Rustic venue with exposed wooden beam ceiling and natural architectural elements",
            'ceiling': "Natural wooden beam ceiling with minimal white fabric accents and warm ambient lighting", 
            'entrance': "Classic floral arch entrance with white flowers and greenery over elegant carpet runner",
            'backdrop': "Sophisticated floral backdrop with white and green arrangements and elegant signage",
            'tables': "Refined table settings with natural elements, white linens, and sophisticated centerpieces",
            'catering': "Elegant catering displays with rustic charm and sophisticated presentation"
        }
    }

def select_reference_style(event_type, colors, description):
    """Select the most appropriate reference style based on event details"""
    description_lower = description.lower() if description else ""
    
    # Check for specific style keywords
    if any(word in description_lower for word in ['balloon', 'modern', 'contemporary', 'colorful']):
        return 'modern_balloon'
    elif any(word in description_lower for word in ['nature', 'garden', 'butterfly', 'fairy', 'forest', 'green']):
        return 'garden_nature'  
    elif any(word in description_lower for word in ['rustic', 'wooden', 'natural', 'organic', 'country']):
        return 'rustic_elegant'
    elif any(word in description_lower for word in ['elegant', 'traditional', 'classic', 'formal', 'gold']):
        return 'elegant_traditional'
    
    # Default based on event type
    if event_type.lower() in ['wedding', 'anniversary']:
        return 'elegant_traditional'
    elif event_type.lower() in ['kiddie', 'birthday']:
        return 'modern_balloon'
    elif event_type.lower() in ['christening', 'garden party']:
        return 'garden_nature'
    else:
        return 'elegant_traditional'

def generate_event_entrance_prompt(event_type, colors, description, pax):
    """Generate enhanced event entrance design prompt using Nike's Catering Services reference styles"""
    
    # Get reference descriptions
    reference_styles = get_reference_venue_descriptions()
    selected_style = select_reference_style(event_type, colors, description)
    style_ref = reference_styles[selected_style]
    
    # Format colors for the prompt
    if colors and len(colors) > 0:
        if len(colors) == 1:
            color_scheme = f"primarily {colors[0].lower()}"
        elif len(colors) == 2:
            color_scheme = f"{colors[0].lower()} and {colors[1].lower()}"
        else:
            color_scheme = f"{colors[0].lower()}, {colors[1].lower()}, and {colors[2].lower()}"
    else:
        color_scheme = "elegant neutral tones"
    
    # Build comprehensive prompt based on reference images
    prompt = f"""Create a professional event entrance design for Nike's Catering Services featuring a {description.lower() if description else event_type.lower()} themed {event_type.lower()} celebration.

VENUE LAYOUT: {style_ref['venue']}

CEILING DESIGN: {style_ref['ceiling']}

ENTRANCE PATHWAY: {style_ref['entrance']} - Adapt this design using {color_scheme} as the primary color palette.

MAIN BACKDROP: {style_ref['backdrop']} - Incorporate {description if description else event_type + ' themed elements'} while maintaining the professional Nike's Catering Services aesthetic.

TABLE ARRANGEMENTS: {style_ref['tables']} - Use {color_scheme} for linens, chair covers, and decorative accents.

CATERING PRESENTATION: {style_ref['catering']}

THEME ADAPTATION: Transform this reference style to reflect a {description if description else event_type} theme while maintaining the sophisticated venue layout, professional table arrangements, and elegant entrance design. The color scheme should be {color_scheme} throughout all elements including draping, table settings, floral arrangements, and decorative accents.

GUEST CAPACITY: Design should accommodate approximately {pax if pax else 50} guests with appropriate spacing and table arrangements.

STYLE REQUIREMENTS: 
- Professional catering service quality
- Elegant entrance with carpet runner or pathway
- Coordinated ceiling treatment and lighting
- Themed backdrop as focal point  
- Matching table linens and chair covers
- Professional food display areas
- Cohesive color coordination throughout
- High-end event photography quality
- Realistic lighting and shadows
- Ultra-detailed and photorealistic"""
    
    return prompt