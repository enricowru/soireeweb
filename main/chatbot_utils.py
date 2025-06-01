from fuzzywuzzy import process
import re
from django.conf import settings
import os
from django.core.cache import cache
import requests
from PIL import Image
from io import BytesIO
from django.templatetags.static import static

def get_fuzzy_match(query, choices, threshold=80):
    """
    Get the best fuzzy match for a query from a list of choices.
    Returns (match, score) if score >= threshold, else (None, 0)
    """
    result = process.extractOne(query, choices, score_cutoff=threshold)
    return result if result else (None, 0)

def generate_ai_theme_image(theme_name):
    print(f"[DEBUG] generate_ai_theme_image CALLED for: {theme_name}")
    """
    Generate an AI image based on the theme name using DeepAI
    """
    cache_key = f'ai_theme_image_{theme_name.lower()}'
    cached_image = cache.get(cache_key)
    if cached_image:
        print(f"[DEBUG] Returning cached AI image for {theme_name}: {cached_image}")
        return cached_image

    try:
        response = requests.post(
            "https://api.deepai.org/api/text2img",
            data={'text': f"Create a beautiful event decoration theme for {theme_name}, suitable for a party or celebration. The image should be colorful and festive."},
            headers={'api-key': settings.DEEPAI_API_KEY}
        )
        result = response.json()
        print(f"[DEBUG] DeepAI API response: {result}")
        image_url = result.get('output_url')
        if image_url:
            # Download and save the image
            save_dir = os.path.join(settings.BASE_DIR, 'main', 'static', 'main', 'images', 'ai_themes')
            os.makedirs(save_dir, exist_ok=True)
            image_path = os.path.join(save_dir, f'{theme_name.lower().replace(" ", "_")}.jpg')
            img_data = requests.get(image_url).content
            with open(image_path, 'wb') as f:
                f.write(img_data)
            relative_path = f'/static/main/images/ai_themes/{theme_name.lower().replace(" ", "_")}.jpg'
            cache.set(cache_key, relative_path, 60 * 60 * 24)  # Cache for 24 hours
            print(f"[DEBUG] Saved AI image for {theme_name} at {relative_path}")
            return relative_path
        else:
            print(f"[ERROR] No output_url in DeepAI response: {result}")
            return None
    except Exception as e:
        print(f"[ERROR] Exception in generate_ai_theme_image: {e}")
        return None

def wildcard_match(pattern, text):
    """
    Match text using wildcard patterns
    Example: wildcard_match("dis*", "disney") -> True
    """
    pattern = pattern.replace("*", ".*")
    return bool(re.match(pattern, text, re.IGNORECASE))

def get_theme_suggestions(user_input, all_themes):
    """
    Get theme suggestions based on user input using fuzzy matching
    """
    matches = process.extract(user_input, all_themes, limit=3)
    return [match[0] for match in matches if match[1] >= 60]

def enhance_bot_response(response_text, suggestions=None):
    """
    Make bot responses more natural and helpful
    """
    if suggestions:
        response_text += "\n\nDid you mean one of these?\n" + "\n".join(f"- {s}" for s in suggestions)
    return response_text

def get_food_suggestions(user_input, food_items):
    """
    Get food suggestions based on user input using fuzzy matching
    """
    matches = process.extract(user_input, food_items, limit=3)
    return [match[0] for match in matches if match[1] >= 60]

def get_package_suggestions(user_input, packages):
    """
    Get package suggestions based on user input using fuzzy matching
    """
    matches = process.extract(user_input, packages, limit=3)
    return [match[0] for match in matches if match[1] >= 60]

def get_color_suggestions(user_input, colors):
    """
    Get color suggestions based on user input using fuzzy matching
    """
    matches = process.extract(user_input, colors, limit=3)
    return [match[0] for match in matches if match[1] >= 60]

def get_event_type_suggestions(user_input, event_types):
    """
    Get event type suggestions based on user input using fuzzy matching
    """
    matches = process.extract(user_input, event_types, limit=3)
    return [match[0] for match in matches if match[1] >= 60]

def get_combined_suggestions(user_input, choices, threshold=60):
    """
    Get suggestions using both fuzzy matching and wildcard matching
    """
    # Get fuzzy matches
    fuzzy_matches = process.extract(user_input, choices, limit=3)
    fuzzy_suggestions = [match[0] for match in fuzzy_matches if match[1] >= threshold]
    
    # Get wildcard matches
    wildcard_suggestions = []
    for choice in choices:
        if wildcard_match(f"*{user_input}*", choice.lower()):
            wildcard_suggestions.append(choice)
    
    # Combine and deduplicate suggestions
    all_suggestions = list(set(fuzzy_suggestions + wildcard_suggestions))
    return all_suggestions[:3]  # Return top 3 suggestions

def validate_and_suggest(user_input, valid_choices, context="item"):
    """
    Validate user input and provide suggestions if needed
    Returns (is_valid, corrected_input, suggestions)
    """
    # Try exact match first
    if user_input.lower() in [choice.lower() for choice in valid_choices]:
        return True, user_input, []
    
    # Try fuzzy match
    match, score = get_fuzzy_match(user_input, valid_choices)
    if match and score >= 80:
        return True, match, []
    
    # Get suggestions
    suggestions = get_combined_suggestions(user_input, valid_choices)
    return False, None, suggestions

def get_all_theme_images(theme_name):
    """
    Get both regular and AI-generated theme images
    """
    regular_images = get_theme_images(theme_name)
    ai_image = generate_ai_theme_image(theme_name)
    
    if ai_image:
        return regular_images + [ai_image]
    return regular_images

def get_theme_images(theme):
    """Helper function to get images based on theme"""
    themes = {
        # Disney & Princess Themes
        'mickey': [static('main/images/themes/mickey1.jpg'), static('main/images/themes/mickey2.jpg'), static('main/images/themes/mickey3.jpg')],
        'frozen': [static('main/images/themes/frozen1.jpg'), static('main/images/themes/frozen2.jpg'), static('main/images/themes/frozen3.jpg')],
        'cinderella': [static('main/images/themes/cinderella1.jpg'), static('main/images/themes/cinderalla2.jpg'), static('main/images/themes/cinderella3.jpg')],
        'snow white': [static('main/images/themes/snowwhite1.jpg'), static('main/images/themes/snowwhite2.jpg'), static('main/images/themes/snowwhite3.jpg')],
        'tinkerbell': [static('main/images/themes/tinkerbell1.jpg'), static('main/images/themes/tinkerbell2.jpg'), static('main/images/themes/tinkerbell3.jpg')],
        'princess': [static('main/images/themes/princess1.jpg'), static('main/images/themes/princess2.jpg'), static('main/images/themes/princess3.jpg')],
        # Movie & Animation Themes
        'incredibles': [static('main/images/themes/incredibles1.jpg'), static('main/images/themes/incredibles2.jpg'), static('main/images/themes/incredibles3.jpg')],
        'spongebob': [static('main/images/themes/spongebob1.jpg'), static('main/images/themes/spongebob2.jpg'), static('main/images/themes/spongebob3.jpg'), static('main/images/themes/spongebob4.jpg')],
        'nemo': [static('main/images/themes/nemo1.jpg'), static('main/images/themes/nemo2.jpg'), static('main/images/themes/nemo3.jpg')],
        'cars': [static('main/images/themes/cars1.jpg'), static('main/images/themes/cars2.jpg'), static('main/images/themes/cars3.jpg')],
        # Gaming & Entertainment
        'mario': [static('main/images/themes/mario1.jpg'), static('main/images/themes/mario2.jpg'), static('main/images/themes/mario3.jpg')],
        'roblox': [static('main/images/themes/roblox1.jpg'), static('main/images/themes/roblox2.jpg'), static('main/images/themes/roblox3.jpg')],
        'one piece': [static('main/images/themes/onepiece1.jpg'), static('main/images/themes/onepiece2.jpg'), static('main/images/themes/onepiece3.jpg')],
        # Superhero & Action
        'avengers': [static('main/images/themes/avengers1.jpg'), static('main/images/themes/avengers2.jpg'), static('main/images/themes/avengers3.jpg')],
        'transformers': [static('main/images/themes/transformers1.jpg'), static('main/images/themes/transformers2.jpg'), static('main/images/themes/transformers3.jpg')],
        # Sports & Vehicles
        'basketball': [static('main/images/themes/bball1.jpg'), static('main/images/themes/bball2.jpg'), static('main/images/themes/bball3.jpg')],
        'ferrari': [static('main/images/themes/ferrari1.jpg'), static('main/images/themes/ferrari2.jpg'), static('main/images/themes/ferrari3.jpg')],
        # Nature & Animals
        'zoo': [static('main/images/themes/zoo1.jpg'), static('main/images/themes/zoo2.jpg'), static('main/images/themes/zoo3.jpg')],
        'dinosaur': [static('main/images/themes/dino1.jpg'), static('main/images/themes/dino2.jpg'), static('main/images/themes/dino3.jpg')],
        'bear': [static('main/images/themes/bear1.jpg'), static('main/images/themes/bear2.jpg'), static('main/images/themes/bear3.jpg')],
        'butterfly': [static('main/images/themes/butterfly1.jpg'), static('main/images/themes/butterfly2.jpg'), static('main/images/themes/butterfly3.jpg')],
        # Colors & Styles
        'pink': [static('main/images/themes/pink1.jpg'), static('main/images/themes/pink2.jpg'), static('main/images/themes/pink3.jpg'), static('main/images/themes/pink4.jpg')],
        'green': [static('main/images/themes/green1.jpg'), static('main/images/themes/green2.jpg'), static('main/images/themes/green3.jpg')],
        'rainbow': [static('main/images/themes/rainbow1.jpg'), static('main/images/themes/rainbow2.jpg'), static('main/images/themes/rainbow3.jpg')],
        # Special Themes
        'halloween': [static('main/images/themes/halloween1.jpg'), static('main/images/themes/halloween2.jpg'), static('main/images/themes/halloween3.jpg')],
        'wedding': [static('main/images/themes/wedding1.jpg'), static('main/images/themes/wedding2.jpg'), static('main/images/themes/wedding3.jpg')],
        'traditional': [static('main/images/themes/traditional1.jpg'), static('main/images/themes/traditional2.jpg'), static('main/images/themes/traditional3.jpg')],
        # Other Popular Themes
        'barbie': [static('main/images/themes/barbie1.jpg'), static('main/images/themes/barbie2.jpg'), static('main/images/themes/barbie3.jpg')],
        'kuromi': [static('main/images/themes/kuromi1.jpg'), static('main/images/themes/kuromi2.jpg'), static('main/images/themes/kuromi3.jpg')],
        'cocomelon': [static('main/images/themes/cocolemon1.jpg'), static('main/images/themes/cocomelon2.jpg'), static('main/images/themes/cocomelon3.jpg')],
        'pony': [static('main/images/themes/pony1.jpg'), static('main/images/themes/pony2.jpg'), static('main/images/themes/pony3.jpg')],
    }
    return themes.get(theme.lower().strip(), [])