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
    validate_and_suggest
)
from fuzzywuzzy import process

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

def get_food_categories():
    """Helper function to get food categories"""
    return [
        'vegetables',
        'dessert',
        'pasta',
        'drinks',
        'beef',
        'pork',
        'chicken',
        'seafood'
    ]

def get_food_menu(category):
    """Helper function to get food items by category (updated to match actual menu)"""
    menu = {
        'vegetables': [
            'Buttered Mixed Vegetables',
            'Chopsuey in White Sauce',
            'Chopsuey in Oyster Sauce',
            'Lumpiang Sariwa',
            'Oriental Mixed Vegetables',
            'Stir Fry Vegetables',
        ],
        'dessert': [
            'Buko Salad',
            'Buko Pandan',
            'Chocolate Fountain',
            'Coffee Jelly',
            'Dessert Buffet',
            'Fruit Salad',
            'Garden Salad',
            'Ice Cream',
            'Leche Flan',
            'Mango Tapioca',
            'Tropical Fruits',
        ],
        'pasta': [
            'Baked Macaroni',
            'Fettuccine Alfredo',
            'Lasagna Rolls',
            'Linguine in White or Red Sauce',
            'Pancit Bihon or Canton',
            'Penne in White or Red Sauce',
            'Rigatoni in White or Red Sauce',
            'Spaghetti',
        ],
        'drinks': [
            'Blue Lemonade',
            'Cucumber Lemonade',
            'Four Seasons',
            'Lemon Tea',
            'Orange Juice',
            'Pineapple Juice',
            'Red Tea',
        ],
        'beef': [
            'Beef Broccoli',
            'Beef Caldereta',
            'Beef Kare-Kare',
            'Beef Teriyaki',
            'Beef with Gravy Sauce',
            'Garlic Beef',
            'Lengua Pastel',
            'Pot-Roast Beef',
        ],
        'pork': [
            'Grilled Liempo',
            'Hawaiian Sparibs',
            'Kare-Kare Bagnet',
            'Lechon Kawali',
            'Lengua Pastel',
            'Lumpiang Shanghai',
            'Pork BBQ',
            'Pork Caldereta',
            'Pork Hamonado',
            'Pork Menudo',
            'Pork Morcon',
            'Pork Teriyaki',
            'Roast Pork Hawaiian',
            'Roast Pork with Raisin Sauce',
        ],
        'chicken': [
            'Breaded Fried Chicken',
            'Buttered Chicken',
            'Chicken BBQ',
            'Chicken Cordon Bleu',
            'Chicken Lollipop',
            'Chicken Pastel',
            'Chicken Teriyaki',
            'Honey Glazed Chicken',
            'Hongkong Chicken',
            'Orange Chicken with Lemon Sauce',
            'Royal Chicken',
        ],
        'seafood': [
            'Calamares',
            'Fish Fillet with Chili Sauce',
            'Fish Fillet with Tartar Sauce',
            'Fish Tofu',
            'Mixed Seafoods with Vegetables',
            'Squid with Lemon Sauce',
            'Tempura',
        ],
    }
    return menu.get(category.lower(), [])

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
    static_dir = os.path.join(settings.BASE_DIR, 'main', 'static', 'main', 'images', 'packages')
    prefix = event_type.lower()
    images = []
    for fname in os.listdir(static_dir):
        if fname.lower().startswith(prefix):
            images.append((fname.replace('.jpg', '').replace('_', ' ').title(), f'/static/main/images/packages/{fname}'))
    images.sort()  # Optional: sort by name
    return images

# Package rules for all event types
PACKAGE_RULES = {
    'A': {'dishes': 3, 'pasta': 1, 'drinks': 1, 'rice': True, 'dessert': True},
    'B': {'dishes': 4, 'pasta': 1, 'drinks': 1, 'rice': True, 'dessert': True},
    'C': {'dishes': 5, 'pasta': 1, 'drinks': 1, 'rice': True, 'dessert': True},
}

def get_food_menu_images():
    """Return all food menu images for display."""
    static_dir = os.path.join(settings.BASE_DIR, 'main', 'static', 'main', 'images', 'foodMenu')
    images = []
    for fname in os.listdir(static_dir):
        if fname.lower().endswith('.jpg'):
            images.append(f'/static/main/images/foodMenu/{fname}')
    images.sort()
    return images

def chatbot_view(request):
    # Always start fresh if session is new or uninitialized
    if not request.session.get('initialized', False):
        request.session['chat_history'] = [
            {'sender': 'bot', 'text': "Welcome! Do you need help with event planning or do you want to view FAQs? (Type 'event planning' or 'faq')"}
        ]
        request.session['planner_state'] = 'start'
        request.session['planner_data'] = {}
        request.session['initialized'] = True
        request.session.modified = True

    chat_history = request.session.get('chat_history', [])
    planner_state = request.session.get('planner_state', 'start')
    planner_data = request.session.get('planner_data', {})

    if request.method == 'POST':
        user_message = request.POST.get('message')
        chat_history.append({'sender': 'user', 'text': user_message})
        lower_msg = user_message.lower().strip()

        bot_response = None

        # --- GLOBAL: Allow user to change color, theme, event, or package at any time before summary ---
        color_keywords = [
            'change color', 'choose another color', 'pick a new color', 'switch color', 'change palette', 'pick another color', 'select different color',
            'i want to change the color', 'i want to select another color', 'i want to pick a different color', 'go back to color', 'reset color', 'back to color selection', 'color options', 'different color', 'color change'
        ]
        theme_keywords = [
            'change theme', 'choose another theme', 'pick a new theme', 'switch theme', 'i want another theme', 'pick another theme', 'select different theme', 'choose theme', 'select theme',
            'i want to change the theme', 'i want to select another theme', 'i want to pick a different theme', 'go back to theme', 'reset theme', 'back to theme selection', 'theme options', 'different theme', 'theme change',
            'modify theme', 'update theme', 'edit theme', 'alter theme', 'redo theme', 'reselect theme', 'pick theme again', 'pick again theme', 'start theme over', 'theme selection again', 'theme again', 'theme redo', 'theme reselect', 'theme edit', 'theme update', 'theme modify', 'theme alter', 'theme reset', 'theme pick again', 'theme pick new', 'theme pick different', 'theme pick another', 'theme pick', 'theme choose again', 'theme choose new', 'theme choose different', 'theme choose another', 'theme choose', 'theme select again', 'theme select new', 'theme select different', 'theme select another', 'theme select'
        ]
        event_keywords = [
            'change event', 'choose another event', 'pick a new event', 'switch event', 'change event type', 'pick another event', 'select different event', 'choose event', 'select event',
            'i want to change the event', 'i want to select another event', 'i want to pick a different event', 'go back to event', 'reset event', 'back to event selection', 'event options', 'different event', 'event change',
            'i want to select other type of event', 'i want to select other event type', 'i want to change the type of event', 'change my event', 'start over', 'back to event type', 'pick a new event', 'new event'
        ]
        package_keywords = [
            'change package', 'choose another package', 'pick a new package', 'switch package', 'pick another package', 'select different package', 'choose package', 'select package',
            'i want to change the package', 'i want to select another package', 'i want to pick a different package', 'go back to package', 'reset package', 'back to package selection', 'package options', 'different package', 'package change'
        ]
        restart_keywords = [
            'restart', 'start over', 'reset', 'new plan', 'new event'
        ]
        help_keywords = ['/help']
        def matches_any(keywords):
            return any(k in lower_msg for k in keywords)

        # If the user tries to change a field after it is already completed, prompt to restart
        completed_states = ['food_select_dishes', 'food_select_pasta', 'food_select_drink', 'food_select_finish', 'summary']
        if planner_state in completed_states and (
            matches_any(color_keywords) or matches_any(theme_keywords) or matches_any(event_keywords) or matches_any(package_keywords)
        ):
            bot_response = {
                'sender': 'bot',
                'text': "You have already completed this step. If you want to start over and make changes, please type 'reset' or 'restart'."
            }
            chat_history.append(bot_response)
            request.session['chat_history'] = chat_history
            request.session.modified = True
            return render(request, 'main/chatbot.html', {
                'chat_history': chat_history,
                'saved_sessions': ChatSession.objects.all().order_by('-updated_at'),
                'current_title': 'New Chat'
            })

        # Restart command
        if matches_any(restart_keywords):
            request.session.flush()
            bot_response = {
                'sender': 'bot',
                'text': "The chat has been reset. Welcome! Do you need help with event planning or do you want to view FAQs? (Type 'event planning' or 'faq')"
            }
            request.session['planner_state'] = 'start'
            request.session['planner_data'] = {}
            request.session['initialized'] = True
            chat_history = [bot_response]
            request.session['chat_history'] = chat_history
            request.session.modified = True
            return render(request, 'main/chatbot.html', {
                'chat_history': chat_history,
                'saved_sessions': ChatSession.objects.all().order_by('-updated_at'),
                'current_title': 'New Chat'
            })

        # Help command
        if matches_any(help_keywords):
            bot_response = {
                'sender': 'bot',
                'text': "You can type any of the following at any time:\n- change color\n- change theme\n- change event\n- change package\n- restart\n- help\nContinue your event planning or type a command above."
            }
            chat_history.append(bot_response)
            request.session['chat_history'] = chat_history
            request.session.modified = True
            return render(request, 'main/chatbot.html', {
                'chat_history': chat_history,
                'saved_sessions': ChatSession.objects.all().order_by('-updated_at'),
                'current_title': 'New Chat'
            })

        # Store the current state to return to after change
        if matches_any(color_keywords):
            request.session['return_to_state'] = planner_state
            bot_response = {
                'sender': 'bot',
                'text': "Would you like to use the default color palette for this theme, or do you want to modify the colors? (Type 'default' or specify your colors.)"
            }
            request.session['planner_state'] = 'color_palette_confirm'
            chat_history.append(bot_response)
            request.session['chat_history'] = chat_history
            request.session['planner_data'] = planner_data
            request.session.modified = True
            return render(request, 'main/chatbot.html', {
                'chat_history': chat_history,
                'saved_sessions': ChatSession.objects.all().order_by('-updated_at'),
                'current_title': 'New Chat'
            })
        if matches_any(theme_keywords):
            request.session['return_to_state'] = planner_state
            event_type = planner_data.get('event_type')
            # Clear previous theme/category selection so the next category is always fresh
            planner_data.pop('current_themes', None)
            planner_data.pop('current_category', None)
            planner_data.pop('theme', None)
            if not event_type:
                bot_response = {
                    'sender': 'bot',
                    'text': "Please select an event type first (Kiddie Party, Birthday Party, Wedding, or Christening)."
                }
                request.session['planner_state'] = 'event_type'
            else:
                # Show theme categories as a bulleted list without numbers
                theme_categories = ['Disney', 'Movie', 'Gaming', 'Superhero', 'Sports', 'Animal', 'Color', 'Special', 'Other']
                category_bullets = '<ul>' + ''.join([f'<li>{cat}</li>' for cat in theme_categories]) + '</ul>'
                bot_response = {
                    'sender': 'bot',
                    'text': f"Great choice! Now, what type of theme are you interested in? Please choose one of the following options:{category_bullets}(Type the category name, e.g., 'Disney')"
                }
            chat_history.append(bot_response)
            request.session['chat_history'] = chat_history
            request.session['planner_data'] = planner_data
            request.session.modified = True
            return render(request, 'main/chatbot.html', {
                'chat_history': chat_history,
                'saved_sessions': ChatSession.objects.all().order_by('-updated_at'),
                'current_title': 'New Chat'
            })
        if matches_any(event_keywords):
            request.session['return_to_state'] = planner_state
            # Always show event type options
            event_type_options = ['Kiddie Party', 'Birthday Party', 'Wedding', 'Christening']
            event_type_bullets = '<ul>' + ''.join([f'<li>{cat}</li>' for cat in event_type_options]) + '</ul>'
            bot_response = {
                'sender': 'bot',
                'text': f"What type of event would you like to plan? Please choose one of the following options:{event_type_bullets}(Type the category name, e.g., 'Wedding')"
            }
            request.session['planner_state'] = 'event_type'
            chat_history.append(bot_response)
            request.session['chat_history'] = chat_history
            request.session['planner_data'] = planner_data
            request.session.modified = True
            return render(request, 'main/chatbot.html', {
                'chat_history': chat_history,
                'saved_sessions': ChatSession.objects.all().order_by('-updated_at'),
                'current_title': 'New Chat'
            })
        if matches_any(package_keywords):
            request.session['return_to_state'] = planner_state
            event_type_input = planner_data.get('event_type', '').lower()
            event_type_map = {
                'kiddie party': 'kiddie',
                'birthday party': 'birthday',
                'wedding': 'wedding',
                'christening': 'christening',
            }
            event_type = event_type_map.get(event_type_input, event_type_input)
            if not event_type:
                # Prompt for event type first
                event_type_options = ['Kiddie Party', 'Birthday Party', 'Wedding', 'Christening']
                event_type_bullets = '<ul>' + ''.join([f'<li>{cat}</li>' for cat in event_type_options]) + '</ul>'
                bot_response = {
                    'sender': 'bot',
                    'text': f"Please select an event type first:{event_type_bullets}(Type the category name, e.g., 'Wedding')"
                }
                request.session['planner_state'] = 'event_type'
            else:
                package_images = get_event_package_images(event_type)
                bot_response = {
                    'sender': 'bot',
                    'text': f"Here are our available packages for {event_type_input.title()}:",
                    'package_options': package_images
                }
                request.session['planner_state'] = 'package_image_choice'
            chat_history.append(bot_response)
            request.session['chat_history'] = chat_history
            request.session['planner_data'] = planner_data
            request.session.modified = True
            return render(request, 'main/chatbot.html', {
                'chat_history': chat_history,
                'saved_sessions': ChatSession.objects.all().order_by('-updated_at'),
                'current_title': 'New Chat'
            })

        # After color/theme/event/package change, return to previous state if set
        if planner_state in ['color_palette_confirm', 'theme_choice', 'event_type', 'package_image_choice'] and 'return_to_state' in request.session and request.session['return_to_state']:
            # Only trigger return if the user has just completed the change (e.g., after color, theme, event, or package selection)
            return_to_state = request.session.pop('return_to_state')
            # For color, update color_palette and IMMEDIATELY prompt for package selection
            if planner_state == 'color_palette_confirm':
                color_options = ['default', 'custom']
                valid_color_palettes = [
                    'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'white', 'black', 'gold', 'silver', 'brown', 'gray', 'beige', 'ivory', 'cream', 'peach', 'maroon', 'navy', 'teal', 'turquoise', 'aqua', 'lavender', 'violet', 'magenta', 'lime', 'mint', 'coral', 'pearl', 'rose', 'champagne', 'burgundy', 'pastel', 'rainbow', 'multicolor', 'colorful',
                ]
                popular_combos = [
                    'red and gold', 'blue and gold', 'blue and yellow', 'pink and gold', 'pink and purple', 'blue and silver', 'gold and white', 'white and gold', 'black and gold', 'black and white', 'green and gold', 'mint and peach', 'peach and gold', 'red and white', 'yellow and white', 'purple and silver', 'navy and gold', 'navy and silver', 'rose gold', 'champagne and gold', 'pastel rainbow', 'pastel pink', 'pastel blue', 'pastel green', 'pastel yellow', 'pastel purple', 'pastel mint', 'pastel peach', 'pastel orange', 'pastel lavender', 'pastel violet', 'pastel magenta', 'pastel coral', 'pastel cream', 'pastel beige', 'pastel ivory', 'pastel rose', 'pastel mint and peach', 'pastel pink and gold', 'pastel blue and gold',
                ]
                normalized_msg = lower_msg.strip()
                color_selected = None
                try:
                    idx = int(normalized_msg) - 1
                    if 0 <= idx < len(color_options):
                        color_selected = color_options[idx]
                except Exception:
                    pass
                if not color_selected:
                    color_match, score = get_fuzzy_match(normalized_msg, color_options)
                    if color_match and (score >= 90):
                        color_selected = color_match
                theme_selected = planner_data.get('theme', None)
                images = get_theme_images(theme_selected) if theme_selected else []
                ai_image = generate_ai_theme_image(theme_selected) if theme_selected else None
                theme_image_choice = planner_data.get('theme_image_choice', 'given')
                if theme_image_choice == 'ai':
                    images_to_show = [ai_image] if ai_image else []
                else:
                    images_to_show = images
                is_valid_palette = False
                if color_selected or normalized_msg == 'default':
                    is_valid_palette = True
                else:
                    user_palette = normalized_msg.lower().replace(' and ', ',').replace(' & ', ',')
                    user_palette = user_palette.replace(';', ',')
                    color_parts = [c.strip() for c in user_palette.split(',') if c.strip()]
                    valid_colors_lower = [c.lower() for c in valid_color_palettes]
                    if 1 <= len(color_parts) <= 3 and all(c in valid_colors_lower for c in color_parts):
                        is_valid_palette = True
                    else:
                        combos_lower = [c.lower() for c in popular_combos]
                        if normalized_msg.lower() in combos_lower:
                            is_valid_palette = True
                if is_valid_palette:
                    planner_data['color_palette'] = color_selected or normalized_msg
                    event_type_input = planner_data.get('event_type', '').lower()
                    event_type_map = {
                        'kiddie party': 'kiddie',
                        'birthday party': 'birthday',
                        'wedding': 'wedding',
                        'christening': 'christening',
                    }
                    event_type = event_type_map.get(event_type_input, event_type_input)
                    package_images = get_event_package_images(event_type)
                    bot_response = {
                        'sender': 'bot',
                        'text': f"Here are our available packages for {event_type_input.title()}:",
                        'package_options': package_images
                    }
                    request.session['planner_state'] = 'package_image_choice'
                else:
                    # Improved fuzzy suggestion for color palettes
                    all_palettes = valid_color_palettes + popular_combos
                    # Get top 3 close matches
                    suggestions = process.extract(normalized_msg, all_palettes, limit=3)
                    suggestions = [s for s in suggestions if s[1] >= 70]
                    # If user entered two colors, try to match each color and suggest a combo
                    combo_suggestion = None
                    if len(color_parts) == 2:
                        c1, c2 = color_parts
                        c1_match, c1_score = process.extractOne(c1, valid_colors_lower)
                        c2_match, c2_score = process.extractOne(c2, valid_colors_lower)
                        if c1_score >= 80 and c2_score >= 80:
                            # Try to find a combo in popular_combos
                            for combo in popular_combos:
                                if c1_match in combo and c2_match in combo:
                                    combo_suggestion = combo
                                    break
                            if not combo_suggestion:
                                combo_suggestion = f"{valid_color_palettes[valid_colors_lower.index(c1_match)]} and {valid_color_palettes[valid_colors_lower.index(c2_match)]}"
                    if combo_suggestion:
                        suggestion_text = f"Did you mean '{combo_suggestion}'? Please type a valid color palette or 'default'."
                    elif suggestions:
                        suggestion_text = f"Did you mean '{suggestions[0][0]}'? Please type a valid color palette or 'default'."
                    else:
                        suggestion_text = "Please specify a valid color palette (e.g., 'blue and gold', 'pastel', 'rainbow', 'pink and gold', or any 1-3 colors from the standard palette) or type 'default' to use the original colors."
                    bot_response = {
                        'sender': 'bot',
                        'text': suggestion_text,
                        'selected_theme_images': images_to_show,
                        'theme_confirm_name': theme_selected.title() if theme_selected else '',
                    }
            # For theme, update theme and IMMEDIATELY prompt for color palette
            if planner_state == 'theme_choice':
                all_cats = get_all_categories()
                normalized_msg = lower_msg.strip()
                # Try category matching first
                is_valid, corrected_input, suggestions = validate_and_suggest(normalized_msg, all_cats, "category")
                if is_valid:
                    selected_category = corrected_input
                    themes, images, image_labels = get_themes_and_images(selected_category)
                    theme_options = [(theme.title(), get_theme_images(theme)[0] if get_theme_images(theme) else None) for theme in themes]
                    cat_desc = get_category_description(selected_category)
                    bot_response = {
                        'sender': 'bot',
                        'text': f"These are some sample themes we have catered for the {selected_category.title()} category.\n{cat_desc}\n\nWhich theme do you want to use for your event?",
                        'theme_options': theme_options,
                    }
                    planner_data['current_themes'] = themes
                    planner_data['current_category'] = selected_category
                else:
                    # Try theme matching (by number or name)
                    current_themes = planner_data.get('current_themes', [])
                    theme_selected = None
                    # Try number selection
                    try:
                        idx = int(normalized_msg) - 1
                        if 0 <= idx < len(current_themes):
                            theme_selected = current_themes[idx]
                    except Exception:
                        pass
                    # Try name selection
                    if not theme_selected:
                        is_valid, corrected_input, suggestions = validate_and_suggest(normalized_msg, current_themes, "theme")
                        if is_valid:
                            theme_selected = corrected_input
                    if theme_selected:
                        planner_data['theme'] = theme_selected
                        images = get_theme_images(theme_selected)
                        ai_image = generate_ai_theme_image(theme_selected)
                        bot_response = {
                            'sender': 'bot',
                            'text': 'Do you want to keep the generated image as the theme design or do you prefer using the ones we have available? Type "ai" or "given".',
                            'theme_confirm_images': images,
                            'theme_confirm_name': theme_selected.title(),
                            'ai_generated_image': ai_image,
                        }
                        request.session['planner_state'] = 'theme_image_choice'
                    else:
                        if suggestions:
                            bot_response = {
                                'sender': 'bot',
                                'text': enhance_bot_response(
                                    "I didn't understand. Did you mean one of these themes?",
                                    suggestions
                                ),
                                'theme_options': [(theme.title(), get_theme_images(theme)[0] if get_theme_images(theme) else None) for theme in suggestions]
                            }
                        else:
                            theme_categories = ['Disney', 'Movie', 'Gaming', 'Superhero', 'Sports', 'Animal', 'Color', 'Special', 'Other']
                            category_bullets = '<ul>' + ''.join([f'<li>{cat}</li>' for cat in theme_categories]) + '</ul>'
                            bot_response = {
                                'sender': 'bot',
                                'text': f"I didn't understand. Please choose a category from the list below:{category_bullets}"
                            }
            # For event, update event_type and IMMEDIATELY prompt for theme selection
            if planner_state == 'event_type':
                valid_events = ['kiddie party', 'birthday party', 'wedding', 'christening']
                normalized_msg = lower_msg.strip()
                event_selected = None
                # Try number selection first
                try:
                    idx = int(normalized_msg) - 1
                    if 0 <= idx < len(valid_events):
                        event_selected = valid_events[idx]
                except Exception:
                    pass
                # If number selection failed, try enhanced matching
                if not event_selected:
                    is_valid, corrected_input, suggestions = validate_and_suggest(normalized_msg, valid_events, "event type")
                    if is_valid:
                        event_selected = corrected_input
                if event_selected:
                    planner_data['event_type'] = event_selected
                    theme_categories = ['Disney', 'Movie', 'Gaming', 'Superhero', 'Sports', 'Animal', 'Color', 'Special', 'Other']
                    category_bullets = '<ul>' + ''.join([f'<li>{cat}</li>' for cat in theme_categories]) + '</ul>'
                    bot_response = {
                        'sender': 'bot',
                        'text': f"Great choice! Now, what type of theme are you interested in? Please choose one of the following options:{category_bullets}(Type the category name, e.g., 'Disney')"
                    }
                    request.session['planner_state'] = 'theme_choice'
                else:
                    event_type_options = ['Kiddie Party', 'Birthday Party', 'Wedding', 'Christening']
                    event_type_bullets = '<ul>' + ''.join([f'<li>{cat}</li>' for cat in event_type_options]) + '</ul>'
                    bot_response = {
                        'sender': 'bot',
                        'text': f"What type of event would you like to plan? Please choose one of the following options:{event_type_bullets}(Type the category name, e.g., 'Wedding')"
                    }
                    request.session['planner_state'] = 'event_type'
                chat_history.append(bot_response)
                request.session['chat_history'] = chat_history
                request.session['planner_data'] = planner_data
                request.session.modified = True
                return render(request, 'main/chatbot.html', {
                    'chat_history': chat_history,
                    'saved_sessions': ChatSession.objects.all().order_by('-updated_at'),
                    'current_title': 'New Chat'
                })
            # For package, update package selection and IMMEDIATELY prompt for package letter
            if planner_state == 'package_image_choice':
                event_type_input = planner_data.get('event_type', '').lower()
                event_type_map = {
                    'kiddie party': 'kiddie',
                    'birthday party': 'birthday',
                    'wedding': 'wedding',
                    'christening': 'christening',
                }
                event_type = event_type_map.get(event_type_input, event_type_input)
                package_images = get_event_package_images(event_type)
                package_names = [pkg[0] for pkg in package_images]
                package_selected = None
                # Try number selection first
                try:
                    idx = int(user_message.strip()) - 1
                    if 0 <= idx < len(package_images):
                        package_selected = idx
                    else:
                        package_selected = None
                        # If the input is a number but out of range, do not try fuzzy matching
                except Exception:
                    package_selected = None
                    # Only try fuzzy/wildcard matching if input is not a number at all
                    is_valid, corrected_input, suggestions = validate_and_suggest(lower_msg, package_names, "package")
                    if is_valid:
                        package_selected = package_names.index(corrected_input)
                if package_selected is not None and 0 <= package_selected < len(package_images):
                    planner_data['package_image'] = package_images[package_selected][1]
                    planner_data['package_image_label'] = package_images[package_selected][0]
                    bot_response = {
                        'sender': 'bot',
                        'text': f"Which package do you want for {package_images[package_selected][0]}? (Type A, B, or C)",
                        'package_image_selected': package_images[package_selected][1],
                        'package_image_label': package_images[package_selected][0],
                    }
                    request.session['planner_state'] = 'package_letter_choice'
                else:
                    # Numbered list for package options
                    numbered_options = '<ul>' + ''.join([f'<li>{i+1}. {name}</li>' for i, name in enumerate(package_names)]) + '</ul>'
                    bot_response = {
                        'sender': 'bot',
                        'text': f"Please select from the options given below:{numbered_options}"
                    }
                chat_history.append(bot_response)
                request.session['chat_history'] = chat_history
                request.session['planner_data'] = planner_data
                request.session.modified = True
                return render(request, 'main/chatbot.html', {
                    'chat_history': chat_history,
                    'saved_sessions': ChatSession.objects.all().order_by('-updated_at'),
                    'current_title': 'New Chat'
                })
            # If returning to finish, prompt for finish/done
            if return_to_state == 'food_select_finish':
                bot_response = {
                    'sender': 'bot',
                    'text': "Type 'finish' or 'done' to see the summary of your event plan."
                }
                request.session['planner_state'] = 'food_select_finish'
            else:
                request.session['planner_state'] = return_to_state
            chat_history.append(bot_response)
            request.session['chat_history'] = chat_history
            request.session['planner_data'] = planner_data
            request.session.modified = True
            return render(request, 'main/chatbot.html', {
                'chat_history': chat_history,
                'saved_sessions': ChatSession.objects.all().order_by('-updated_at'),
                'current_title': 'New Chat'
            })

        # Step 0: Start - event planning or FAQ
        if planner_state == 'start':
            # Prioritize event planning/faq over help
            if 'faq' in lower_msg:
                bot_response = {
                    'sender': 'bot',
                    'text': (
                        "Here are some frequently asked questions:<ul>"
                        "<li>How do I book an event?</li>"
                        "<li>What are your payment options?</li>"
                        "<li>Can I customize a theme?</li>"
                        "<li>What is your cancellation policy?</li>"
                        "</ul>(Type your question or 'event planning' to start planning an event.)"
                    )
                }
                request.session['planner_state'] = 'faq'
            elif 'event' in lower_msg or 'plan' in lower_msg:
                theme_categories = ['Disney', 'Movie', 'Gaming', 'Superhero', 'Sports', 'Animal', 'Color', 'Special', 'Other']
                category_bullets = '<ul>' + ''.join([f'<li>{cat}</li>' for cat in theme_categories]) + '</ul>'
                bot_response = {
                    'sender': 'bot',
                    'text': f"What type of event would you like to plan? (Kiddie Party, Birthday Party, Wedding, or Christening)"
                }
                request.session['planner_state'] = 'event_type'
            elif matches_any(help_keywords):
                bot_response = {
                    'sender': 'bot',
                    'text': "You can type any of the following at any time:\n- change color\n- change theme\n- change event\n- change package\n- restart\n- help\nContinue your event planning or type a command above."
                }
            else:
                bot_response = {
                    'sender': 'bot',
                    'text': "Do you need help with event planning or do you want to view FAQs? (Type 'event planning' or 'faq')"
                }
        # After FAQ is shown, if in 'faq' state, check if user typed a question
        if planner_state == 'faq':
            faq_qas = {
                'how do i book an event': "You can enjoy complete event planning with us. Our team will assist you every step of the way.",
                'what are your payment options': "We accept GCash or cash payments.",
                'can i customize a theme': "Yes, you can! Our virtual event assistant can help you, or you may further refine your theme/design with our admin team.",
                'what is your cancellation policy': "All down payment fees made for reservations are forfeited upon cancellation. Reservation fees are non-refundable, non-transferable, and non-convertible."
            }
            normalized_msg = lower_msg.strip().rstrip('?').lower()
            if 'event planning' in normalized_msg:
                theme_categories = ['Disney', 'Movie', 'Gaming', 'Superhero', 'Sports', 'Animal', 'Color', 'Special', 'Other']
                category_bullets = '<ul>' + ''.join([f'<li>{cat}</li>' for cat in theme_categories]) + '</ul>'
                bot_response = {
                    'sender': 'bot',
                    'text': f"What type of event would you like to plan? (Kiddie Party, Birthday Party, Wedding, or Christening)"
                }
                request.session['planner_state'] = 'event_type'
                chat_history.append(bot_response)
                request.session['chat_history'] = chat_history
                request.session.modified = True
                return render(request, 'main/chatbot.html', {
                    'chat_history': chat_history,
                    'saved_sessions': ChatSession.objects.all().order_by('-updated_at'),
                    'current_title': 'New Chat'
                })
            # Fuzzy match user input to FAQ questions
            #from .utils import get_fuzzy_match
            faq_questions = list(faq_qas.keys())
            match, score = get_fuzzy_match(normalized_msg, faq_questions)
            if match and score >= 80:
                bot_response = {
                    'sender': 'bot',
                    'text': faq_qas[match]
                }
                chat_history.append(bot_response)
                request.session['chat_history'] = chat_history
                request.session.modified = True
                return render(request, 'main/chatbot.html', {
                    'chat_history': chat_history,
                    'saved_sessions': ChatSession.objects.all().order_by('-updated_at'),
                    'current_title': 'New Chat'
                })
            # If not a valid question or 'event planning', guide the user
            bot_response = {
                'sender': 'bot',
                'text': "Please choose a question from the list above or type 'event planning' to start planning an event."
            }
            chat_history.append(bot_response)
            request.session['chat_history'] = chat_history
            request.session.modified = True
            return render(request, 'main/chatbot.html', {
                'chat_history': chat_history,
                'saved_sessions': ChatSession.objects.all().order_by('-updated_at'),
                'current_title': 'New Chat'
            })
        # Step 1: Event Type Selection (with validation)
        elif planner_state == 'event_type':
            valid_events = ['kiddie party', 'birthday party', 'wedding', 'christening']
            normalized_msg = lower_msg.strip()
            event_selected = None
            # Try number selection first
            try:
                idx = int(normalized_msg) - 1
                if 0 <= idx < len(valid_events):
                    event_selected = valid_events[idx]
            except Exception:
                pass
            # Try name selection if number selection failed
            if not event_selected:
                is_valid, corrected_input, suggestions = validate_and_suggest(normalized_msg, valid_events, "event type")
                if is_valid:
                    event_selected = corrected_input
            if event_selected:
                planner_data['event_type'] = event_selected
                theme_categories = ['Disney', 'Movie', 'Gaming', 'Superhero', 'Sports', 'Animal', 'Color', 'Special', 'Other']
                category_bullets = '<ul>' + ''.join([f'<li>{cat}</li>' for cat in theme_categories]) + '</ul>'
                bot_response = {
                    'sender': 'bot',
                    'text': f"Great choice! Now, what type of theme are you interested in? Please choose one of the following options:{category_bullets}(Type the category name, e.g., 'Disney')"
                }
                request.session['planner_state'] = 'theme_choice'
            else:
                event_type_options = ['Kiddie Party', 'Birthday Party', 'Wedding', 'Christening']
                event_type_bullets = '<ul>' + ''.join([f'<li>{cat}</li>' for cat in event_type_options]) + '</ul>'
                bot_response = {
                    'sender': 'bot',
                    'text': f"What type of event would you like to plan? Please choose one of the following options:{event_type_bullets}(Type the category name, e.g., 'Wedding')"
                }
                request.session['planner_state'] = 'event_type'
            chat_history.append(bot_response)
            request.session['chat_history'] = chat_history
            request.session['planner_data'] = planner_data
            request.session.modified = True
            return render(request, 'main/chatbot.html', {
                'chat_history': chat_history,
                'saved_sessions': ChatSession.objects.all().order_by('-updated_at'),
                'current_title': 'New Chat'
            })
        # Step 2: Theme Selection (with validation)
        elif planner_state == 'theme_choice':
            all_cats = get_all_categories()
            normalized_msg = lower_msg.strip()
            # Try category matching first
            is_valid, corrected_input, suggestions = validate_and_suggest(normalized_msg, all_cats, "category")
            if is_valid:
                selected_category = corrected_input
                themes, images, image_labels = get_themes_and_images(selected_category)
                theme_options = [(theme.title(), get_theme_images(theme)[0] if get_theme_images(theme) else None) for theme in themes]
                cat_desc = get_category_description(selected_category)
                bot_response = {
                    'sender': 'bot',
                    'text': f"These are some sample themes we have catered for the {selected_category.title()} category.\n{cat_desc}\n\nWhich theme do you want to use for your event?",
                    'theme_options': theme_options,
                }
                planner_data['current_themes'] = themes
                planner_data['current_category'] = selected_category
            else:
                # Try theme matching (by number or name)
                current_themes = planner_data.get('current_themes', [])
                theme_selected = None
                # Try number selection
                try:
                    idx = int(normalized_msg) - 1
                    if 0 <= idx < len(current_themes):
                        theme_selected = current_themes[idx]
                except Exception:
                    pass
                # Try name selection
                if not theme_selected:
                    is_valid, corrected_input, suggestions = validate_and_suggest(normalized_msg, current_themes, "theme")
                    if is_valid:
                        theme_selected = corrected_input
                if theme_selected:
                    planner_data['theme'] = theme_selected
                    images = get_theme_images(theme_selected)
                    ai_image = generate_ai_theme_image(theme_selected)
                    bot_response = {
                        'sender': 'bot',
                        'text': 'Do you want to keep the generated image as the theme design or do you prefer using the ones we have available? Type "ai" or "given".',
                        'theme_confirm_images': images,
                        'theme_confirm_name': theme_selected.title(),
                        'ai_generated_image': ai_image,
                    }
                    request.session['planner_state'] = 'theme_image_choice'
                else:
                    # Numbered list for theme options
                    theme_options = [(theme.title(), get_theme_images(theme)[0] if get_theme_images(theme) else None) for theme in current_themes]
                    numbered_theme_options = '<ul>' + ''.join([f'<li>{i+1}. {theme[0]}</li>' for i, theme in enumerate(theme_options)]) + '</ul>'
                    bot_response = {
                        'sender': 'bot',
                        'text': f"Please select from the options given below:{numbered_theme_options}"
                    }
                chat_history.append(bot_response)
                request.session['chat_history'] = chat_history
                request.session['planner_data'] = planner_data
                request.session.modified = True
                return render(request, 'main/chatbot.html', {
                    'chat_history': chat_history,
                    'saved_sessions': ChatSession.objects.all().order_by('-updated_at'),
                    'current_title': 'New Chat'
                })

        # Step 4: Color Palette Confirmation
        elif planner_state == 'color_palette_confirm':
            valid_color_palettes = [
                'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'white', 'black', 'gold', 'silver', 'brown', 'gray', 'beige', 'ivory', 'cream', 'peach', 'maroon', 'navy', 'teal', 'turquoise', 'aqua', 'lavender', 'violet', 'magenta', 'lime', 'mint', 'coral', 'pearl', 'rose', 'champagne', 'burgundy', 'pastel', 'rainbow', 'multicolor', 'colorful',
            ]
            popular_combos = [
                'red and gold', 'blue and gold', 'blue and yellow', 'pink and gold', 'pink and purple', 'blue and silver', 'gold and white', 'white and gold', 'black and gold', 'black and white', 'green and gold', 'mint and peach', 'peach and gold', 'red and white', 'yellow and white', 'purple and silver', 'navy and gold', 'navy and silver', 'rose gold', 'champagne and gold', 'pastel rainbow', 'pastel pink', 'pastel blue', 'pastel green', 'pastel yellow', 'pastel purple', 'pastel mint', 'pastel peach', 'pastel orange', 'pastel lavender', 'pastel violet', 'pastel magenta', 'pastel coral', 'pastel cream', 'pastel beige', 'pastel ivory', 'pastel rose', 'pastel mint and peach', 'pastel pink and gold', 'pastel blue and gold',
            ]
            normalized_msg = lower_msg.strip()
            # Accept fuzzy/wildcard matches for 'default'
            default_match, default_score = get_fuzzy_match(normalized_msg, ['default'])
            if (default_match and default_score >= 80) or wildcard_match('*default*', normalized_msg):
                color_selected = 'default'
                planner_data['color_palette'] = color_selected
                event_type_input = planner_data.get('event_type', '').lower()
                event_type_map = {
                    'kiddie party': 'kiddie',
                    'birthday party': 'birthday',
                    'wedding': 'wedding',
                    'christening': 'christening',
                }
                event_type = event_type_map.get(event_type_input, event_type_input)
                package_images = get_event_package_images(event_type)
                bot_response = {
                    'sender': 'bot',
                    'text': f"Here are our available packages for {event_type_input.title()}:",
                    'package_options': package_images
                }
                request.session['planner_state'] = 'package_image_choice'
            else:
                # Try matching against both single colors and combinations
                all_palettes = valid_color_palettes + popular_combos
                is_valid, corrected_input, suggestions = validate_and_suggest(normalized_msg, all_palettes, "color palette")
                if is_valid:
                    color_selected = corrected_input
                    planner_data['color_palette'] = color_selected
                    event_type_input = planner_data.get('event_type', '').lower()
                    event_type_map = {
                        'kiddie party': 'kiddie',
                        'birthday party': 'birthday',
                        'wedding': 'wedding',
                        'christening': 'christening',
                    }
                    event_type = event_type_map.get(event_type_input, event_type_input)
                    package_images = get_event_package_images(event_type)
                    bot_response = {
                        'sender': 'bot',
                        'text': f"Here are our available packages for {event_type_input.title()}:",
                        'package_options': package_images
                    }
                    request.session['planner_state'] = 'package_image_choice'
                else:
                    # Numbered list for color palettes (if needed)
                    numbered_color_options = '<ul>' + ''.join([f'<li>{i+1}. {c}</li>' for i, c in enumerate(valid_color_palettes + popular_combos)]) + '</ul>'
                    bot_response = {
                        'sender': 'bot',
                        'text': f"Please select from the options given below:{numbered_color_options}"
                    }
            chat_history.append(bot_response)
            request.session['chat_history'] = chat_history
            request.session['planner_data'] = planner_data
            request.session.modified = True
            return render(request, 'main/chatbot.html', {
                'chat_history': chat_history,
                'saved_sessions': ChatSession.objects.all().order_by('-updated_at'),
                'current_title': 'New Chat'
            })

        # Step 5: Package Image Choice (with validation)
        elif planner_state == 'package_image_choice':
            event_type_input = planner_data.get('event_type', '').lower()
            event_type_map = {
                'kiddie party': 'kiddie',
                'birthday party': 'birthday',
                'wedding': 'wedding',
                'christening': 'christening',
            }
            event_type = event_type_map.get(event_type_input, event_type_input)
            package_images = get_event_package_images(event_type)
            package_names = [pkg[0] for pkg in package_images]
            package_selected = None
            # Try number selection first
            try:
                idx = int(user_message.strip()) - 1
                if 0 <= idx < len(package_images):
                    package_selected = idx
                else:
                    package_selected = None
                    # If the input is a number but out of range, do not try fuzzy matching
            except Exception:
                package_selected = None
                # Only try fuzzy/wildcard matching if input is not a number at all
                is_valid, corrected_input, suggestions = validate_and_suggest(lower_msg, package_names, "package")
                if is_valid:
                    package_selected = package_names.index(corrected_input)
            if package_selected is not None and 0 <= package_selected < len(package_images):
                planner_data['package_image'] = package_images[package_selected][1]
                planner_data['package_image_label'] = package_images[package_selected][0]
                bot_response = {
                    'sender': 'bot',
                    'text': f"Which package do you want for {package_images[package_selected][0]}? (Type A, B, or C)",
                    'package_image_selected': package_images[package_selected][1],
                    'package_image_label': package_images[package_selected][0],
                }
                request.session['planner_state'] = 'package_letter_choice'
            else:
                # Numbered list for package options
                numbered_options = '<ul>' + ''.join([f'<li>{i+1}. {name}</li>' for i, name in enumerate(package_names)]) + '</ul>'
                bot_response = {
                    'sender': 'bot',
                    'text': f"Please select from the options given below:{numbered_options}"
                }
            chat_history.append(bot_response)
            request.session['chat_history'] = chat_history
            request.session['planner_data'] = planner_data
            request.session.modified = True
            return render(request, 'main/chatbot.html', {
                'chat_history': chat_history,
                'saved_sessions': ChatSession.objects.all().order_by('-updated_at'),
                'current_title': 'New Chat'
            })

        # Step 6: Package Letter Choice
        elif planner_state == 'package_letter_choice':
            change_commands = [
                'change color', 'choose another color', 'pick a new color', 'switch color', 'change palette', 'pick another color', 'select different color',
                'change package', 'choose another package', 'pick a new package', 'switch package', 'pick another package', 'select different package',
                'change event', 'choose another event', 'pick a new event', 'switch event', 'change event type', 'pick another event', 'select different event',
                'change event type', 'event type', 'change theme', 'choose another theme', 'pick a new theme', 'switch theme', 'pick another theme', 'select different theme',
            ]
            letter = user_message.strip().upper()
            letter_selected = None
            # Strictly accept only A, B, or C
            if letter in ['A', 'B', 'C']:
                letter_selected = letter
            # Allow change commands
            elif any(cmd in user_message.lower() for cmd in change_commands):
                letter_selected = None  # Let the global change logic handle it
            else:
                letter_selected = None
            if letter_selected:
                planner_data['package_letter'] = letter_selected
                planner_data['package_choice'] = f"{planner_data.get('package_image_label', '')} - Package {letter_selected}"
                food_menu_images = get_food_menu_images()
                rules = PACKAGE_RULES[letter_selected]
                rules_text = f"You can choose:<ul><li>{rules['dishes']} dishes</li><li>{rules['pasta']} pasta</li><li>{rules['drinks']} drink</li></ul>Please note that Steamed Rice and Dessert Buffet are already included.<br><br>Review the menu and type OK when you are ready to make your selections."
                bot_response = {
                    'sender': 'bot',
                    'text': rules_text,
                    'food_menu_images': food_menu_images
                }
                request.session['planner_state'] = 'food_menu_review'
            elif any(cmd in user_message.lower() for cmd in change_commands):
                # Let the global change logic handle it (do nothing here)
                pass
            else:
                bot_response = {
                    'sender': 'bot',
                    'text': "Please type A, B, or C for the package letter. Only these letters are accepted.",
                    'package_image_selected': planner_data.get('package_image'),
                    'package_image_label': planner_data.get('package_image_label'),
                }

        # Step 7: Food Menu Review (wait for user to type OK/Ready)
        elif planner_state == 'food_menu_review':
            if user_message.strip().lower() in ['ok', 'ready', 'done', 'go']:
                package_letter = planner_data.get('package_letter')
                rules = PACKAGE_RULES[package_letter]
                bot_response = {
                    'sender': 'bot',
                    'text': f"Please select {rules['dishes']} dishes (type them separated by commas)."
                }
                planner_data['food_selection_state'] = 'dishes'
                planner_data['food_selection'] = {}
                request.session['planner_state'] = 'food_select_dishes'
                request.session['planner_data'] = planner_data
            else:
                food_menu_images = get_food_menu_images()
                bot_response = {
                    'sender': 'bot',
                    'text': 'Please review the food menu above and type OK when you are ready to make your selections.',
                    'food_menu_images': food_menu_images
                }

        # Step 8: Food Select Dishes
        elif planner_state == 'food_select_dishes':
            change_commands = [
                'change color', 'choose another color', 'pick a new color', 'switch color', 'change palette', 'pick another color', 'select different color',
                'change package', 'choose another package', 'pick a new package', 'switch package', 'pick another package', 'select different package',
                'change event', 'choose another event', 'pick a new event', 'switch event', 'change event type', 'pick another event', 'select different event',
                'change event type', 'event type', 'change theme', 'choose another theme', 'pick a new theme', 'switch theme', 'pick another theme', 'select different theme',
            ]
            package_letter = planner_data.get('package_letter')
            rules = PACKAGE_RULES[package_letter]
            dish_cats = ['vegetables', 'beef', 'pork', 'chicken', 'seafood']
            valid_dishes = []
            for cat in dish_cats:
                valid_dishes += get_food_menu(cat)
            
            dishes = [d.strip() for d in user_message.split(',') if d.strip()]
            corrected_dishes = []
            invalid = []
            
            for d in dishes:
                is_valid, corrected_input, suggestions = validate_and_suggest(d.lower(), valid_dishes, "dish")
                if is_valid:
                    corrected_dishes.append(corrected_input)
                else:
                    if suggestions:
                        invalid.append((d, suggestions[0]))
                    else:
                        invalid.append((d, None))

            if any(cmd in user_message.lower() for cmd in change_commands):
                pass  # Let global change logic handle
            elif len(corrected_dishes) != rules['dishes'] or invalid:
                error_msg = f"One or more of your selected dishes are not on the menu or you selected the wrong number. Please choose {rules['dishes']} from the following categories:<br>"
                error_msg += "<ul><li>Vegetables</li><li>Beef</li><li>Pork</li><li>Chicken</li><li>Seafood</li></ul>"
                if invalid:
                    suggestions = []
                    for orig, suggestion in invalid:
                        if suggestion:
                            suggestions.append(f"Did you mean '{suggestion}' for '{orig}'?")
                    if suggestions:
                        error_msg += "<br>" + "<br>".join(suggestions)
                bot_response = {
                    'sender': 'bot',
                    'text': error_msg
                }
            else:
                planner_data['food_selection']['dishes'] = corrected_dishes
                bot_response = {
                    'sender': 'bot',
                    'text': f"Please select {rules['pasta']} pasta (type it)."
                }
                request.session['planner_state'] = 'food_select_pasta'
                request.session['planner_data'] = planner_data

        # Step 9: Food Select Pasta
        elif planner_state == 'food_select_pasta':
            change_commands = [
                'change color', 'choose another color', 'pick a new color', 'switch color', 'change palette', 'pick another color', 'select different color',
                'change package', 'choose another package', 'pick a new package', 'switch package', 'pick another package', 'select different package',
                'change event', 'choose another event', 'pick a new event', 'switch event', 'change event type', 'pick another event', 'select different event',
                'change event type', 'event type', 'change theme', 'choose another theme', 'pick a new theme', 'switch theme', 'pick another theme', 'select different theme',
            ]
            package_letter = planner_data.get('package_letter')
            rules = PACKAGE_RULES[package_letter]
            valid_pasta = get_food_menu('pasta')
            valid_pasta_lower = [p.lower() for p in valid_pasta]
            pasta = [p.strip() for p in user_message.split(',') if p.strip()]
            corrected_pasta = []
            invalid = []
            for p in pasta:
                match, score = get_fuzzy_match(p.lower(), valid_pasta_lower)
                if match and score >= 80:
                    corrected_pasta.append(valid_pasta[valid_pasta_lower.index(match)])
                else:
                    # Try to find a close match for suggestion
                    close_match, close_score = get_fuzzy_match(p.lower(), valid_pasta_lower)
                    if close_match and close_score >= 60:
                        invalid.append((p, valid_pasta[valid_pasta_lower.index(close_match)]))
                    else:
                        invalid.append((p, None))

            if any(cmd in user_message.lower() for cmd in change_commands):
                pass
            elif len(corrected_pasta) != rules['pasta'] or invalid:
                error_msg = f"One or more of your selected pasta are not on the menu or you selected the wrong number. Please select {rules['pasta']} pasta from the menu."
                # Add suggestions for invalid pasta
                if invalid:
                    suggestions = []
                    for orig, suggestion in invalid:
                        if suggestion:
                            suggestions.append(f"Did you mean '{suggestion}' for '{orig}'?")
                    if suggestions:
                        error_msg += "<br>" + "<br>".join(suggestions)
                bot_response = {
                    'sender': 'bot',
                    'text': error_msg
                }
            else:
                planner_data['food_selection']['pasta'] = corrected_pasta
                bot_response = {
                    'sender': 'bot',
                    'text': f"Please select {rules['drinks']} drink (type it)."
                }
                request.session['planner_state'] = 'food_select_drink'
                request.session['planner_data'] = planner_data

        # Step 10: Food Select Drink
        elif planner_state == 'food_select_drink':
            change_commands = [
                'change color', 'choose another color', 'pick a new color', 'switch color', 'change palette', 'pick another color', 'select different color',
                'change package', 'choose another package', 'pick a new package', 'switch package', 'pick another package', 'select different package',
                'change event', 'choose another event', 'pick a new event', 'switch event', 'change event type', 'pick another event', 'select different event',
                'change event type', 'event type', 'change theme', 'choose another theme', 'pick a new theme', 'switch theme', 'pick another theme', 'select different theme',
            ]
            package_letter = planner_data.get('package_letter')
            rules = PACKAGE_RULES[package_letter]
            valid_drinks = get_food_menu('drinks')
            valid_drinks_lower = [d.lower() for d in valid_drinks]
            drinks = [d.strip() for d in user_message.split(',') if d.strip()]
            corrected_drinks = []
            invalid = []
            for d in drinks:
                match, score = get_fuzzy_match(d.lower(), valid_drinks_lower)
                if match and score >= 80:
                    corrected_drinks.append(valid_drinks[valid_drinks_lower.index(match)])
                else:
                    # Try to find a close match for suggestion
                    close_match, close_score = get_fuzzy_match(d.lower(), valid_drinks_lower)
                    if close_match and close_score >= 60:
                        invalid.append((d, valid_drinks[valid_drinks_lower.index(close_match)]))
                    else:
                        invalid.append((d, None))

            if any(cmd in user_message.lower() for cmd in change_commands):
                pass
            elif len(corrected_drinks) != rules['drinks'] or invalid:
                error_msg = f"One or more of your selected drinks are not on the menu or you selected the wrong number. Please select {rules['drinks']} drink from the menu."
                # Add suggestions for invalid drinks
                if invalid:
                    suggestions = []
                    for orig, suggestion in invalid:
                        if suggestion:
                            suggestions.append(f"Did you mean '{suggestion}' for '{orig}'?")
                    if suggestions:
                        error_msg += "<br>" + "<br>".join(suggestions)
                bot_response = {
                    'sender': 'bot',
                    'text': error_msg
                }
            else:
                planner_data['food_selection']['drinks'] = corrected_drinks
                bot_response = {
                    'sender': 'bot',
                    'text': "Type 'finish' or 'done' to see the summary of your event plan."
                }
                request.session['planner_state'] = 'food_select_finish'
                request.session['planner_data'] = planner_data

        # Step 11: Food Select Finish
        elif planner_state == 'food_select_finish':
            if user_message.strip().lower() in ['finish', 'done']:
                selected = planner_data['food_selection']
                # Get summary images
                package_image = planner_data.get('package_image')
                theme = planner_data.get('theme')
                images = get_theme_images(theme) if theme else []
                ai_image = generate_ai_theme_image(theme) if theme else None
                theme_image_choice = planner_data.get('theme_image_choice', 'given')
                if theme_image_choice == 'ai':
                    theme_image = ai_image
                else:
                    theme_image = images[0] if images else None
                # Prepare summary lines for template
                summary_lines = []
                summary_lines.append({'type': 'text', 'value': f"Event type: {planner_data.get('event_type', 'N/A').title()}"})
                summary_lines.append({'type': 'theme', 'value': f"Theme: {planner_data.get('theme', 'N/A').title()}", 'img': theme_image})
                summary_lines.append({'type': 'text', 'value': f"Color palette: {planner_data.get('color_palette', 'N/A')}"})
                summary_lines.append({'type': 'package', 'value': f"Package: {planner_data.get('package_choice', 'N/A')}", 'img': package_image})
                summary_lines.append({'type': 'text', 'value': "Food Selection:"})
                summary_lines.append({'type': 'text', 'value': f"Dishes: {', '.join(selected['dishes'])}"})
                summary_lines.append({'type': 'text', 'value': f"Pasta: {', '.join(selected['pasta'])}"})
                summary_lines.append({'type': 'text', 'value': f"Drinks: {', '.join(selected['drinks'])}"})
                summary_lines.append({'type': 'text', 'value': "Rice: Steamed Rice"})
                summary_lines.append({'type': 'text', 'value': "Dessert: Dessert Buffet"})
                bot_response = {
                    'sender': 'bot',
                    'text': "Here is a summary of your event plan:",
                    'summary_lines': summary_lines,
                }
                request.session['planner_state'] = 'start'
                request.session['planner_data'] = {}
            else:
                bot_response = {
                    'sender': 'bot',
                    'text': "Type 'finish' or 'done' to see the summary of your event plan."
                }

        # New Step: Theme Image Choice
        elif planner_state == 'theme_image_choice':
            ai_match, ai_score = get_fuzzy_match(lower_msg, ['ai'])
            given_match, given_score = get_fuzzy_match(lower_msg, ['given'])
            if (ai_match and ai_score >= 80) or wildcard_match('*ai*', lower_msg):
                planner_data['theme_image_choice'] = 'ai'
                theme = planner_data.get('theme')
                images = get_theme_images(theme) if theme else []
                ai_image = generate_ai_theme_image(theme) if theme else None
                images_to_show = [ai_image] if ai_image else []
                bot_response = {
                    'sender': 'bot',
                    'text': "Would you like to use the default color palette for this theme, or do you want to modify the colors? (Type 'default' or specify your colors.)",
                    'selected_theme_images': images_to_show,
                    'theme_confirm_name': theme.title() if theme else '',
                }
                request.session['planner_state'] = 'color_palette_confirm'
            elif (given_match and given_score >= 80) or wildcard_match('*given*', lower_msg):
                planner_data['theme_image_choice'] = 'given'
                theme = planner_data.get('theme')
                images = get_theme_images(theme) if theme else []
                ai_image = generate_ai_theme_image(theme) if theme else None
                images_to_show = images
                bot_response = {
                    'sender': 'bot',
                    'text': "Would you like to use the default color palette for this theme, or do you want to modify the colors? (Type 'default' or specify your colors.)",
                    'selected_theme_images': images_to_show,
                    'theme_confirm_name': theme.title() if theme else '',
                }
                request.session['planner_state'] = 'color_palette_confirm'
            else:
                # Reprompt if invalid input
                theme = planner_data.get('theme')
                images = get_theme_images(theme) if theme else []
                ai_image = generate_ai_theme_image(theme) if theme else None
                bot_response = {
                    'sender': 'bot',
                    'text': "Please select from the options given below:<ul><li>ai</li><li>given</li></ul>",
                    'theme_confirm_images': images,
                    'theme_confirm_name': theme.title() if theme else '',
                    'ai_generated_image': ai_image,
                }
            chat_history.append(bot_response)
            request.session['chat_history'] = chat_history
            request.session['planner_data'] = planner_data
            request.session.modified = True
            return render(request, 'main/chatbot.html', {
                'chat_history': chat_history,
                'saved_sessions': ChatSession.objects.all().order_by('-updated_at'),
                'current_title': 'New Chat'
            })

        # Fallback: always guide to start
        if bot_response is None:
            bot_response = {
                'sender': 'bot',
                'text': "What type of event would you like to plan? (Kiddie Party, Birthday Party, Wedding, or Christening)"
            }
            request.session['planner_state'] = 'event_type'

        chat_history.append(bot_response)
        request.session['chat_history'] = chat_history
        request.session['planner_data'] = planner_data
        request.session.modified = True

    # Auto-generate a title for the chat session based on the first user message
    if chat_history and len(chat_history) > 1:
        first_user_msg = next((msg['text'] for msg in chat_history if msg['sender'] == 'user'), None)
        if first_user_msg:
            title = f"Chat: {first_user_msg[:30]}..."
        else:
            title = "New Chat"
    else:
        title = "New Chat"

    # Fetch saved chat sessions for the sidebar
    saved_sessions = ChatSession.objects.all().order_by('-updated_at')

    # Find the current session id by matching chat_history
    current_session_id = None
    for session in saved_sessions:
        if session.chat_history == chat_history:
            current_session_id = session.id
            break

    return render(request, 'main/chatbot.html', {
        'chat_history': chat_history,
        'saved_sessions': saved_sessions,
        'current_title': title,
        'current_session_id': current_session_id
    })

def save_chat_session(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        chat_history = request.session.get('chat_history', [])
        title = get_first_user_message(chat_history)
        planner_state = request.session.get('planner_state', 'start')
        planner_data = request.session.get('planner_data', {})
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

def delete_chat_session(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id)
    session.delete()
    return JsonResponse({'status': 'success'})

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
