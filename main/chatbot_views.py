import re
from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static
from django.http import JsonResponse
from .models import ChatSession
import json
import os
from django.conf import settings
from .utils import (
    get_fuzzy_match, 
    generate_ai_theme_image, 
    wildcard_match,
    get_theme_suggestions,
    enhance_bot_response,
    get_all_theme_images,
    get_theme_images,
    get_food_suggestions,
    get_package_suggestions,
    get_color_suggestions,
    get_event_type_suggestions,
    get_combined_suggestions,
    validate_and_suggest,
    get_all_dishes_for_selection,
    get_food_menu,
    get_food_categories
)
from fuzzywuzzy  import process
from django.contrib.staticfiles.storage import staticfiles_storage
import cloudinary.utils
from datetime import datetime


def get_all_categories():
    return [
        'disney', 'movie', 'gaming', 'superhero', 'sports', 'animal', 'color', 'special', 'other'
    ]

def get_category_themes(category):
    """Helper function to get themes by category"""
    categories = {
        'disney': ['mickey', 'frozen', 'cinderella', 'snow white', 'tinkerbell', 'princess'],
        'movie': ['incredibles', 'spongebob', 'nemo', 'cars'],
        'gaming': ['mario', 'roblox', 'one piece'],
        'superhero': ['avengers', 'transformers'],
        'sports': ['basketball', 'ferrari'],
        'animal': ['zoo', 'dinosaur', 'bear', 'butterfly'],
        'color': ['pink', 'green', 'rainbow'],
        'special': ['halloween', 'wedding', 'traditional'],
        'other': ['barbie', 'kuromi', 'cocomelon', 'pony']
    }
    return categories.get(category.lower().strip(), [])

def get_category_response(category):
    """Helper function to get specific category responses"""
    responses = {
        'disney': "For Disney themes, we have Mickey Mouse, Frozen, Cinderella, Snow White, Tinkerbell, and Princess themes. Which one would you like to see?",
        'movie': "For Movie themes, we have Incredibles, SpongeBob, Finding Nemo, and Cars themes. Which one interests you?",
        'gaming': "For Gaming themes, we have Mario, Roblox, and One Piece themes. Which one would you like to explore?",
        'superhero': "For Superhero themes, we have Avengers and Transformers themes. Which one would you like to see?",
        'sports': "For Sports themes, we have Basketball and Ferrari Racing themes. Which one interests you?",
        'animal': "For Animal themes, we have Zoo, Dinosaurs, Bears, and Butterflies themes. Which one would you like to see?",
        'color': "For Color themes, we have Pink, Green, and Rainbow themes. Which one interests you?",
        'special': "For Special themes, we have Halloween, Wedding, and Traditional themes. Which one would you like to explore?",
        'other': "For Other themes, we have Barbie, Kuromi, Cocomelon, and My Little Pony themes. Which one would you like to see?"
    }
    return responses.get(category.lower(), "I couldn't find that category. Would you like to see our available categories?")

def get_event_packages(event_type):
    """Helper function to get packages based on event type"""
    packages = {
        'birthday': [
            ('100 pax - Package A', static('main/images/packages/birthday_a.jpg')),
            ('200 pax - Package B', static('main/images/packages/birthday_b.jpg')),
            ('300 pax - Package C', static('main/images/packages/birthday_c.jpg'))
        ],
        'kiddie': [
            ('50 pax - Package A', static('main/images/packages/kiddie_a.jpg')),
            ('100 pax - Package B', static('main/images/packages/kiddie_b.jpg')),
            ('150 pax - Package C', static('main/images/packages/kiddie_c.jpg'))
        ],
        'wedding': [
            ('200 pax - Package A', static('main/images/packages/wedding_a.jpg')),
            ('300 pax - Package B', static('main/images/packages/wedding_b.jpg')),
            ('400 pax - Package C', static('main/images/packages/wedding_c.jpg'))
        ],
        'christening': [
            ('100 pax - Package A', static('main/images/packages/christening_a.jpg')),
            ('150 pax - Package B', static('main/images/packages/christening_b.jpg')),
            ('200 pax - Package C', static('main/images/packages/christening_c.jpg'))
        ]
    }
    return packages.get(event_type.lower(), [])

def get_themes_and_images(category):
    themes = get_category_themes(category)
    images = []
    image_labels = []
    for theme in themes:
        theme_imgs = get_theme_images(theme)
        if theme_imgs:
            images.append(theme_imgs[0])
            image_labels.append(theme.title())
    return themes, images, image_labels

def get_category_description(category):
    desc = {
        'disney': 'For Disney themes, we have: Mickey, Frozen, Cinderella, Snow White, Tinkerbell, Princess.',
        'movie': 'For Movie themes, we have: Incredibles, Spongebob, Nemo, Cars.',
        'gaming': 'For Gaming themes, we have: Mario, Roblox, One Piece.',
        'superhero': 'For Superhero themes, we have: Avengers, Transformers.',
        'sports': 'For Sports themes, we have: Basketball, Ferrari.',
        'animal': 'For Animal themes, we have: Zoo, Dinosaur, Bear, Butterfly.',
        'color': 'For Color themes, we have: Pink, Green, Rainbow.',
        'special': 'For Special themes, we have: Halloween, Wedding, Traditional.',
        'other': 'For Other themes, we have: Barbie, Kuromi, Cocomelon, Pony.'
    }
    return desc.get(category, '')

def get_event_package_images(event_type):
    """Dynamically get all package images for the event type from the static directory."""
    # Assuming package images are uploaded to Cloudinary with public IDs matching their filenames (without extension)
    package_public_ids = {
        'kiddie': ['kiddie_170pax_irkxsg', 'kiddie_80pax_twgrmz', 'kiddie_160pax_b5ezdz', 'kiddie_150pax_m7cdrz', 'kiddie_70pax_hdawxz', 'kiddie_50pax_dpgjez', 'kiddie_100pax_z1jsn0', 'kiddie_130pax_yeyoka', 'kiddie_120pax_soflwe', 'kiddie_180pax_knwwyp', 'kiddie_200pax_kmpgn4'],
        'birthday': ['birthday_120pax_r25otc', 'birthday_130pax_hz5unq', 'birthday_150pax_gtqtim', 'birthday_100pax_zheug3', 'birthday_170pax_jtbtam', 'birthday_160pax_b3ecp4', 'birthday_80pax_vvu9g2', 'birthday_70pax_vew5ay', 'birthday_50pax_yjwdwl', 'birthday_200pax_gcjprl', 'birthday_180_pax_hircrw'], # Add actual birthday package public IDs here
        'wedding': ['wedding_250pax_haxcqu', 'wedding_70pax_swgj6f', 'wedding_120pax_cnd4mj', 'wedding_150pax_ftvdmh', 'wedding_200pax_dsdfrl', 'wedding_60pax_wjrahh', 'wedding_80pax_y7az0i', 'wedding_180pax_aotyby', 'wedding_50pax_akotgi', 'wedding_160pax_twyve5', 'wedding_170pax_wb3mcl', 'wedding_130pax_eamuys', 'wedding_100pax_mtujpw'], # Add actual wedding package public IDs here
        'christening': ['christening_70pax_cyznmy', 'christening_150pax_idheaa', 'christening_80pax_slf4sl', 'christening_200pax_t3vuye','christening_50pax_nxh9ke', 'christening_100pax_insvxv', 'christening_120pax_ua9yie'], # Add actual christening package public IDs here
    }
    prefix = event_type.lower()
    public_ids = package_public_ids.get(prefix, [])
    
    images = []
    for public_id in public_ids:
         # Generate Cloudinary URL
         image_url = cloudinary.utils.cloudinary_url(public_id, secure=True)[0]
         # Extract package name from public ID (remove 6-character suffix if present)
         parts = public_id.split('_')
         if len(parts) > 1 and len(parts[-1]) == 6 and parts[-1].isalnum():
             # Assume the last part is a 6-character suffix and remove it if it's alphanumeric
             descriptive_id = '_'.join(parts[:-1])
         else:
             descriptive_id = public_id

         package_name = descriptive_id.replace('_', ' ').title()
         images.append((package_name, image_url))
         
    images.sort() # Optional: sort by name
    return images

# Package rules for all event types
PACKAGE_RULES = {
    'A': {'dishes': 3, 'pasta': 1, 'drinks': 1, 'rice': True, 'dessert': True},
    'B': {'dishes': 4, 'pasta': 1, 'drinks': 1, 'rice': True, 'dessert': True},
    'C': {'dishes': 5, 'pasta': 1, 'drinks': 1, 'rice': True, 'dessert': True},
}

def get_pax_options(event_type):
    """Helper function to get pax options based on event type"""
    pax_options = {
        'kiddie party': [50, 70, 80, 100, 120, 130, 150, 160, 170, 180, 200],
        'birthday party': [50, 70, 80, 100, 120, 130, 150, 160, 170, 180, 200],
        'wedding': [50, 60, 70, 80, 100, 120, 130, 150, 160 , 170, 180, 200, 250],
        'christening': [50, 70, 80, 100, 120, 150, 200]
    }
    # Return list of strings with 'pax' appended
    return [f'{pax}pax' for pax in pax_options.get(event_type.lower(), [])]

def get_food_menu_images():
    """Return all food menu images for display from Cloudinary.
    Assuming food menu images are uploaded to Cloudinary with specific public IDs.
    """
    # Replace with your actual Cloudinary public IDs for food menu images
    food_menu_public_ids = [
        'FoodMenu1_llri2i',
        'FoodMenu2_cmzxrt',
    ]

    image_urls = []
    for public_id in food_menu_public_ids:
        # Generate Cloudinary URL
        image_url = cloudinary.utils.cloudinary_url(public_id, secure=True)[0]
        image_urls.append(image_url)

    return image_urls

def chatbot_view(request):
    # Initialize session if needed
    if not request.session.get('initialized', False):
        request.session['chat_history'] = [
            {'sender': 'bot', 'text': "Hey there! I'm Patrice – your go-to buddy for planning awesome events.\nWhether it's something big, small, or totally extra, I've got your back.\n\nSo, what date are we looking at for your event?", 'show_date_input': True}
        ]
        request.session['planner_state'] = 'date_input'
        request.session['planner_data'] = {}
        request.session['initialized'] = True
        request.session.modified = True

    chat_history = request.session.get('chat_history', [])
    planner_state = request.session.get('planner_state', 'date_input')
    planner_data = request.session.get('planner_data', {})
    bot_response = None

    if request.method == 'POST':
        user_message = request.POST.get('message')
        chat_history.append({'sender': 'user', 'text': user_message})

        # Handle input validation first
        if planner_state == 'date_input':
            is_valid, error_msg, corrected_value = validate_input('date', user_message)
            if is_valid:
                planner_data['event_date'] = corrected_value
                bot_response = {
                    'sender': 'bot',
                    'text': "Great! Now, what type of event would you like to plan?",
                    'show_event_buttons': True
                }
                planner_state = 'event_type'
            else:
                bot_response = {
                    'sender': 'bot',
                    'text': error_msg,
                    'show_date_input': True
                }

        elif planner_state == 'event_type':
            is_valid, error_msg, corrected_value = validate_input('event_type', user_message)
            if is_valid:
                planner_data['event_type'] = corrected_value
                planner_data['is_custom_event'] = corrected_value not in ['kiddie party', 'birthday party', 'wedding', 'christening']
                bot_response = {
                    'sender': 'bot',
                    'text': "Great! Now, please tell me the number of guests (pax) for your event.",
                    'show_pax_input': True,
                    'pax_options': get_pax_options(corrected_value.lower())
                }
                planner_state = 'number_of_pax'
            else:
                bot_response = {
                    'sender': 'bot',
                    'text': error_msg,
                    'show_event_buttons': True
                }

        elif planner_state == 'number_of_pax':
            try:
                # Handle both dropdown selection and custom input
                if user_message.startswith('--Select'):
                    raise ValueError("Please select a valid number of guests")
                
                pax_str = user_message.strip().lower().replace('pax', '').strip()
                num_pax = int(pax_str)
                event_type = planner_data.get('event_type', '').lower()
                valid_pax_options = [int(p.replace('pax', '')) for p in get_pax_options(event_type)]
                
                if num_pax in valid_pax_options:
                    planner_data['number_of_pax'] = num_pax
                    
                    # Map event type to base key for package lookup
                    event_type_raw = planner_data.get('event_type', '').lower()
                    event_type_map = {
                        'kiddie party': 'kiddie',
                        'birthday party': 'birthday',
                        'wedding': 'wedding',
                        'christening': 'christening',
                    }
                    event_type_key = event_type_map.get(event_type_raw, event_type_raw)
                    
                    # Attempt to preselect a package image for later display based on pax
                    expected_id_pattern = f"{event_type_key}_{num_pax}pax".lower()
                    all_public_ids = sum([ids for ids in [
                        ['kiddie_170pax_irkxsg', 'kiddie_80pax_twgrmz', 'kiddie_160pax_b5ezdz', 'kiddie_150pax_m7cdrz', 'kiddie_70pax_hdawxz', 'kiddie_50pax_dpgjez', 'kiddie_100pax_z1jsn0', 'kiddie_130pax_yeyoka', 'kiddie_120pax_soflwe', 'kiddie_180pax_knwwyp', 'kiddie_200pax_kmpgn4'],
                        ['birthday_120pax_r25otc', 'birthday_130pax_hz5unq', 'birthday_150pax_gtqtim', 'birthday_100pax_zheug3', 'birthday_170pax_jtbtam', 'birthday_160pax_b3ecp4', 'birthday_80pax_vvu9g2', 'birthday_70pax_vew5ay', 'birthday_50pax_yjwdwl', 'birthday_200pax_gcjprl', 'birthday_180_pax_hircrw'],
                        ['wedding_250pax_haxcqu', 'wedding_70pax_swgj6f', 'wedding_120pax_cnd4mj', 'wedding_150pax_ftvdmh', 'wedding_200pax_dsdfrl', 'wedding_60pax_wjrahh', 'wedding_80pax_y7az0i', 'wedding_180pax_aotyby', 'wedding_50pax_akotgi', 'wedding_160pax_twyve5', 'wedding_170pax_wb3mcl', 'wedding_130pax_eamuys', 'wedding_100pax_mtujpw'],
                        ['christening_70pax_cyznmy', 'christening_150pax_idheaa', 'christening_80pax_slf4sl', 'christening_200pax_t3vuye', 'christening_50pax_nxh9ke', 'christening_100pax_insvxv', 'christening_120pax_ua9yie']
                    ]], [])
                    found_public_id = next((pid for pid in all_public_ids if pid.lower().startswith(expected_id_pattern)), None)
                    if found_public_id:
                        package_image_url = cloudinary.utils.cloudinary_url(found_public_id, secure=True)[0]
                        descriptive_id = '_'.join(found_public_id.split('_')[:-1]) if len(found_public_id.split('_')[-1]) == 6 else found_public_id
                        planner_data['package_image'] = package_image_url
                        planner_data['package_image_label'] = descriptive_id.replace('_', ' ').title()

                    # Move to venue selection
                    bot_response = {
                        'sender': 'bot',
                        'text': "Great! Now, please provide the venue or location for your event.",
                        'show_venue_input': True
                    }
                    planner_state = 'venue_location'
                else:
                    bot_response = {
                        'sender': 'bot',
                        'text': f"For {planner_data.get('event_type', '').title()} events, we have options for {min(valid_pax_options)} to {max(valid_pax_options)} guests. Please select from the available options.",
                        'show_pax_input': True,
                        'pax_options': get_pax_options(event_type)
                    }
            except ValueError:
                event_type = planner_data.get('event_type', '').lower()
                bot_response = {
                    'sender': 'bot',
                    'text': "Please select a valid number of guests from the dropdown or enter a custom number.",
                    'show_pax_input': True,
                    'pax_options': get_pax_options(event_type)
                }

        elif planner_state == 'venue_location':
            is_valid, error_msg, corrected_value = validate_input('venue', user_message)
            if is_valid:
                planner_data['venue_location'] = corrected_value
                # Ask for color palette next
                color_suggestions = ['pastel', 'vibrant', 'neutral', 'earth tones', 'black & white']
                suggestions_text = ', '.join(color_suggestions)
                bot_response = {
                    'sender': 'bot',
                    'text': f"Great! What color palette would you like for your event? Here are some ideas: {suggestions_text}. Type 'default' to skip or specify your own.",
                }
                planner_state = 'color_palette'
            else:
                bot_response = {
                    'sender': 'bot',
                    'text': error_msg,
                    'show_venue_input': True
                }

        elif planner_state == 'color_palette':
            # Accept any non-empty input as color palette, with optional suggestion validation
            is_valid, error_msg, corrected_value = validate_input('color_palette', user_message)
            if is_valid:
                planner_data['color_palette'] = corrected_value

                theme_categories = get_all_categories()
                category_bullets = '<ul>' + ''.join([f'<li>{cat}</li>' for cat in theme_categories]) + '</ul>'
                bot_response = {
                    'sender': 'bot',
                    'text': f"Great! Now, let's choose a theme for your event. Please select a category:{category_bullets}",
                    'show_theme_category_buttons': True,
                    'theme_category_options': theme_categories
                }
                planner_state = 'theme_choice'
            else:
                bot_response = {
                    'sender': 'bot',
                    'text': error_msg or "Please enter a valid color palette.",
                }

        elif planner_state == 'theme_choice':
            is_valid, error_msg, corrected_value = validate_input('theme_category', user_message)
            if is_valid:
                themes = get_category_themes(corrected_value)
                theme_options = [(theme.title(), get_theme_images(theme)[0] if get_theme_images(theme) else None) for theme in themes]
                bot_response = {
                    'sender': 'bot',
                    'text': f"Great choice! Here are the available themes for {corrected_value}. Please select one:",
                    'show_theme_buttons': True,
                    'theme_options': theme_options
                }
                planner_state = 'theme_select'
                planner_data['current_category'] = corrected_value
            else:
                bot_response = {
                    'sender': 'bot',
                    'text': error_msg,
                    'show_theme_category_buttons': True,
                    'theme_category_options': get_all_categories()
                }

        elif planner_state == 'theme_select':
            # Expect the user_message to be one of the themes under current_category
            current_cat = planner_data.get('current_category')
            themes = get_category_themes(current_cat)
            if user_message.lower() in [t.lower() for t in themes]:
                selected_theme = next(t for t in themes if t.lower() == user_message.lower())
                planner_data['theme'] = selected_theme
                planner_data['theme_images'] = get_theme_images(selected_theme)

                bot_response = {
                    'sender': 'bot',
                    'text': "Do you like this theme?",
                    'show_theme_confirmation': True,
                    'theme_confirm_images': planner_data['theme_images'],
                    'theme_confirm_name': selected_theme.title()
                }
                planner_state = 'theme_confirmation'
            else:
                # Prompt again
                theme_options = [(theme.title(), get_theme_images(theme)[0] if get_theme_images(theme) else None) for theme in themes]
                bot_response = {
                    'sender': 'bot',
                    'text': "Please select a valid theme from the options:",
                    'show_theme_buttons': True,
                    'theme_options': theme_options
                }

        elif planner_state == 'theme_confirmation':
            if user_message.lower() in ['yes', 'y']:
                if planner_data.get('is_custom_event', False):
                    food_menu_images = get_food_menu_images()
                    bot_response = {
                        'sender': 'bot',
                        'text': "Great! Now let's look at the food menu. Please review the options and press OK when you are ready to make your selections.",
                        'images': food_menu_images,
                        'show_food_menu_section': True
                    }
                    planner_state = 'food_menu_review'
                else:
                    # Show package options based on event type and pax
                    # Map event type to base key for package lookup
                    event_type_raw = planner_data.get('event_type', '').lower()
                    event_type_map = {
                        'kiddie party': 'kiddie',
                        'birthday party': 'birthday',
                        'wedding': 'wedding',
                        'christening': 'christening',
                    }
                    event_type_key = event_type_map.get(event_type_raw, event_type_raw)
                    num_pax = planner_data.get('number_of_pax')
                    package_images = get_event_package_images(event_type_key)
                    if package_images:
                        planner_data['package_images'] = package_images

                        # Select image whose pax exactly matches the chosen number
                        def extract_pax(label):
                            m = re.search(r'(\d+)\s*Pax', label, re.IGNORECASE)
                            return int(m.group(1)) if m else None

                        exact_match_images = [img for img in package_images if extract_pax(img[0]) == num_pax]
                        selected_image = exact_match_images[0] if exact_match_images else package_images[0]
                        selected_label, selected_url = selected_image

                        bot_response = {
                            'sender': 'bot',
                            'text': f"You selected: {selected_label}",
                            'package_image_selected': selected_url,
                            'package_image_label': selected_label
                        }
                        planner_state = 'package_letter_choice'
                    else:
                        # Fallback to food menu if no package images
                        food_menu_images = get_food_menu_images()
                        bot_response = {
                            'sender': 'bot',
                            'text': "Let's look at the food menu. Please review the options and press OK when you are ready to make your selections.",
                            'images': food_menu_images,
                            'show_food_menu_section': True
                        }
                        planner_state = 'food_menu_review'
            elif user_message.lower() in ['no', 'n']:
                theme_categories = get_all_categories()
                category_bullets = '<ul>' + ''.join([f'<li>{cat}</li>' for cat in theme_categories]) + '</ul>'
                bot_response = {
                    'sender': 'bot',
                    'text': f"No problem! Let's try another theme. What type of theme are you interested in?{category_bullets}",
                    'show_theme_category_buttons': True,
                    'theme_category_options': theme_categories
                }
                planner_state = 'theme_choice'
            else:
                bot_response = {
                    'sender': 'bot',
                    'text': "Please respond with 'yes' or 'no'. Do you like this theme?",
                    'show_theme_confirmation': True,
                    'theme_confirm_images': planner_data.get('theme_images', []),
                    'theme_confirm_name': planner_data.get('theme', '').title()
                }

        elif planner_state == 'package_letter_choice':
            is_valid, error_msg, corrected_value = validate_input('package_letter', user_message)
            if is_valid:
                planner_data['package_letter'] = corrected_value
                planner_data['package_choice'] = f"{planner_data.get('package_image_label', '')} - Package {corrected_value}"
                
                food_menu_images = get_food_menu_images()
                # Use default rules if no package_letter (custom events)
                rules = PACKAGE_RULES.get(corrected_value, {'dishes': 3, 'pasta': 1, 'drinks': 1, 'rice': True, 'dessert': True})
                rules_text = f"Based on Package {corrected_value}, here are the food selection rules:\n\nYou can choose:\n<ul><li>{rules['dishes']} dishes</li><li>{rules['pasta']} pasta</li><li>{rules['drinks']} drink</li></ul>\nPlease note that Steamed Rice and Dessert Buffet are already included.\n\nReview the menu and press OK when you are ready to make your selections."
                
                bot_response = {
                    'sender': 'bot',
                    'text': rules_text,
                    'images': food_menu_images,
                    'show_food_menu_section': True
                }
                planner_state = 'food_menu_review'
            else:
                bot_response = {
                    'sender': 'bot',
                    'text': error_msg,
                    'show_package_buttons': True,
                    'package_images': planner_data.get('package_images', [])
                }

        elif planner_state == 'food_menu_review':
            if user_message.lower() in ['ok', 'ready', 'done', 'go']:
                package_letter = planner_data.get('package_letter')
                # Use default rules if no package_letter (custom events)
                rules = PACKAGE_RULES.get(package_letter, {'dishes': 3, 'pasta': 1, 'drinks': 1, 'rice': True, 'dessert': True})
                bot_response = {
                    'sender': 'bot',
                    'text': f"Please select {rules['dishes']} dishes:",
                    'show_dish_buttons': True,
                    'dish_options': get_all_dishes_for_selection(),
                    'planner_data': planner_data
                }
                planner_data['food_selection'] = {'dishes': [], 'pasta': [], 'drinks': []}
                planner_state = 'food_select_dishes'
            else:
                food_menu_images = get_food_menu_images()
                bot_response = {
                    'sender': 'bot',
                    'text': 'Please review the food menu and press OK when you are ready.',
                    'images': food_menu_images,
                    'show_food_menu_section': True
                }

        elif planner_state == 'food_select_dishes':
            selected_dishes = [d.strip() for d in user_message.split(',') if d.strip()]
            package_letter = planner_data.get('package_letter')
            # Use default rules if no package_letter (custom events)
            rules = PACKAGE_RULES.get(package_letter, {'dishes': 3, 'pasta': 1, 'drinks': 1, 'rice': True, 'dessert': True})
            
            all_valid = True
            corrected_dishes = []
            error_msgs = []
            
            for dish in selected_dishes:
                is_valid, error_msg, corrected_value = validate_input('dish', dish, context={'all_dishes': get_all_dishes_for_selection()})
                if is_valid:
                    corrected_dishes.append(corrected_value)
                else:
                    all_valid = False
                    error_msgs.append(f"'{dish}': {error_msg}")
            
            if all_valid and len(corrected_dishes) == rules['dishes']:
                planner_data['food_selection']['dishes'] = corrected_dishes
                bot_response = {
                    'sender': 'bot',
                    'text': f"Please select {rules['pasta']} pasta:",
                    'show_pasta_buttons': True,
                    'pasta_options': get_food_menu('pasta')
                }
                planner_state = 'food_select_pasta'
            else:
                error_text = f"Please select exactly {rules['dishes']} valid dishes."
                if error_msgs:
                    error_text += "\nIssues found:\n" + "\n".join(error_msgs)
                bot_response = {
                    'sender': 'bot',
                    'text': error_text,
                    'show_dish_buttons': True,
                    'dish_options': get_all_dishes_for_selection(),
                    'planner_data': planner_data
                }

        elif planner_state == 'food_select_pasta':
            selected_pasta = user_message.strip()
            package_letter = planner_data.get('package_letter')
            # Use default rules if no package_letter (custom events)
            rules = PACKAGE_RULES.get(package_letter, {'dishes': 3, 'pasta': 1, 'drinks': 1, 'rice': True, 'dessert': True})
            
            is_valid, error_msg, corrected_value = validate_input('pasta', selected_pasta, context={'pasta_options': get_food_menu('pasta')})
            if is_valid:
                planner_data['food_selection']['pasta'] = [corrected_value]
                bot_response = {
                    'sender': 'bot',
                    'text': f"Please select {rules['drinks']} drink:",
                    'show_drink_buttons': True,
                    'drink_options': get_food_menu('drinks')
                }
                planner_state = 'food_select_drink'
            else:
                bot_response = {
                    'sender': 'bot',
                    'text': error_msg,
                    'show_pasta_buttons': True,
                    'pasta_options': get_food_menu('pasta')
                }

        elif planner_state == 'food_select_drink':
            selected_drink = user_message.strip()
            package_letter = planner_data.get('package_letter')
            # Use default rules if no package_letter (custom events)
            rules = PACKAGE_RULES.get(package_letter, {'dishes': 3, 'pasta': 1, 'drinks': 1, 'rice': True, 'dessert': True})
            
            is_valid, error_msg, corrected_value = validate_input('drink', selected_drink, context={'drink_options': get_food_menu('drinks')})
            if is_valid:
                planner_data['food_selection']['drinks'] = [corrected_value]
                bot_response = {
                    'sender': 'bot',
                    'text': "Great! Your selections are complete. Would you like to review your choices or make any changes?",
                    'show_finish_options': True
                }
                planner_state = 'food_select_finish'
            else:
                bot_response = {
                    'sender': 'bot',
                    'text': error_msg,
                    'show_drink_buttons': True,
                    'drink_options': get_food_menu('drinks')
                }

        elif planner_state == 'food_select_finish':
            if user_message.lower() in ['finish', 'done']:
                # Prepare summary
                summary_lines = []
                summary_lines.append({'type': 'text', 'value': f"Event type: {planner_data.get('event_type', 'N/A').title()}"})
                summary_lines.append({'type': 'text', 'value': f"Event Date: {planner_data.get('event_date', 'N/A')}"})
                summary_lines.append({'type': 'text', 'value': f"Number of Guests: {planner_data.get('number_of_pax', 'N/A')}"})
                summary_lines.append({'type': 'text', 'value': f"Venue/Location: {planner_data.get('venue_location', 'N/A')}"})
                
                if not planner_data.get('is_custom_event', False):
                    theme = planner_data.get('theme')
                    theme_imgs = planner_data.get('theme_images', [])
                    theme_image = theme_imgs[0] if theme_imgs else None
                    summary_lines.append({'type': 'theme', 'value': f"Theme: {theme.title() if theme else 'N/A'}", 'img': theme_image})
                    summary_lines.append({'type': 'text', 'value': f"Color palette: {planner_data.get('color_palette', 'N/A')}"})
                
                package_image = planner_data.get('package_image')
                summary_lines.append({'type': 'package', 'value': f"Package: {planner_data.get('package_choice', 'N/A')}", 'img': package_image})
                
                # Food selection details
                summary_lines.append({'type': 'text', 'value': "Food Selection:"})
                if 'food_selection' in planner_data:
                    selected_food = planner_data['food_selection']
                    if 'dishes' in selected_food: summary_lines.append({'type': 'text', 'value': f"Dishes: {', '.join(selected_food['dishes'])}"})
                    if 'pasta' in selected_food: summary_lines.append({'type': 'text', 'value': f"Pasta: {', '.join(selected_food['pasta'])}"})
                    if 'drinks' in selected_food: summary_lines.append({'type': 'text', 'value': f"Drinks: {', '.join(selected_food['drinks'])}"})
                
                summary_lines.append({'type': 'text', 'value': "Rice: Steamed Rice"})
                summary_lines.append({'type': 'text', 'value': "Dessert: Dessert Buffet"})
                
                bot_response = {
                    'sender': 'bot',
                    'text': "Here is a summary of your event plan:",
                    'summary_lines': summary_lines
                }
                planner_state = 'summary'
            else:
                bot_response = {
                    'sender': 'bot',
                    'text': "Do you want to change anything you selected? If not, press the finish button.",
                    'show_finish_options': True
                }

        if bot_response:
            chat_history.append(bot_response)
            request.session['planner_state'] = planner_state
            request.session['planner_data'] = planner_data
            request.session['chat_history'] = chat_history
            request.session.modified = True

    # Handle GET request or no bot_response case
    if not bot_response:
        if request.method == 'GET':
            bot_response = {
                'sender': 'bot',
                'text': "Hey there! I'm Patrice – your go-to buddy for planning awesome events.\nWhether it's something big, small, or totally extra, I've got your back.\n\nSo, what date are we looking at for your event?",
                'show_date_input': True
            }
            chat_history = [bot_response]
            request.session['chat_history'] = chat_history
            request.session['planner_state'] = 'date_input'
            request.session['planner_data'] = {}
            request.session['initialized'] = True
            request.session.modified = True

    # Generate title for the chat session
    title = generate_chat_title(chat_history, planner_data)

    # Fetch saved sessions and find current session
    saved_sessions = ChatSession.objects.all().order_by('-updated_at')
    current_session_id = find_current_session_id(saved_sessions, chat_history, planner_data)

    return render(request, 'chatbot.html', {
        'chat_history': chat_history,
        'saved_sessions': saved_sessions,
        'current_title': title,
        'current_session_id': current_session_id
    })

def generate_chat_title(chat_history, planner_data):
    """Generate a title for the chat session based on planner data or first user message"""
    if planner_data:
        title_parts = []
        if planner_data.get('event_type'):
            title_parts.append(planner_data['event_type'].title())
        if planner_data.get('event_date'):
            title_parts.append(planner_data['event_date'])
        if planner_data.get('number_of_pax'):
            title_parts.append(f"{planner_data['number_of_pax']}pax")
        
        if title_parts:
            title = ": ".join(title_parts)
            return title[:50] + "..." if len(title) > 50 else title

    return get_first_user_message(chat_history)

def find_current_session_id(saved_sessions, chat_history, planner_data):
    """Find the ID of the current session by comparing chat histories"""
    for session in saved_sessions:
        if compare_chat_histories(session.chat_history, chat_history) and session.planner_data == planner_data:
            return session.id
    return None

def compare_chat_histories(history1, history2):
    """Compare two chat histories ignoring dynamic UI elements"""
    def simplify_message(msg):
        return {'sender': msg['sender'], 'text': msg['text']}
    
    simplified1 = [simplify_message(msg) for msg in history1]
    simplified2 = [simplify_message(msg) for msg in history2]
    return simplified1 == simplified2

def save_chat_session(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        chat_history = request.session.get('chat_history', [])
        # Generate title based on available planner data
        planner_data = request.session.get('planner_data', {})
        title_parts = []
        if planner_data.get('event_type'):
             title_parts.append(planner_data['event_type'].title())
        if planner_data.get('event_date'):
             title_parts.append(planner_data['event_date'])
        if planner_data.get('number_of_pax'):
             title_parts.append(f"{planner_data['number_of_pax']}pax")

        if title_parts:
             title = ": ".join(title_parts)
             if len(title) > 50: # Keep title reasonably short
                  title = title[:50] + "..."
        else:
            # Fallback to first user message if no planner data for title
            title = get_first_user_message(chat_history)

        planner_state = request.session.get('planner_state', 'start')

        user = request.user if request.user.is_authenticated else None
        session = ChatSession.objects.create(
            title=title,
            chat_history=chat_history,
            planner_state=planner_state,
            planner_data=planner_data,
            user=user
        )
        return JsonResponse({'id': session.id, 'title': session.title})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def list_chat_sessions(request):
    sessions = ChatSession.objects.all().order_by('-updated_at')
    return JsonResponse({'sessions': list(sessions.values('id', 'title', 'updated_at'))})

def load_chat_session(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id)
    request.session['chat_history'] = session.chat_history
    request.session['planner_state'] = session.planner_state
    request.session['planner_data'] = session.planner_data
    request.session.modified = True
    return redirect('chatbot')

def new_chat_session(request):
    request.session.pop('chat_history', None)
    request.session.pop('planner_state', None)
    request.session.pop('planner_data', None)
    request.session.pop('initialized', None)  # Remove the flag so chatbot_view will re-initialize
    request.session.modified = True
    return redirect('chatbot')

def get_first_user_message(chat_history):
    for msg in chat_history:
        if msg.get('sender') == 'user' and msg.get('text'):
            return msg['text']
    return 'New Chat'

def handle_state_transition(request, current_state, user_message, planner_data):
    """
    Centralized state transition logic.
    Returns (new_state, bot_response, updated_planner_data)
    """
    lower_msg = user_message.lower().strip()
    bot_response = None
    new_state = current_state

    # Handle global commands first
    if matches_any(restart_keywords, lower_msg):
        return 'date_input', {
            'sender': 'bot',
            'text': "The chat has been reset. Hey there! I'm Patrice – your go-to buddy for planning awesome events.\nWhether it's something big, small, or totally extra, I've got your back.\n\nSo, what date are we looking at for your event?",
            'show_date_input': True
        }, {}

    if matches_any(help_keywords, lower_msg):
        return current_state, {
            'sender': 'bot',
            'text': "You can type any of the following at any time:\n- change color\n- change theme\n- change event\n- change package\n- restart\n- help\nContinue your event planning or type a command above."
        }, planner_data

    # Handle change commands
    if current_state in ['food_select_dishes', 'food_select_pasta', 'food_select_drink', 'food_select_finish', 'summary']:
        if matches_any(color_keywords + theme_keywords + event_keywords + package_keywords, lower_msg):
            return current_state, {
                'sender': 'bot',
                'text': "You have already completed this step. If you want to start over and make changes, please type 'reset' or 'restart'."
            }, planner_data

    # Handle state-specific logic
    if current_state == 'date_input':
        try:
            event_date = datetime.strptime(user_message, '%Y-%m-%d')
            planner_data['event_date'] = user_message
            return 'event_type', {
                'sender': 'bot',
                'text': "Great! Now, what type of event would you like to plan?",
                'show_event_buttons': True
            }, planner_data
        except ValueError:
            return current_state, {
                'sender': 'bot',
                'text': "Please enter a valid date in YYYY-MM-DD format.",
                'show_date_input': True
            }, planner_data

    # Add more state transitions here...

    return new_state, bot_response, planner_data

def matches_any(keywords, text):
    """Helper function to check if any keyword matches the text"""
    return any(k in text for k in keywords)

def validate_input(input_type, value, context=None):
    """
    Centralized validation logic for different types of inputs.
    Returns (is_valid, error_message, corrected_value)
    """
    if input_type == 'date':
        try:
            date = datetime.strptime(value, '%Y-%m-%d')
            return True, None, value
        except ValueError:
            return False, "Please enter a valid date in YYYY-MM-DD format.", None

    elif input_type == 'event_type':
        valid_events = ['kiddie party', 'birthday party', 'wedding', 'christening']
        is_valid, corrected_input, suggestions = validate_and_suggest(value.lower(), valid_events, "event type")
        if is_valid:
            return True, None, corrected_input
        elif value.strip():  # If not empty, treat as custom event
            return True, None, value.strip()
        else:
            return False, "Please select an event type from the options or enter a custom event type.", None

    elif input_type == 'pax':
        try:
            pax_str = value.strip().lower().replace('pax', '').strip()
            num_pax = int(pax_str)
            event_type = context.get('event_type', '').lower() if context else ''
            valid_pax_options = [int(p.replace('pax', '')) for p in get_pax_options(event_type)]
            if num_pax in valid_pax_options:
                return True, None, num_pax
            else:
                return False, f"For {event_type.title()} events, we have options for {min(valid_pax_options)} to {max(valid_pax_options)} guests.", None
        except ValueError:
            return False, "Please enter a valid number for guests.", None

    elif input_type == 'venue':
        if value.strip():
            return True, None, value.strip()
        return False, "Please provide a venue or location for the event.", None

    elif input_type == 'theme_category':
        categories = get_all_categories()
        if value.lower() in [cat.lower() for cat in categories]:
            return True, None, next(cat for cat in categories if cat.lower() == value.lower())
        return False, "Please select a valid theme category.", None

    elif input_type == 'package_letter':
        if value.upper() in ['A', 'B', 'C']:
            return True, None, value.upper()
        return False, "Please select package A, B, or C.", None

    elif input_type == 'dish':
        all_dishes = []
        for category, dishes in context.get('all_dishes', {}).items():
            all_dishes.extend(dishes)
        is_valid, corrected_input, suggestions = validate_and_suggest(value.lower(), [d.lower() for d in all_dishes], "dish")
        if is_valid:
            return True, None, all_dishes[[d.lower() for d in all_dishes].index(corrected_input)]
        else:
            suggestion_text = f"Did you mean '{suggestions[0]}'" if suggestions else "No similar dishes found"
            return False, suggestion_text, None

    elif input_type == 'pasta':
        pasta_options = context.get('pasta_options', [])
        is_valid, corrected_input, suggestions = validate_and_suggest(value.lower(), [p.lower() for p in pasta_options], "pasta")
        if is_valid:
            return True, None, pasta_options[[p.lower() for p in pasta_options].index(corrected_input)]
        else:
            suggestion_text = f"Did you mean '{suggestions[0]}'" if suggestions else "No similar pasta options found"
            return False, suggestion_text, None

    elif input_type == 'drink':
        drink_options = context.get('drink_options', [])
        is_valid, corrected_input, suggestions = validate_and_suggest(value.lower(), [d.lower() for d in drink_options], "drink")
        if is_valid:
            return True, None, drink_options[[d.lower() for d in drink_options].index(corrected_input)]
        else:
            suggestion_text = f"Did you mean '{suggestions[0]}'" if suggestions else "No similar drink options found"
            return False, suggestion_text, None

    elif input_type == 'color_palette':
        # Accept any non-empty string; could add suggestion match
        if value.strip():
            return True, None, value.strip()
        return False, "Please provide a color palette.", None

    return False, "Invalid input type for validation.", None
