from fuzzywuzzy import process
from django.conf import settings
from django.core.cache import cache
from PIL import Image
from io import BytesIO
from django.templatetags.static import static

import re
import os
import requests
import cloudinary


# ✅ Moderator Permission Check
def is_moderator(user):
    return user.groups.filter(name='Moderators').exists()


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
    # Use Cloudinary
    themes_public_ids = {
        
        # Disney & Princess Themes
        'mickey': ['mickey1_tjr7h0', 'mickey2_pxslgt', 'mickey3_qiya8u'],
        'frozen': ['frozen1_dk7v5o', 'frozen2_tyo4wh', 'frozen3_juo1gl'],
        'cinderella': ['cinderella1_mmllks', 'cinderalla2_je5abg', 'cinderella3_ryewrw'],
        'snow white': ['snowwhite1_ebjhlv', 'snowwhite2_xoq7wp', 'snowwhite3_qgghb6'],
        'tinkerbell': ['tinkerbell1_wutjm9', 'tinkerbell2_rvusmy', 'tinkerbell3_x1vztm'],
        'princess': ['princess1_ckf2ef', 'princess2_rn0z7q', 'princess3_flsdje'],
        
        # Movie & Animation Themes
        'incredibles': ['incredibles1_j3ecdz', 'incredibles2_t6woik', 'incredibles3_rsnody'],
        'spongebob': ['spongebob1_jygh8a', 'spongebob2_nhnz7r', 'spongebob3_lnksll', 'spongebob4_z3pwmv'],
        'nemo': ['nemo1_fwlhqc', 'nemo2_csahmk', 'nemo3_ffr1bz'],
        'cars': ['cars1_m5dywg', 'cars2_owb6uf', 'cars3_vlbluf'],
        
        # Gaming & Entertainment
        'mario': ['mario1_htowh3', 'mario2_nhrpwo', 'mario3_wxhbpr'],
        'roblox': ['roblox1_g3jscs', 'roblox2_hpso4g', 'roblox3_pkrmmz'],
        'one piece': ['onepiece1_ihxymg', 'onepiece2_kqlelt', 'onepiece3_gixekh'],
        
        # Superhero & Action
        'avengers': ['avengers1_z8kgd7', 'avengers2_kgeegl', 'avengers3_rp9hxm'],
        'transformers': ['transformers1_hpi1nw', 'transformers2_yrvfhz', 'transformers3_jkxnmk'],
        
        # Sports & Vehicles
        'basketball': ['bball1_lzy501', 'bball2_zmutfl', 'bball3_u7hgin'],
        'ferrari': ['ferrari1_gjoxg9', 'ferrari2_bnyapi', 'ferrari3_oqh4xi'],
        
        # Nature & Animals
        'zoo': ['zoo1_lkhguo', 'zoo2_izmxug', 'zoo3_tpivyn'],
        'dinosaur': ['dino1_rgtkxl', 'dino2_i21hjp', 'dino3_emjiim'],
        'bear': ['bear1_h4p6et', 'bear2_bliufl', 'bear3_uyhzr7'],
        'butterfly': ['butterfly1_jnpau7', 'butterfly2_o3gnyl', 'butterfly3_g2eouo'],
        
        # Colors & Styles
        'pink': ['pink1_xpydyr', 'pink2_zws6c6', 'pink3_du7zpo', 'pink4_zg4mno'],
        'green': ['green1_fkl6x9', 'green2_fxbdhw', 'green3_mzeklc'],
        'rainbow': ['rainbow1_pqsbfi', 'rainbow2_be8qcj', 'rainbow3_pf0k0c'],
        
        # Special Themes
        'halloween': ['halloween1_x4onph', 'halloween2_tp5kqb', 'halloween3_xaypho'],
        'wedding': ['wedding1_i4j4ed', 'wedding2_ahxv8y', 'wedding3_ebx0yl'],
        'traditional': ['traditional1_fdjojh', 'traditional2_v0a3un', 'traditional3_e2c2vc'],
        
        # Other Popular Themes
        'barbie': ['barbie1_y2kro4', 'barbie2_adipbp', 'barbie3_wmmwam'],
        'kuromi': ['kuromi1_eoqwpc', 'kuromi2_ielfn3', 'kuromi3_nchbhx'],
        'cocomelon': ['cocolemon1_xvkaxa', 'cocomelon2_x8gwf6', 'cocomelon3_bjw2xa'],
        'pony': ['pony1_rdvceu', 'pony2_u9xona', 'pony3_idj8mn'],
    }

    theme_public_ids = themes_public_ids.get(theme.lower().strip(), [])

    image_urls = [cloudinary.utils.cloudinary_url(public_id, secure=True)[0] for public_id in theme_public_ids]

    return image_urls

CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', 'dzjrdqkiw')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY', '891881498673297')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', 'Z7QaNRs-E_qgvkCByZxev7fwyiU')

# Optional: Configure as default storage for Django's collectstatic
# DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaStorage'
# STATICFILES_STORAGE = 'cloudinary_storage.storage.StaticStorage'

# Configure Cloudinary directly (alternative to CLOUDINARY_URL environment variable)
cloudinary.config(
    cloud_name = CLOUDINARY_CLOUD_NAME,
    api_key = CLOUDINARY_API_KEY,
    api_secret = CLOUDINARY_API_SECRET,
    secure = True # Use HTTPS
)
