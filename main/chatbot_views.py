import re
from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static
from django.http import JsonResponse
from .models import ChatSession
import json
from fuzzywuzzy import process

def get_faq_categories():
    """Return all FAQ categories for Nike's Catering Services"""
    return [
        'general', 'booking', 'payment', 'cancellation', 'services', 'packages', 'food', 'themes', 'pricing', 'contact'
    ]

def get_faq_questions(category):
    """Return FAQ questions and answers for a specific category"""
    faq_data = {
        'general': {
            'what is nikes catering services': "Nike's Catering Services is a premier catering company specializing in events like birthdays, weddings, christenings, and kiddie parties. We provide complete event planning, food preparation, setup, and decoration services.",
            'where are you located': "We are located in [City/Area]. We provide catering services throughout [Region] and surrounding areas.",
            'how long have you been in business': "We have been serving our community with exceptional catering services since 2014, building a reputation for quality, reliability, and creativity.",
            'what makes you different from other caterers': "We stand out through our personalized service, creative themes, high-quality food, professional staff, and attention to detail. We treat every event as unique and special.",
            'do you have insurance and permits': "Yes, we are fully licensed, insured, and comply with all health and safety regulations required for catering services."
        },
        'booking': {
            'how do i book an event': "You can book an event by contacting us through our website.",
            'how far in advance should i book': "We recommend booking at least 2 weeks in advance for small events and atleast 3 months for larger events like weddings. Popular dates fill up quickly, so early booking is advised.",
            'what information do you need for booking': "We'll need your event date, time, location, expected guest count, event type, theme preferences, and any special dietary requirements or requests.",
            'do you require a deposit': "Yes, we require a down payment to secure your booking. The amount varies based on event size and package selected. We require a minum of 10,000 pesos or 20% downpayment for your booking confirmation.",
            'can i change my event details after booking': "Yes, you can make changes to your event details up to 3 weeks before the event, subject to availability and any additional costs."
        },
        'payment': {
            'what are your payment options': "We accept cash, GCash, bank transfers, and other digital payment methods. Payment plans can be arranged for larger events.",
            'when is payment due': "A deposit is required upon booking, with the remaining balance due 1 week before the event. Final payment is due on or before the event day.",
            'do you offer payment plans': "Yes, we offer flexible payment plans for larger events. We can work with you to create a payment schedule that fits your budget.",
            'are there any hidden fees': "No hidden fees. All costs are clearly outlined in your quote, including setup, service, and cleanup fees.",
            'do you provide receipts': "Yes, we provide detailed receipts for all payments and can issue invoices for business clients."
        },
        'cancellation': {
            'what is your cancellation policy': "All down payment fees made for reservations are forfeited upon cancellation. Reservation fees are non-refundable, non-transferable, and non-convertible.",
            'can i reschedule my event': "If the client needs to reschedule the reservation date due to unforeseen events or circumstances, the client must provide us with as much early notice as possible of the rebooking. Rebooking and/or damage fees may apply.",
            'what happens if i cancel last minute': "Cancellations within 48 hours of the event will result in full payment being due, as we cannot recover costs for last-minute cancellations.",
            'do you offer refunds': "Deposits and reservation fees are non-refundable as per our cancellation policy. We recommend event insurance for additional protection.",
            'what if there is bad weather': "We work with you to create a backup plan for outdoor events. In case of severe weather, we can reschedule or move to an indoor location if available."
        },
        'services': {
            'what services do you provide': "We provide complete event services including food preparation, setup and decoration, serving staff, cleanup, theme coordination, and event planning assistance.",
            'do you provide staff': "Yes, we provide professional serving staff, chefs, and setup crew. Staff numbers are determined by guest count and service level.",
            'do you handle setup and cleanup': "Yes, we handle all setup before the event and cleanup afterward. This includes tables, chairs, decorations, and food service areas.",
            'do you provide decorations': "Yes, we provide decorations based on your chosen theme. We can also work with your existing decorations or coordinate with your decorator.",
            'do you provide tableware and linens': "Yes, we provide all necessary tableware, linens, and serving pieces. We can also coordinate with your existing items if preferred."
        },
        'packages': {
            'what packages do you offer': "We offer various packages for different event types: Birthday Parties and Kiddie Parties  (50-200 pax), Weddings (50-250 pax), and Christenings (50-200 pax). For custom events, we have package for below 100 and up",
            'what is included in your packages': "Our packages include food, beverages, setup, decoration, serving staff, and cleanup.",
            'can i customize a package': "Yes, we can customize packages to meet your specific needs. We can add or remove items, adjust portions, or create a completely custom menu.",
            'do you offer vegetarian options': "Yes, we offer vegetarian and vegan options. We can accommodate various dietary restrictions and preferences.",
            'what about dietary restrictions': "We can accommodate various dietary restrictions including vegetarian, vegan, gluten-free, and allergy-specific requirements. Please inform us of any special needs during booking."
        },
        'food': {
            'what type of food do you serve': "We serve a wide variety of Filipino and international cuisine including beef, pork, chicken, seafood, vegetables, pasta, and desserts. Our menu can be customized to your preferences.",
            'is the food prepared fresh': "Yes, all our food is prepared fresh on the day of your event. We use high-quality ingredients and follow strict food safety guidelines.",
            'can you accommodate special dietary needs': "Yes, we can accommodate various dietary restrictions including vegetarian, vegan, gluten-free, and allergy-specific requirements.",
            'do you provide tastings': "Yes, we offer food tastings for larger events like weddings every weekend of the month. This allows you to sample our menu and make final selections.",
            'what about food allergies': "We take food allergies seriously and can accommodate most allergy requirements. Please inform us of any allergies during booking.",
            'do you provide beverages': "Yes, we provide a selection of beverages including juices, soft drinks, and water. We can also coordinate with your preferred beverage provider.",
            'can you provide alcohol': "We can coordinate alcohol service, but you'll need to provide the alcohol and obtain necessary permits. We can recommend licensed bartenders."
        },
        'themes': {
            'what themes do you offer': "We offer a wide variety of themes including Disney, Movie, Gaming, Superhero, Sports, Animal, Color, Special Occasions, and more. We can also create custom themes.",
            'can i customize a theme': "Yes, you can customize themes to match your vision. We can modify colors to create your perfect theme. For default themes that our team already created, please ask the admin for more information.",
            'do you provide themed decorations': "Yes, we provide themed decorations that match your chosen theme. This includes table settings, centerpieces, and venue decorations.",
            'can you work with my existing decorations': "Absolutely! We can incorporate your existing decorations with our theme or coordinate with your decorator. Just inform our admin after creating a booking.",
            'do you offer seasonal themes': "Yes, we offer seasonal themes for holidays and special occasions throughout the year."
        },
        'pricing': {
            'how much do your services cost': "Our pricing varies based on event type, guest count, package selection, and customization requirements. We provide detailed quotes after booking.",
            'what factors affect pricing': "Pricing is affected by guest count, food selection, service level, theme complexity, location, and any special requirements.",
            'do you offer discounts': "We offer discounts for large events, repeat customers, and off-peak dates. We can also work with your budget to create a suitable package.",
            'are there additional fees': "Additional fees may apply for special requests, extended service hours, or additional staff. All fees are clearly outlined in your quote.",
            'do you offer package deals': "Yes, we offer package deals that provide better value than selecting services individually. Our packages are designed to meet common event needs."
        },
        'contact': {
            'how can i contact you': "You can contact us through our website after creating a booking. The admin responds within 24 hours.",
            'what are your business hours': "Our website work 24/7. Create a booking and the admin responds within 24 hours.",
            'do you offer consultations': "Yes, we offer free consultations to discuss your event needs and provide recommendations. Consultations will work after creating a booking.",
            'how quickly do you respond to inquiries': "We aim to respond to all inquiries within 24 hours.",
            'can i visit your kitchen': "We have food tastings that happen every weekend of the month. Visiting the kitchen itself is prohibited."
        }
    }
    return faq_data.get(category.lower(), {})

def get_faq_suggestions(user_input):
    """Get FAQ suggestions based on user input"""
    all_questions = []
    all_categories = get_faq_categories()
    
    for category in all_categories:
        questions = get_faq_questions(category)
        all_questions.extend(questions.keys())
    
    # Find best matches with a lower threshold for better typo tolerance
    matches = process.extract(user_input.lower(), all_questions, limit=3)
    return [match[0] for match in matches if match[1] >= 40]  # Lowered from 60 to 40

def detect_category_only_request(user_input):
    """Return a category name if the message is basically asking about a category
    (e.g., "packages", "about packages"), otherwise return None.
    """
    lower_msg = user_input.lower()
    words = re.findall(r"\w+", lower_msg)
    if not words:
        return None

    filler_words = {
        'about', 'info', 'information', 'details', 'category', 'categories',
        'question', 'questions', 'on', 'regarding', 'tell', 'me', 'show', 'list', 'the'
    }

    for category in get_faq_categories():
        if category in words:
            other_words = [w for w in words if w != category]
            if all(w in filler_words for w in other_words):
                return category
    
    # Fuzzy catch: very short or single-word inputs that are close to a category name
    if len(words) <= 3 and len(lower_msg) <= 20:
        match = process.extractOne(lower_msg, get_faq_categories())
        if match and match[1] >= 85:
            return match[0]
    return None

def get_referenced_categories(user_input):
    """Return categories referenced in the text using direct mentions or synonyms."""
    text = user_input.lower()
    synonym_map = {
        'packages': ['package', 'packages', 'pax'],
        'pricing': ['price', 'pricing', 'cost', 'rate', 'rates', 'fee', 'fees'],
        'booking': ['book', 'booking', 'reserve', 'reservation', 'schedule'],
        'payment': ['pay', 'payment', 'payments', 'deposit', 'downpayment'],
        'cancellation': ['cancel', 'cancellation', 'refund', 'reschedule', 'rebook'],
        'themes': ['theme', 'themes', 'motif'],
        'food': ['food', 'menu', 'beverage', 'drinks', 'alcohol'],
        'services': ['service', 'services', 'staff', 'setup', 'decoration'],
        'contact': ['contact', 'reach', 'message'],
        'general': ['about', 'info', 'information']
    }

    referenced = []
    for category, keywords in synonym_map.items():
        # Exact substring hit
        if any(kw in text for kw in keywords):
            referenced.append(category)
            continue
        # Fuzzy match for short inputs or typos (e.g., "boking" ~ booking)
        if len(text.split()) <= 3 and len(text) <= 30:
            match = process.extractOne(text, keywords + [category])
            if match and match[1] >= 85:
                referenced.append(category)
    return referenced

def normalize_question_by_category(user_input, category):
    """Map common phrasings to a canonical FAQ question within a category."""
    text = user_input.lower()

    if category == 'packages':
        if any(w in text for w in ['see', 'show', 'list', 'available', 'options']):
            return 'what packages do you offer'
        if any(w in text for w in ['include', 'included', 'includes', 'inside', 'content', 'contents']):
            return 'what is included in your packages'
        if 'custom' in text or 'customize' in text or 'customise' in text:
            return 'can i customize a package'
        if any(w in text for w in ['vegetarian', 'vegan']):
            return 'do you offer vegetarian options'
        if any(w in text for w in ['diet', 'restriction', 'restrictions', 'allergy', 'allergies']):
            return 'what about dietary restrictions'

    if category == 'pricing':
        if any(w in text for w in ['price', 'pricing', 'cost', 'rate', 'rates', 'how much']):
            return 'how much do your services cost'
        if any(w in text for w in ['discount', 'discounts', 'promo', 'promotion']):
            return 'do you offer discounts'
        if 'fee' in text or 'fees' in text:
            return 'are there additional fees'
        if 'deal' in text or 'package deal' in text:
            return 'do you offer package deals'

    if category == 'booking':
        if any(w in text for w in ['change', 'modify', 'edit']):
            return 'can i change my event details after booking'
        if any(w in text for w in ['book', 'reserve', 'schedule']):
            return 'how do i book an event'

    return None

def find_best_faq_match(user_input, questions):
    """Find the best matching FAQ question using multiple strategies"""
    user_input_lower = user_input.lower().strip()
    user_words = set(user_input_lower.split())
    
    # Skip very short inputs that are likely greetings
    if len(user_input_lower) < 10 and len(user_words) <= 2:
        # Check if it's just a greeting or very short input
        greetings = {'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'morning', 'afternoon', 'evening'}
        if user_input_lower in greetings or any(greeting in user_input_lower for greeting in greetings):
            return None, 0
    
    best_match = None
    best_score = 0
    
    for question in questions.keys():
        question_words = set(question.lower().split())
        
        # Strategy 1: Exact word matching (but require meaningful matches)
        common_words = user_words.intersection(question_words)
        # Filter out very common words that don't add meaning
        meaningful_words = {word for word in common_words if len(word) > 2 and word not in {
            'the', 'and', 'or', 'for', 'with', 'from', 'about', 'what', 'how', 'when', 'where', 'why', 'do', 'you', 'your', 'are', 'is', 'can', 'will', 'have', 'has', 'had', 'does', 'did'
        }}
        
        if len(meaningful_words) >= 2:  # At least 2 meaningful words must match
            score = len(meaningful_words) / max(len(user_words), len(question_words))
            if score > best_score:
                best_score = score
                best_match = question
        
        # Strategy 2: Fuzzy matching for individual words (but only for longer words)
        for user_word in user_words:
            if len(user_word) > 3:  # Only check words longer than 3 characters
                for question_word in question_words:
                    if len(question_word) > 3:
                        # Use fuzzy matching for individual words
                        similarity = process.fuzz.ratio(user_word.lower(), question_word.lower())
                        if similarity >= 75:  # Higher threshold for word-level similarity
                            score = similarity / 100.0
                            if score > best_score:
                                best_score = score
                                best_match = question
                                break
    
    # Strategy 3: Overall fuzzy matching as fallback (but with higher threshold)
    if not best_match or best_score < 0.4:  # Increased threshold
        overall_matches = process.extract(user_input_lower, questions.keys(), limit=1)
        if overall_matches and overall_matches[0][1] >= 65:  # Higher threshold for overall matching
            best_match = overall_matches[0][0]
            best_score = overall_matches[0][1] / 100.0
    
    return best_match, best_score

def chatbot_view(request):
    # Always start fresh if session is new or uninitialized
    if not request.session.get('initialized', False):
        request.session['chat_history'] = [
            {'sender': 'bot', 'text': "Welcome to Nike's Catering Services! I'm your virtual assistant. How can I help you today? Feel free to ask me anything about our services, packages, pricing, booking, themes, food options, or any other questions you might have about our catering services."}
        ]
        request.session['initialized'] = True
        request.session.modified = True

    chat_history = request.session.get('chat_history', [])

    if request.method == 'POST':
        user_message = request.POST.get('message')
        chat_history.append({'sender': 'user', 'text': user_message})
        lower_msg = user_message.lower().strip()

        bot_response = None

        # Handle restart command
        if any(keyword in lower_msg for keyword in ['restart', 'start over', 'reset', 'new chat', 'clear']):
            request.session.flush()
            bot_response = {
                'sender': 'bot',
                'text': "Welcome to Nike's Catering Services! I'm your virtual assistant. How can I help you today? Feel free to ask me anything about our services, packages, pricing, booking, themes, food options, or any other questions you might have about our catering services."
            }
            request.session['initialized'] = True
            chat_history = [bot_response]
            request.session['chat_history'] = chat_history
            request.session.modified = True
            return render(request, 'chatbot/main/chatbot.html', {
                'chat_history': chat_history,
                'saved_sessions': ChatSession.objects.all().order_by('-updated_at'),
                'current_title': 'New Chat'
            })

        # Handle help command
        if any(keyword in lower_msg for keyword in ['help', 'what can you do', 'commands', 'options']):
            categories = get_faq_categories()
            category_list = '<ul>' + ''.join([f'<li>{cat.title()}</li>' for cat in categories]) + '</ul>'
            bot_response = {
                'sender': 'bot',
                'text': f"I can help you with information about Nike's Catering Services. Here are the main topics I can assist with:{category_list}You can ask me specific questions about any of these areas, or just type your question naturally!"
            }

        # Handle greetings
        elif any(keyword in lower_msg for keyword in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'morning', 'afternoon', 'evening']):
            bot_response = {
                'sender': 'bot',
                'text': "Hello! Welcome to Nike's Catering Services. I'm here to help you with any questions about our catering services, packages, pricing, booking, themes, or food options. How can I assist you today?"
            }

        # Handle direct theme requests (e.g., "mickey", "barbie", "show avengers")
        elif any(keyword in lower_msg for keyword in ['show', 'see', 'sample', 'samples', 'image', 'images', 'picture', 'pictures', 'gallery', 'photo', 'photos']) or any(theme in lower_msg for theme in ['mickey', 'barbie', 'avengers', 'frozen', 'cinderella', 'spongebob', 'mario', 'basketball', 'pink', 'green', 'halloween', 'wedding']):
            print(f"[DEBUG] Theme detection triggered for: {lower_msg}")
            
            # Simple test for "mickey" to see if images work
            if 'mickey' in lower_msg:
                print(f"[DEBUG] Mickey detected, testing image display")
                test_images = [
                    'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1/mickey1_tjr7h0.jpg',
                    'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1/mickey2_pxslgt.jpg',
                    'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1/mickey3_qiya8u.jpg'
                ]
                bot_response = {
                    'sender': 'bot',
                    'text': "Here are sample images for the Mickey theme!",
                    'images': test_images
                }
                print(f"[DEBUG] Test response created with {len(test_images)} images")
            else:
                from .utils import get_available_theme_names, get_theme_images, get_fuzzy_match
                all_themes = get_available_theme_names()
                print(f"[DEBUG] Available themes: {all_themes[:5]}...")
                theme_match, score = get_fuzzy_match(lower_msg, all_themes, threshold=75)
                print(f"[DEBUG] Theme match result: {theme_match} with score {score}")
                
                if theme_match:
                    print(f"[DEBUG] Getting images for theme: {theme_match}")
                    imgs = get_theme_images(theme_match)
                    print(f"[DEBUG] Images returned: {len(imgs) if imgs else 0} images")
                    if imgs:
                        bot_response = {
                            'sender': 'bot',
                            'text': f"Here are sample images for the {theme_match.title()} theme.",
                            'images': imgs
                        }
                    else:
                        bot_response = {
                            'sender': 'bot',
                            'text': f"I found the {theme_match.title()} theme, but I'm having trouble loading the images right now. Please try again later."
                        }
                else:
                    # If no specific theme matched, show available themes
                    examples = ', '.join([name.title() for name in all_themes[:8]])
                    bot_response = {
                        'sender': 'bot',
                        'text': f"I can show you sample images for many themes! Try typing a specific theme name like: {examples}. You can also type 'show mickey' or 'see barbie' to view specific theme images."
                    }

        # Handle category requests
        elif any(keyword in lower_msg for keyword in ['show categories', 'list categories', 'what topics', 'categories']):
            categories = get_faq_categories()
            category_list = '<ul>' + ''.join([f'<li>{cat.title()}</li>' for cat in categories]) + '</ul>'
            bot_response = {
                'sender': 'bot',
                'text': f"Here are the main categories I can help you with:{category_list}Ask me about any specific category or just ask your question directly!"
            }

        else:
            # Try answering within categories explicitly referenced in the message first
            prioritized_categories = get_referenced_categories(user_message)
            all_categories = get_faq_categories()
            remaining_categories = [c for c in all_categories if c not in prioritized_categories]

            found_answer = False

            # 1) Category-only request -> list questions for that category
            category_only = detect_category_only_request(user_message)
            if category_only:
                if category_only == 'themes':
                    # Special handling for themes - show both FAQ questions AND theme categories
                    from .utils import get_available_theme_names
                    theme_names = get_available_theme_names()
                    
                    # Get FAQ questions for themes
                    questions = get_faq_questions('themes')
                    question_list = '<ul>' + ''.join([f'<li>{q.replace("_", " ").title()}</li>' for q in questions.keys()]) + '</ul>'
                    
                    # Show theme categories
                    theme_categories = [
                        'Disney', 'Movie', 'Gaming',
                        'Superhero', 'Sports', 'Animals',
                        'Colors', 'Special Themes', 'Other Popular Themes'
                    ]
                    theme_list = '<ul>' + ''.join([f'<li>{cat}</li>' for cat in theme_categories]) + '</ul>'
                    examples = ', '.join([name.title() for name in theme_names[:8]])
                    
                    bot_response = {
                        'sender': 'bot',
                        'text': f"Here are some common questions about Themes:{question_list}<br><br>Here are our theme categories:{theme_list}<br><br>We have many themes including: {examples}<br><br>To see sample images for a specific theme, type the theme name like 'mickey', 'show avengers', or 'see barbie'."
                    }
                else:
                    questions = get_faq_questions(category_only)
                    question_list = '<ul>' + ''.join([f'<li>{q.replace("_", " ").title()}</li>' for q in questions.keys()]) + '</ul>'
                    bot_response = {
                        'sender': 'bot',
                        'text': f"Here are some common questions about {category_only.title()}:{question_list}Ask me any of these questions or ask something else!"
                    }
                found_answer = True

            # 2) If not just a category, try normalized question inside referenced categories
            if not found_answer and prioritized_categories:
                for category in prioritized_categories:
                    # Special: theme image flow if user asks to see/show samples
                    if category == 'themes':
                        from .utils import get_available_theme_names, get_theme_images, get_fuzzy_match
                        lower_text = user_message.lower()
                        wants_samples = any(k in lower_text for k in ['show', 'see', 'sample', 'samples', 'image', 'images', 'picture', 'pictures', 'gallery', 'photo', 'photos'])
                        all_themes = get_available_theme_names()
                        theme_match, score = get_fuzzy_match(lower_text, all_themes, threshold=75)
                        if theme_match and (wants_samples or 'theme' in lower_text or 'themes' in lower_text):
                            imgs = get_theme_images(theme_match)
                            if imgs:
                                bot_response = {
                                    'sender': 'bot',
                                    'text': f"Here are sample images for the {theme_match.title()} theme.",
                                    'images': imgs
                                }
                                found_answer = True
                                break
                        # If they are in theme context but no theme matched, offer prompt with examples
                        if 'themes' in prioritized_categories and not wants_samples and not found_answer:
                            examples = ', '.join([name.title() for name in all_themes[:8]])
                            bot_response = {
                                'sender': 'bot',
                                'text': f"We have many theme categories. Would you like to see samples for a specific one? For example: {examples}. You can type 'show avengers' or 'see barbie'."
                            }
                            found_answer = True
                            break

                    questions = get_faq_questions(category)
                    normalized = normalize_question_by_category(user_message, category)
                    if normalized and normalized in questions:
                        bot_response = {
                            'sender': 'bot',
                            'text': questions[normalized]
                        }
                        # Add theme follow-up prompt if applicable
                        if category == 'themes':
                            from .utils import get_available_theme_names
                            examples = ', '.join([name.title() for name in get_available_theme_names()[:6]])
                            bot_response['text'] += f"<br><br>Would you like to see sample images for a theme? For example: {examples}. You can type 'show avengers' or 'see barbie'."
                        found_answer = True
                        break

            # 3) If still no answer, try best-match inside referenced categories first
            if not found_answer:
                for category in prioritized_categories + remaining_categories:
                    questions = get_faq_questions(category)
                    best_match, match_score = find_best_faq_match(user_message, questions)
                    if best_match and match_score >= 0.5:
                        text = questions[best_match]
                        # If this came from themes, append the prompt to view sample images
                        if category == 'themes':
                            from .utils import get_available_theme_names
                            examples = ', '.join([name.title() for name in get_available_theme_names()[:6]])
                            text += f"<br><br>Would you like to see sample images for a theme? For example: {examples}. You can type 'show avengers' or 'see barbie'."
                        bot_response = {
                            'sender': 'bot',
                            'text': text
                        }
                        found_answer = True
                        break

            # 4) Suggestions fallback
            if not found_answer:
                suggestions = get_faq_suggestions(user_message)
                if suggestions:
                    suggestion_text = "I didn't find an exact match, but here are some related questions you might want to ask:\n"
                    suggestion_text += '<ul>' + ''.join([f'<li>{s.replace("_", " ").title()}</li>' for s in suggestions]) + '</ul>'
                    suggestion_text += "Or you can ask me about our services, packages, pricing, or booking process, You can also type 'help' to see what I can assist you with."
                    bot_response = {
                        'sender': 'bot',
                        'text': suggestion_text
                    }
                else:
                    bot_response = {
                        'sender': 'bot',
                        'text': "I'm not sure I understand your question. You can ask me about our catering services, packages, pricing, booking, or any other specific questions. You can also type 'help' to see what I can assist you with."
                    }

        # Add bot response to chat history
        if bot_response:
            chat_history.append(bot_response)
            request.session['chat_history'] = chat_history
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

    return render(request, 'chatbot/main/chatbot.html', {
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
        user = request.user if request.user.is_authenticated else None
        session = ChatSession.objects.create(
            title=title,
            chat_history=chat_history,
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
    request.session.modified = True
    return redirect('chatbot')

def delete_chat_session(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id)
    session.delete()
    return JsonResponse({'status': 'success'})

def new_chat_session(request):
    request.session.pop('chat_history', None)
    request.session.pop('initialized', None)
    request.session.modified = True
    return redirect('chatbot')

def get_first_user_message(chat_history):
    for msg in chat_history:
        if msg.get('sender') == 'user' and msg.get('text'):
            return msg['text']
    return 'New Chat'

# API endpoints for mobile app
def api_chatbot_message(request):
    """API endpoint for mobile app to send messages to chatbot"""
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
            
        # Initialize chat history if not exists
        if not request.session.get('initialized', False):
            request.session['chat_history'] = [
                {'sender': 'bot', 'text': "Welcome to Nike's Catering Services! I'm your virtual assistant. How can I help you today? Feel free to ask me anything about our services, packages, pricing, booking, themes, food options, or any other questions you might have about our catering services."}
            ]
            request.session['initialized'] = True
            request.session.modified = True

        chat_history = request.session.get('chat_history', [])
        chat_history.append({'sender': 'user', 'text': user_message})
        
        # Generate bot response using existing logic
        bot_response = generate_bot_response(user_message, chat_history)
        chat_history.append({'sender': 'bot', 'text': bot_response})
        
        request.session['chat_history'] = chat_history
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'bot_response': bot_response,
            'chat_history': chat_history
        })
    
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)

def generate_bot_response(user_message, chat_history):
    """Generate bot response using existing chatbot logic"""
    lower_msg = user_message.lower().strip()
    
    # Handle restart command
    if any(keyword in lower_msg for keyword in ['restart', 'start over', 'reset', 'new chat', 'clear']):
        return "Welcome to Nike's Catering Services! I'm your virtual assistant. How can I help you today? Feel free to ask me anything about our services, packages, pricing, booking, themes, food options, or any other questions you might have about our catering services."

    # Handle help command
    if any(keyword in lower_msg for keyword in ['help', 'what can you do', 'commands', 'options']):
        categories = get_faq_categories()
        category_list = '\n• ' + '\n• '.join([cat.title() for cat in categories])
        return f"I can help you with information about Nike's Catering Services. Here are the main topics I can assist with:{category_list}\n\nYou can ask me specific questions about any of these areas, or just type your question naturally!"

    # Handle greetings
    if any(keyword in lower_msg for keyword in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
        return "Hello! Welcome to Nike's Catering Services. I'm here to help you with any questions about our catering services, packages, pricing, booking, themes, or food options. How can I assist you today?"

    # Try category-only detection first
    category = detect_category_only_request(user_message)
    if category:
        questions = get_faq_questions(category)
        if questions:
            question_list = '\n• ' + '\n• '.join(questions.keys())
            return f"Here are some frequently asked questions about {category.title()}:{question_list}\n\nFeel free to ask me any of these questions or ask something specific about {category}!"

    # Check for referenced categories and try normalization
    referenced_categories = get_referenced_categories(user_message)
    best_match = None
    best_score = 0

    for category in referenced_categories:
        questions = get_faq_questions(category)
        normalized = normalize_question_by_category(user_message, category)
        if normalized and normalized in questions:
            return questions[normalized]
        
        match, score = find_best_faq_match(user_message, questions)
        if match and score > best_score:
            best_match = match
            best_score = score

    if best_match and best_score >= 0.4:
        for category in referenced_categories:
            questions = get_faq_questions(category)
            if best_match in questions:
                return questions[best_match]

    # Fallback: search all categories
    all_questions = {}
    for category in get_faq_categories():
        all_questions.update(get_faq_questions(category))
    
    match, score = find_best_faq_match(user_message, all_questions)
    if match and score >= 0.5:
        return all_questions[match]

    # Get suggestions for partial matches
    suggestions = get_faq_suggestions(user_message)
    if suggestions:
        suggestion_list = '\n• ' + '\n• '.join(suggestions[:3])
        return f"I'm not sure about that specific question, but here are some related topics I can help with:{suggestion_list}\n\nOr feel free to ask me about our packages, pricing, booking process, food options, themes, or any other aspect of our catering services!"

    # Default response
    return "Thank you for your question! I'd be happy to help you with information about Nike's Catering Services. Could you please be more specific about what you'd like to know? I can help with:\n\n• Packages and pricing\n• Booking process\n• Food and menu options\n• Themes and decorations\n• Payment information\n• Our services\n\nWhat would you like to know more about?"

def api_chatbot_new_session(request):
    """API endpoint to start a new chatbot session"""
    request.session.pop('chat_history', None)
    request.session.pop('initialized', None)
    request.session.modified = True
    
    return JsonResponse({
        'success': True,
        'chat_history': [
            {'sender': 'bot', 'text': "Welcome to Nike's Catering Services! I'm your virtual assistant. How can I help you today? Feel free to ask me anything about our services, packages, pricing, booking, themes, food options, or any other questions you might have about our catering services."}
        ]
    })

def api_chatbot_load_session(request, session_id):
    """API endpoint to load a chatbot session"""
    try:
        session = get_object_or_404(ChatSession, id=session_id)
        request.session['chat_history'] = session.chat_history
        request.session['initialized'] = True
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'chat_history': session.chat_history,
            'title': session.title
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)