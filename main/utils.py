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
        'mickey': ['https://drive.google.com/uc?export=view&id=1dhdAf0ztwqbJJ_m1dvINkyuSrq0afkOr', 'https://drive.google.com/uc?export=view&id=1eetx4_dwqVvJBs9J4hgOePO31zTAxbpw', 'https://drive.google.com/uc?export=view&id=1NmtHS5Fbso17RfMy8iQqqsFirMqU2gpg'],
        'frozen': ['https://drive.google.com/uc?export=view&id=1SzA3O-Dpp_DJnAYyzVUgI4HH-dsEfZ7G', 'https://drive.google.com/uc?export=view&id=13E-0EnaG6m53O0kDOrFywHgptrnIykoU', 'https://drive.google.com/uc?export=view&id=1XmDYigGKYAk1ShI6ek_0X4ICZTKkroS9'],
        'cinderella': ['https://drive.google.com/uc?export=view&id=11427oy9btqMSkz4_joZ3N-tF3XV-D1Ws', 'https://drive.google.com/uc?export=view&id=1IaRp9n2ZWahIiSs3BZoDjutz6VE_PjF8', 'https://drive.google.com/uc?export=view&id=19jiaXpLCmv2xNqF0Oi2J7AQp3BkMmCS9'],
        'snow white': ['https://drive.google.com/uc?export=view&id=1se2t4kO45UxO62JY8lmbzaKedyhOcTaf', 'https://drive.google.com/uc?export=view&id=1trggQTDOnglh0zAFPIDvego80Xy-sMi4', 'https://drive.google.com/uc?export=view&id=1pjgosC_EA-AdMvo-GlM-7tRw8q9CXkMC'],
        'tinkerbell': ['https://drive.google.com/uc?export=view&id=1WeN76Dz7vnD3DSwESdlYszr8jg6Au9Rr', 'https://drive.google.com/uc?export=view&id=1FGK6Og5AxSSPhoX5djrEPSfQ7edB9whE', 'https://drive.google.com/uc?export=view&id=1E_hS4MX05acvtjAQa_La-IauUiKcC2BG'],
        'princess': ['https://drive.google.com/uc?export=view&id=19Ht3rT8VHTIcIKrftsb6FgU9WrBkOcLn', 'https://drive.google.com/uc?export=view&id=1EMqzqLT-d2l8f-TRtlSymUAcYW__32jG', 'https://drive.google.com/uc?export=view&id=15_q1CWv853Hl4Z56z5OmN8Nu_M8FH4s9'],
        # Movie & Animation Themes
        'incredibles': ['https://drive.google.com/uc?export=view&id=1_OEzdaWNCYrhQhFjlNynkmIHzEcQ4NpL', 'https://drive.google.com/uc?export=view&id=12FW6tmbYLYyT1_lplY8tZkJEDMlzL9EN', 'https://drive.google.com/uc?export=view&id=1MKSPs4GRdIwaCGa3SybnL7Xa5P8dnqoR'],
        'spongebob': ['https://drive.google.com/uc?export=view&id=11mFVUtmr8FFHhVhMqpk435BCPotr1l0K', 'https://drive.google.com/uc?export=view&id=1-dr_QJ7oplmydPUYFjCiNpF-pdiHOKcK', 'https://drive.google.com/uc?export=view&id=1-IxCqn3t2rl2FuxYJVBKf9YoxWqjA_B8', 'https://drive.google.com/uc?export=view&id=1ftm_MMj8a--liDM3kgFZ34xaZ-pXhJ4n'],
        'nemo': ['https://drive.google.com/uc?export=view&id=18QsWaJC0Pn7pHWMwRjS5L2QmN1QFPtOh', 'https://drive.google.com/uc?export=view&id=1Hky-DKlwqv4dMEbDMmVjkZ7thTEIWt4G', 'https://drive.google.com/uc?export=view&id=132ApVHciz3qkRCDzX0Jcb9SHJ1MEBGwn'],
        'cars': ['https://drive.google.com/uc?export=view&id=1Wd_z4XCG1qU6Pz9tzYLNfPlxtcUlxyC9', 'https://drive.google.com/uc?export=view&id=1KJ5UvyDzsLJ-oMDSC59b5VoUQWTcV82x', 'https://drive.google.com/uc?export=view&id=1RTvslZGJui084JyKwAEXIhFEaCLEY7lG'],
        # Gaming & Entertainment
        'mario': ['https://drive.google.com/uc?export=view&id=1g2deztjMFVD8k9DJzz4ScJq0ib9NqxKE', 'https://drive.google.com/uc?export=view&id=1nSvX6En9Vu263JiVMXp0NOAZtqh3iHSV', 'https://drive.google.com/uc?export=view&id=1VafctPCR99iXswof3ZiosXaECKEXe1c0'],
        'roblox': ['https://drive.google.com/uc?export=view&id=14-X_S4h1McyFBQNfIzQ3tracxItLEMj4', 'https://drive.google.com/uc?export=view&id=1TnAjZwGyP5MhmiT8YhhaG7Vs-YTMdwo2', 'https://drive.google.com/uc?export=view&id=1GrvnOHUhnTPEb_l7Mo0BSA5Q1FAHeP30'],
        'one piece': ['https://drive.google.com/uc?export=view&id=1ZAtu9-BEwaJ45seXSMEtZbLgZe7wCpfB', 'https://drive.google.com/uc?export=view&id=1yZWmrf2bAvP40QR2cOCwAlStl7AaCurR', 'https://drive.google.com/uc?export=view&id=1Yz4TjJ_ODtKlZfA-RToBnVKZAxx_upgN'],
        # Superhero & Action
        'avengers': ['https://drive.google.com/uc?export=view&id=1x1H4lfiHCS9gujCTINritStf1em4cpIL', 'https://drive.google.com/uc?export=view&id=1ykdtjFQrqHsqriZlZwijqLld-fc3SovO', 'https://drive.google.com/uc?export=view&id=1HQwupeAc8-uxOT-kZWheJIPJ1fKqzqf8'],
        'transformers': ['https://drive.google.com/uc?export=view&id=1lWXXqfQ93-VZyu4T5qDU9kWO6Uhi-pS2', 'https://drive.google.com/uc?export=view&id=1O56IZiuGosc8nTVWa0gtzSpBCQq9_EKJ', 'https://drive.google.com/uc?export=view&id=19RB2Gj0RXQhrLJjCl9s1eqzrneJvOsyP'],
        # Sports & Vehicles
        'basketball': ['https://drive.google.com/uc?export=view&id=1PM6_dQp16rLnQtbeS0qP74OLFUY09j4C', 'https://drive.google.com/uc?export=view&id=1y1rMVxungHVGRH8b5DdWFaD8CW7iDxE0', 'https://drive.google.com/uc?export=view&id=1NCLGKJ8QHTrvFRsAF3Lu-9oQ0izHcP6N'],
        'ferrari': ['https://drive.google.com/uc?export=view&id=14pHChbvHjrG7pVrYuoiF8orOWtvr0b-f', 'https://drive.google.com/uc?export=view&id=1TjfHVkODw1KiaECD3ds70sbBkXEN5mfq', 'https://drive.google.com/uc?export=view&id=1XVvWdrI8Xbk6oU2iEPoJMSFTeIFvsQwa'],
        # Nature & Animals
        'zoo': ['https://drive.google.com/uc?export=view&id=1GMrc1myk7hMC0Xy2UVINxyFz6OPN2j1m', 'https://drive.google.com/uc?export=view&id=1KGSrVIxxeLT-_LzlA0yZqz4ffFdQX2uz', 'https://drive.google.com/uc?export=view&id=1GLlNO9HhfUnmQstz6BoVGMirk5__fNMj'],
        'dinosaur': ['https://drive.google.com/uc?export=view&id=107l1t3L1qN6tfhWJzCSIyPWs5cJU_169', 'https://drive.google.com/uc?export=view&id=1xrGu4Avwrhgrk8B8KtaUhKqgSBSeK6GU', 'https://drive.google.com/uc?export=view&id=18hhAof80JzQDhCt_lkmTNNRpfL9mI8S9'],
        'bear': ['https://drive.google.com/uc?export=view&id=1yd6j8cTVMok4zWAbtSGpO-IiXPUbqD7j', 'https://drive.google.com/uc?export=view&id=18TdB1oahUnAgs1_34hhQ2Pbh60Lxw34E', 'https://drive.google.com/uc?export=view&id=1F3IPCQTSdrwHi-RPJTZDAU6vCf_vSdVG'],
        'butterfly': ['https://drive.google.com/uc?export=view&id=1OcKpW2MQJuFJRm1G7Goo69XxAbyI2LQR', 'https://drive.google.com/uc?export=view&id=1O0C_v3IrBMyzmmoUZH35ozzSOwSpcMAM', 'https://drive.google.com/uc?export=view&id=1R2rgNL9Saf_MBnLV32mLCI-1bz23FyK3'],
        # Colors & Styles
        'pink': ['https://drive.google.com/uc?export=view&id=1qHxE-rVD9rXkeTFz-p-brhGblwzQ2HDM', 'https://drive.google.com/uc?export=view&id=19cJtYM6bRMK5rzC-F-za7_DE1jY4F56o', 'https://drive.google.com/uc?export=view&id=1WY24TKweSXq_lFd9xIA4k8pjrF5JK_12', 'https://drive.google.com/uc?export=view&id=1lhFhY7hVDt1oRfZODU1sZsjZv62KXbSs'],
        'green': ['https://drive.google.com/uc?export=view&id=1On07tStA7vhArHJ256iWciV2308rSGW_', 'https://drive.google.com/uc?export=view&id=1gtIVwpxK0ynfLF3P1y20Mptrz1O7dZvO', 'https://drive.google.com/uc?export=view&id=1b9XDzoZGiMDwkbZ0MZ16bWcKwDc76uxD'],
        'rainbow': ['https://drive.google.com/uc?export=view&id=1V9a_nYpZu2WpjK4G7zXCU-FGjQxX-_NR', 'https://drive.google.com/uc?export=view&id=10fsShHr2cBK03QQ4iUCqKCI4HJlQ6jo3', 'https://drive.google.com/uc?export=view&id=1tlpkr73HtKFHBOI10hM53aSs1IufkwrD'],
        # Special Themes
        'halloween': ['https://drive.google.com/uc?export=view&id=1_kF3DjwPT5fVqpwoQsfNpzSwUQoMX_sh', 'https://drive.google.com/uc?export=view&id=12TQHS6NHhHTTGeAs-iJBOpbP--SI3URo', 'https://drive.google.com/uc?export=view&id=1ZLJ57QFXOf135fb1twEFTrNsWBReA3aJ'],
        'wedding': ['https://drive.google.com/uc?export=view&id=1P326W7m_Ebhberok8i3ryNB3abZBU5oC', 'https://drive.google.com/uc?export=view&id=1QBbrtgPyF3RI4YVnJ8DYFwFw4HKnw4f_', 'https://drive.google.com/uc?export=view&id=1oTYVV7uBCoeVBZ1CY56kkrFvErh7dPmu'],
        'traditional': ['https://drive.google.com/uc?export=view&id=18n2D128-UCjOH_VN1jN8TUq2s4j2ttrN', 'https://drive.google.com/uc?export=view&id=1s-P3EjJkbjRhPX90UfNyWYUBGN9O57QR', 'https://drive.google.com/uc?export=view&id=1f_juko83Y2H5RJj6SbrI_GUUDtKtF4EF'],
        # Other Popular Themes
        'barbie': ['https://drive.google.com/uc?export=view&id=1gV8HjfPiudDXsvmlDrkHNr9v9GhGk9YF', 'https://drive.google.com/uc?export=view&id=18Uph-YVMvttV8NkxrZKPzpJ-lDTYrW1x', 'https://drive.google.com/uc?export=view&id=1iPJqFkoFu4Yr12FlwdLx09au8tchYjuW'],
        'kuromi': ['https://drive.google.com/uc?export=view&id=1FojdkqjxeIJ48Oizo_i-VLVg5Kc-mt85', 'https://drive.google.com/uc?export=view&id=1LJcmdWWgO_oWlt6PGHPnMMCOjfJUNggK', 'https://drive.google.com/uc?export=view&id=1whqqvRj50QDnc7d9asDYsBWaReBrGpSf'],
        'cocomelon': ['https://drive.google.com/uc?export=view&id=1QCMLBwmlEaygJ_fdLufzIr8nQWVcbqe1', 'https://drive.google.com/uc?export=view&id=1i1W7SOPME6Sf4jyA3vb-wOW38X89i_ft', 'https://drive.google.com/uc?export=view&id=1rw4vCw0lfneqqNR_EPwCnX240d8elqRR'],
        'pony': ['https://drive.google.com/uc?export=view&id=1YZ_xEc2AjgIpCkpw_35Je6RAFNHYcKel', 'https://drive.google.com/uc?export=view&id=13zlS-cD047oommzheqHgjG8SevfGa_67', 'https://drive.google.com/uc?export=view&id=1ol1ZoHZ5cRZd2xFxl3LhQ2LoCTkna8Vk'],
    }
    return themes.get(theme.lower().strip(), [])