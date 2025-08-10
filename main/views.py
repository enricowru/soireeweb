from views.auth import *
from views.design import *
from views.moderator import *
from views.reviews import *
from views.user import *
from views.chat import *


# def home(request):
#     if not request.session.get('logged_in', False):
#         return redirect('login')
#     # Prepare user list for the template
#     user_list = []
#     for username, user in USERS.items():
#         role = 'Admin' if user.get('is_admin') else 'Moderator' if user.get('is_moderator') else 'User'
#         user_list.append({
#             'username': username,
#             'firstname': user.get('firstname', ''),
#             'lastname': user.get('lastname', ''),
#             'role': role
#         })
#     return render(request, 'main.html', {'logged_in': True, 'user_list': user_list})

# def login_view(request):
#     message = ''
#     show_register = False
#     if request.method == 'POST':
#         if 'username' in request.POST and 'password' in request.POST:
#             # Login form submitted
#             username = request.POST.get('username')
#             password = request.POST.get('password')

#             # Attempt to authenticate the user
#             user = authenticate(request, username=username, password=password)

#             if user is not None:
#                 # Log in the user first
#                 login(request, user)
#                 request.session['username'] = username # Store username in session

#                 # Check user roles and redirect accordingly
#                 if user.is_superuser:
#                     request.session['is_moderator'] = False # Ensure admin is not marked as moderator
#                     return redirect('admin_dashboard')
#                 try:
#                     moderator_profile = Moderator.objects.get(user=user)
#                     request.session['is_moderator'] = True
#                     return redirect('moderator')
#                 except Moderator.DoesNotExist:
#                     request.session['is_moderator'] = False
#                     # Redirect regular users to a different page (e.g., homepage)
#                     return redirect('main') # Redirect to the homepage for regular users
#             else:
#                 message = 'Invalid username or password.'

#         elif 'firstname' in request.POST and 'lastname' in request.POST:
#             # Register form submitted
#             username = request.POST.get('username')
#             if username in USERS:
#                 message = 'Username already exists.'
#                 show_register = True
#             else:
#                 password1 = request.POST.get('password1')
#                 password2 = request.POST.get('password2')
#                 if password1 != password2:
#                     message = 'Passwords do not match.'
#                     show_register = True
#                 else:
#                     USERS[username] = {
#                         'password': password1,
#                         'firstname': request.POST.get('firstname'),
#                         'lastname': request.POST.get('lastname'),
#                         'email': request.POST.get('email'),
#                         'mobile': request.POST.get('mobile'),
#                         'is_moderator': False,
#                     }
#                     message = 'Registration successful! You can now log in.'
#     logged_in = request.session.get('logged_in', False)
#     return render(request, 'login.html', {'message': message, 'show_register': show_register, 'logged_in': logged_in})

# def moderator_access(request):
#     # Check if the user is logged in and is a moderator (set in login_view)
#     if not request.user.is_authenticated or not request.session.get('is_moderator', False):
#         messages.error(request, 'You must be logged in as a moderator to access this page.')
#         return redirect('login')

#     # Get the moderator profile for the logged-in user
#     try:
#         moderator = Moderator.objects.get(user=request.user)
#     except Moderator.DoesNotExist:
#         # This case should ideally not happen if is_moderator is True in session,
#         # but as a fallback, log them out and redirect to login.
#         messages.error(request, 'Your moderator profile was not found.')
#         return redirect('logout')

#     # Reset moderator_ok for testing (keep existing logic)
#     if 'moderator_ok' in request.session:
#         del request.session['moderator_ok']

#     code_ok = request.session.get('moderator_ok', False)
#     error = ''

#     if not code_ok:
#         if request.method == 'POST' and 'code' in request.POST:
#             code = request.POST.get('code')
#             # Check if the code matches any event's access code
#             try:
#                 event = Event.objects.get(access_code=code)
#                 # Check if this moderator has access to this event based on their username
#                 # We now use request.user.username which is correct
#                 try:
#                     ModeratorAccess.objects.get(event=event, moderator_username=request.user.username)
#                     request.session['moderator_ok'] = True
#                     request.session['current_event_id'] = event.id
#                     code_ok = True
#                 except ModeratorAccess.DoesNotExist:
#                     error = 'You do not have access to this event.'
#             except Event.DoesNotExist:
#                 error = 'Invalid code.'
#         if not code_ok:
#             return render(request, 'moderator_code.html', {'error': error})

#     # Get the current event data for the moderator dashboard
#     current_event_id = request.session.get('current_event_id')
#     if current_event_id:
#         event = Event.objects.get(id=current_event_id)
#         trackers = EventTracker.objects.filter(event=event).order_by('-timestamp')
#         return render(request, 'event_tracker.html', {
#             'event': event,
#             'trackers': trackers,
#             'moderator': moderator # Pass moderator object to template if needed
#         })

#     # If no current event is set, render the code entry page
#     return render(request, 'moderator_code.html', {'error': error})

# def is_admin(request):
#     username = request.session.get('username')
#     user = USERS.get(username)
#     return user and user.get('is_admin')

# def admin_required(view_func):
#     def wrapper(request, *args, **kwargs):
#         if not is_admin(request):
#             messages.error(request, 'You must be an admin to access this page.')
#             return redirect('login')
#         return view_func(request, *args, **kwargs)
#     return wrapper

# @admin_required
# def admin_dashboard(request):
#     events = Event.objects.all().order_by('-date')
#     return render(request, 'custom_admin/dashboard.html', {'events': events})

# @admin_required
# def event_detail(request, event_id):
#     event = get_object_or_404(Event, pk=event_id)

#     if request.method == 'POST':
#         action = request.POST.get('action')
#         if action == 'checkin':
#             # Customer identifier is removed from the form, use a placeholder or default
#             checkin_username = "Customer" # Or a more dynamic placeholder if available

#             # Use the event's checkin_code
#             checkin_code_used = event.checkin_code if event.checkin_code else 'N/A'
            
#             EventTracker.objects.create(
#                 event=event,
#                 username=checkin_username, # Use placeholder for username
#                 interaction_type='checkin',
#                 content=f'Check-in with code: {checkin_code_used}' # Store the used check-in code
#             )
#             messages.success(request, f'Check-in recorded for {checkin_username}. Used Code: {checkin_code_used}')
#         # You can add other POST actions here in the future if needed

#         # Redirect back to the same page after handling POST
#         return redirect(reverse('event_detail', args=[event.id]))

#     # For GET requests, fetch data for display
#     trackers = EventTracker.objects.filter(event=event).order_by('-timestamp')
#     moderators = ModeratorAccess.objects.filter(event=event)

#     return render(request, 'custom_admin/event_detail.html', {
#         'event': event,
#         'trackers': trackers,
#         'moderators': moderators,
#     })

# @admin_required
# def create_event(request):
#     if request.method == 'POST':
#         form = EventForm(request.POST)
#         if form.is_valid():
#             event = form.save(commit=False)
#             # Generate access code before saving (for moderators)
#             event.access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
#             # Generate check-in code for customers
#             event.checkin_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
#             # Process guest list
#             guest_list = request.POST.get('guest_list', '[]')
#             try:
#                 guests = json.loads(guest_list)
#                 # Add checked_in status to each guest
#                 for guest in guests:
#                     guest['checked_in'] = False
#                 event.participants = guests
#             except json.JSONDecodeError:
#                 event.participants = []
            
#             event.save()
#             messages.success(request, f'Event created successfully! Access code (Moderators): {event.access_code}. Check-in Code (Customers): {event.checkin_code}')
#             return redirect('admin_dashboard')
#         else:
#             # If the form is not valid, errors will be in form.errors
#             messages.error(request, 'Error creating event. Please check the date.')
#     else:
#         form = EventForm() # An unbound form for GET requests
    
#     return render(request, 'custom_admin/create_event.html', {'form': form})

# @admin_required
# def grant_moderator_access(request, event_id):
#     if request.method == 'POST':
#         event = Event.objects.get(id=event_id)
#         firstname = request.POST.get('moderator_firstname')
        
#         # Find a User with the given first name and a linked Moderator profile
#         User = get_user_model()
#         user_with_moderator_profile = User.objects.filter(first_name=firstname, moderator_profile__isnull=False).first()

#         if user_with_moderator_profile:
#             # Check if access already exists for this event and moderator
#             if ModeratorAccess.objects.filter(event=event, moderator_username=user_with_moderator_profile.username).exists():
#                 messages.warning(request, f'Access already granted to {firstname} for this event.')
#             else:
#                 ModeratorAccess.objects.create(event=event, moderator_username=user_with_moderator_profile.username)
#                 messages.success(request, f'Access granted to {firstname}')
#         else:
#             messages.error(request, f'No moderator found with first name: {firstname}')
#     return redirect('event_detail', event_id=event_id)

# @admin_required
# def delete_event(request, event_id):
#     event = get_object_or_404(Event, pk=event_id)
#     if request.method == 'POST':
#         # Store event in history before deleting
#         EventHistory.objects.create(
#             title=event.title,
#             description=event.description,
#             date=event.date,
#             access_code=event.access_code,
#             checkin_code=event.checkin_code,
#             created_at=event.created_at,
#             deleted_by=request.user
#         )
#         event.delete()
#         messages.success(request, 'Event deleted successfully!')
#         return redirect('admin_dashboard')
#     return render(request, 'main/event_confirm_delete.html', {'event': event})

# @admin_required
# def event_history(request):
#     history = EventHistory.objects.all().order_by('-deleted_at')
#     return render(request, 'custom_admin/event_history.html', {'history': history})

# @admin_required
# def create_moderator(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         firstname = request.POST.get('firstname')
#         lastname = request.POST.get('lastname')
#         email = request.POST.get('email')
#         mobile = request.POST.get('mobile')

#         # Check if a User with this username already exists
#         User = get_user_model()
#         if User.objects.filter(username=username).exists():
#             messages.error(request, 'User with this username already exists.')
#         else:
#             # Create the User first
#             user = User.objects.create_user(username=username, password=password, email=email)
#             user.first_name = firstname
#             user.last_name = lastname
#             user.mobile = mobile
#             user.save()

#             # Then create the Moderator profile linked to the User
#             Moderator.objects.create(user=user)
            
#             messages.success(request, f'Moderator account created for {username}')
#             return redirect('admin_dashboard')
    
#     return render(request, 'custom_admin/create_moderator.html')

# @admin_required
# def view_all_moderators(request):
#     moderators = Moderator.objects.all()
#     return render(request, 'custom_admin/all_moderators.html', {'moderators': moderators})

# @admin_required
# def view_all_users(request):
#     # Get all users who are NOT moderators or admins
#     users = []
#     for username, user_data in USERS.items():
#         if not user_data.get('is_moderator') and not user_data.get('is_admin'):
#             users.append({
#                 'username': username,
#                 'firstname': user_data.get('firstname', ''),
#                 'lastname': user_data.get('lastname', ''),
#                 'email': user_data.get('email', ''),
#                 'mobile': user_data.get('mobile', ''),
#             })
#     return render(request, 'custom_admin/all_users.html', {'users': users})

# @admin_required
# def delete_moderator(request, moderator_id):
#     if request.method == 'POST':
#         try:
#             moderator = Moderator.objects.get(id=moderator_id)
#             moderator.delete()
#             messages.success(request, f'Moderator {moderator.username} deleted successfully!')
#         except Moderator.DoesNotExist:
#             messages.error(request, 'Moderator not found.')
#     return redirect('view_all_moderators')

# @admin_required
# def delete_moderator_access(request, access_id, event_id):
#     access = get_object_or_404(ModeratorAccess, id=access_id, event_id=event_id)
#     access.delete()
#     messages.success(request, 'Moderator access removed successfully.')
#     return redirect('event_detail', event_id=event_id)

# @admin_required
# def moderator_edit(request, moderator_id):
#     moderator = get_object_or_404(Moderator, id=moderator_id)
#     user = moderator.user

#     if request.method == 'POST':
#         form = ModeratorEditForm(request.POST, user_instance=user)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Moderator profile updated successfully.')
#             return redirect('view_all_moderators')
#     else:
#         form = ModeratorEditForm(user_instance=user)

#     return render(request, 'custom_admin/moderator_edit.html', {
#         'form': form,
#         'moderator': moderator
#     })

# @admin_required
# def admin_edit(request):
#     # Get the current admin user
#     user = request.user
#     if not user.is_superuser:
#         messages.error(request, 'You must be a superuser to access this page.')
#         return redirect('admin_dashboard')

#     if request.method == 'POST':
#         form = AdminEditForm(request.POST, user_instance=user)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Admin profile updated successfully.')
#             return redirect('admin_dashboard')
#     else:
#         form = AdminEditForm(user_instance=user)

#     return render(request, 'custom_admin/admin_edit.html', {
#         'form': form,
#         'user': user
#     })

# def logout_view(request):
#     # Clear all session data
#     request.session.flush()
#     messages.success(request, 'You have been successfully logged out.')
#     return redirect('login')

# def get_fuzzy_match(query, choices):
#     """
#     Returns the best match and its score from choices for the given query.
#     """
#     match = difflib.get_close_matches(query, choices, n=1, cutoff=0.0)
#     if match:
#         best = match[0]
#         score = difflib.SequenceMatcher(None, query, best).ratio()
#         return best, score
#     return None, 0

# def event_edit(request, event_id):
#     event = get_object_or_404(Event, pk=event_id)
#     if request.method == 'POST':
#         form = EventForm(request.POST, instance=event)
#         if form.is_valid():
#             form.save()
#             # Redirect to a success page or the event detail page (if you have one)
#             return redirect(reverse('event_edit', args=[event.pk])) # Redirect back to the edit page for now
#     else:
#         form = EventForm(instance=event)
#     return render(request, 'main/event_edit.html', {'form': form, 'event': event})

# @admin_required
# def event_delete(request, event_id):
#     event = get_object_or_404(Event, pk=event_id)
#     if request.method == 'POST':
#         # Store event in history before deleting
#         EventHistory.objects.create(
#             title=event.title,
#             description=event.description,
#             date=event.date,
#             access_code=event.access_code,
#             checkin_code=event.checkin_code,
#             created_at=event.created_at,
#             deleted_by=request.user
#         )
#         event.delete()
#         messages.success(request, 'Event deleted successfully!')
#         return redirect('admin_dashboard')
#     return render(request, 'main/event_confirm_delete.html', {'event': event})

# @login_required
# def chat_list(request):
#     chats = Chat.objects.filter(participants=request.user).order_by('-updated_at')
#     available_users = User.objects.exclude(id=request.user.id)
#     return render(request, 'main/chat.html', {
#         'chats': chats,
#         'available_users': available_users
#     })

# @login_required
# def chat_detail(request, chat_id):
#     chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
#     chats = Chat.objects.filter(participants=request.user).order_by('-updated_at')
#     available_users = User.objects.exclude(id=request.user.id)
    
#     # Mark messages as read
#     chat.messages.filter(~Q(sender=request.user), is_read=False).update(is_read=True)
    
#     return render(request, 'main/chat.html', {
#         'chats': chats,
#         'active_chat': chat,
#         'available_users': available_users
#     })

# @login_required
# def create_chat(request):
#     if request.method == 'POST':
#         chat_type = request.POST.get('chat_type')
        
#         if chat_type == 'direct':
#             user_id = request.POST.get('user_id')
#             other_user = get_object_or_404(User, id=user_id)
            
#             # Check if chat already exists
#             existing_chat = Chat.objects.filter(
#                 participants=request.user
#             ).filter(
#                 participants=other_user
#             ).filter(
#                 is_group_chat=False
#             ).first()
            
#             if existing_chat:
#                 return redirect('chat_detail', chat_id=existing_chat.id)
            
#             chat = Chat.objects.create(is_group_chat=False)
#             chat.participants.add(request.user, other_user)
            
#         else:  # group chat
#             name = request.POST.get('group_name')
#             participant_ids = request.POST.getlist('participants')
            
#             chat = Chat.objects.create(
#                 is_group_chat=True,
#                 name=name
#             )
#             chat.participants.add(request.user)
#             chat.participants.add(*participant_ids)
        
#         return redirect('chat_detail', chat_id=chat.id)
    
#     return redirect('chat_list')

# @login_required
# def send_message(request):
#     if request.method == 'POST':
#         chat_id = request.POST.get('chat_id')
#         content = request.POST.get('message')
        
#         chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
        
#         message = Message.objects.create(
#             chat=chat,
#             sender=request.user,
#             content=content
#         )
        
#         # Update chat's updated_at timestamp
#         chat.save()  # This will update the updated_at field
        
#         return JsonResponse({
#             'success': True,
#             'message': {
#                 'content': message.content,
#                 'timestamp': message.timestamp.strftime('%H:%M')
#             }
#         })
    
#     return JsonResponse({'success': False}, status=400)

# @admin_required
# def review_list(request):
#     reviews = Review.objects.all()
#     return render(request, 'custom_admin/review_list.html', {'reviews': reviews})

# @admin_required
# def review_approve(request, review_id):
#     review = get_object_or_404(Review, id=review_id)
#     review.is_approved = True
#     review.save()
#     messages.success(request, 'Review approved successfully.')
#     return redirect('review_list')

# @admin_required
# def review_delete(request, review_id):
#     review = get_object_or_404(Review, id=review_id)
#     if request.method == 'POST':
#         review.delete()
#         messages.success(request, 'Review deleted successfully.')
#         return redirect('review_list')
#     return render(request, 'custom_admin/review_confirm_delete.html', {'review': review})
    

# @csrf_exempt
# def redirect_home(request):
#     return render(request, 'main.html')


# # @csrf_exempt
# # def home(request):
# #     return render(request, 'main.html')


# # @csrf_exempt
# # def login_view(request):
# #     return render(request, 'login.html')


# def editprofile(request):
#     return render(request, 'editprofile.html')
    

# def moredesign(request):
#     sets = {
#         'themed_backdrop': [
#             {
#                 'title': 'Sanrio: Hello Kitty and Friends',
#                 'images': [
#                     'images/upgraded balloon set-up/R1C.jpg',
#                     'images/upgraded balloon set-up/R1A.jpg',
#                     'images/upgraded balloon set-up/R1D.jpg',
#                     'images/upgraded balloon set-up/R1B.jpg',
#                 ]
#             },
#             {
#                 'title': 'Teddy Bear',
#                 'images': [
#                     'images/upgraded balloon set-up/R2C.jpg',
#                     'images/upgraded balloon set-up/R2A.jpg',
#                     'images/upgraded balloon set-up/R2D.jpg',
#                     'images/upgraded balloon set-up/R2B.jpg',
#                 ]
#             },
#             {
#                 'title': 'Kuromi and My Melody (2)',
#                 'images': [
#                     'images/upgraded balloon set-up/R3C.jpg',
#                     'images/upgraded balloon set-up/R3A.jpg',
#                     'images/upgraded balloon set-up/R3D.jpg',
#                     'images/upgraded balloon set-up/R3B.jpg',
#                 ]
#             },
#             {
#                 'title': 'Baby Blue Bear',
#                 'images': [
#                     'images/upgraded balloon set-up/R4C.jpg',
#                     'images/upgraded balloon set-up/R4A.jpg',
#                     'images/upgraded balloon set-up/R4D.jpg',
#                     'images/upgraded balloon set-up/R4B.jpg',
#                 ]
#             },
#             {
#                 'title': 'Disney Princesses',
#                 'images': [
#                     'images/upgraded balloon set-up/R5C.jpg',
#                     'images/upgraded balloon set-up/R5A.jpg',
#                     'images/upgraded balloon set-up/R5D.jpg',
#                     'images/upgraded balloon set-up/R5B.jpg',
#                 ]
#             },
#             {
#                 'title': 'Safari Jungle',
#                 'images': [
#                     'images/upgraded balloon set-up/R6C.jpg',
#                     'images/upgraded balloon set-up/R6A.jpg',
#                     'images/upgraded balloon set-up/R6D.jpg',
#                     'images/upgraded balloon set-up/R6B.jpg',
#                 ]
#             },
#             {
#                 'title': 'Iron Man and Frozen',
#                 'images': [
#                     'images/upgraded balloon set-up/R7C.jpg',
#                     'images/upgraded balloon set-up/R7A.jpg',
#                     'images/upgraded balloon set-up/R7D.jpg',
#                     'images/upgraded balloon set-up/R7B.jpg',
#                 ]
#             },
#             {
#                 'title': 'Cinderella',
#                 'images': [
#                     'images/upgraded balloon set-up/R8C.jpg',
#                     'images/upgraded balloon set-up/R8A.jpg',
#                     'images/upgraded balloon set-up/R8D.jpg',
#                     'images/upgraded balloon set-up/R8B.jpg',
#                 ]
#             },
#             {
#                 'title': 'Blue Royalty',
#                 'images': [
#                     'images/upgraded balloon set-up/R9C.jpg',
#                     'images/upgraded balloon set-up/R9A.jpg',
#                     'images/upgraded balloon set-up/R9D.jpg',
#                     'images/upgraded balloon set-up/R9B.jpg',
#                 ]
#             },
#             {
#                 'title': 'Pink Floral',
#                 'images': [
#                     'images/upgraded balloon set-up/R10C.jpg',
#                     'images/upgraded balloon set-up/R10A.jpg',
#                     'images/upgraded balloon set-up/R10D.jpg',
#                     'images/upgraded balloon set-up/R10B.jpg',
#                 ]
#             },
#             {
#                 'title': 'Mermaid and Sea Life',
#                 'images': [
#                     'images/upgraded balloon set-up/R11C.jpg',
#                     'images/upgraded balloon set-up/R11A.jpg',
#                     'images/upgraded balloon set-up/R11D.jpg',
#                     'images/upgraded balloon set-up/R11B.jpg',
#                 ]
#             },
#             {
#                 'title': 'Barbie',
#                 'images': [
#                     'images/upgraded balloon set-up/R12C.jpg',
#                     'images/upgraded balloon set-up/R12A.jpg',
#                     'images/upgraded balloon set-up/R12D.jpg',
#                     'images/upgraded balloon set-up/R12B.jpg',
#                 ]
#             },
#             {
#                 'title': 'Butterfly Garden',
#                 'images': [
#                     'images/upgraded balloon set-up/R13C.jpg',
#                     'images/upgraded balloon set-up/R13A.jpg',
#                     'images/upgraded balloon set-up/R13D.jpg',
#                     'images/upgraded balloon set-up/R13B.jpg',
#                 ]
#             },
#         ],
#         'minimalist_setup': [
#             {
#                 'title': 'Red & White Roses',
#                 'images': [
#                     'images/minimalist set-up/R1C.jpg',
#                     'images/minimalist set-up/R1A.jpg',
#                     'images/minimalist set-up/R1D.jpg',
#                     'images/minimalist set-up/R1B.jpg',
#                 ]
#             },
#             {
#                 'title': 'Ivory Simplicity',
#                 'images': [
#                     'images/minimalist set-up/R2C.jpg',
#                     'images/minimalist set-up/R2A.jpg',
#                     'images/minimalist set-up/R2D.jpg',
#                     'images/minimalist set-up/R2B.jpg',
#                 ]
#             },
#             {
#  'title': 'Mint Serenity',
#                 'images': [
#                     'images/minimalist set-up/R3C.jpg',
#                     'images/minimalist set-up/R3A.jpg',
#                     'images/minimalist set-up/R3D.jpg',
#                     'images/minimalist set-up/R3B.jpg',
#                 ]
#             },
#             {
#                 'title': 'Amethyst Grace',
#                 'images': [
#                     'images/minimalist set-up/R4C.jpg',
#                     'images/minimalist set-up/R4A.jpg',
#                     'images/minimalist set-up/R4D.jpg',
#                     'images/minimalist set-up/R4B.jpg',
#                 ]
#             },
#             {
#                 'title': 'Sage Whispers',
#                 'images': [
#                     'images/minimalist set-up/R5C.jpg',
#                     'images/minimalist set-up/R5A.jpg',
#                     'images/minimalist set-up/R5D.jpg',
#                     'images/minimalist set-up/R5B.jpg',
#                 ]
#             },
#             {
#                 'title': 'Golden Crimson',
#                 'images': [
#                     'images/minimalist set-up/R6C.jpg',
#                     'images/minimalist set-up/R6A.jpg',
#                     'images/minimalist set-up/R6D.jpg',
#                     'images/minimalist set-up/R6B.jpg',
#                 ]
#             },
#             {
#                 'title': 'Maroon Muse',
#                 'images': [
#                     'images/minimalist set-up/R7C.jpg',
#                     'images/minimalist set-up/R7A.jpg',
#                     'images/minimalist set-up/R7D.jpg',
#                     'images/minimalist set-up/R7B.jpg',
#                 ]
#             },
#             {
#                 'title': 'Ever After Eden',
#                 'images': [
#                     'images/minimalist set-up/R8C.jpg',
#                     'images/minimalist set-up/R8A.jpg',
#                     'images/minimalist set-up/R8D.jpg',
#                     'images/minimalist set-up/R8B.jpg',
#                 ]
#             },
#             {
#                 'title': 'Whispering Vows',
#                 'images': [
#                     'images/minimalist set-up/R9C.jpg',
#                     'images/minimalist set-up/R9A.jpg',
#                     'images/minimalist set-up/R9D.jpg',
#                     'images/minimalist set-up/R9B.jpg',
#                 ]
#             },
#         ],
#         'signature_setup': [
#             {
#                 'title': 'Sunlit Bliss',
#                 'images': [
#                     'images/signature set-up/R1C.jpg',
#                     'images/signature set-up/R1A.jpg',
#                     'images/signature set-up/R1E.jpg',
#                     'images/signature set-up/R1F.jpg',
#                     'images/signature set-up/R1B.jpg',
#                     'images/signature set-up/R1D.jpg',
#                 ]
#             },
#             {
#                 'title': 'Forest Glow',
#                 'images': [
#                     'images/signature set-up/R2C.jpg',
#                     'images/signature set-up/R2A.jpg',
#                     'images/signature set-up/R2E.jpg',
#                     'images/signature set-up/R2F.jpg',
#                     'images/signature set-up/R2B.jpg',
#                     'images/signature set-up/R2D.jpg',
#                 ]
#             },
#             {
#                 'title': 'Blue Royale',
#                 'images': [
#                     'images/signature set-up/R3C.jpg',
#                     'images/signature set-up/R3A.jpg',
#                     'images/signature set-up/R3E.jpg',
#                     'images/signature set-up/R3F.jpg',
#                     'images/signature set-up/R3B.jpg',
#                     'images/signature set-up/R3D.jpg',
#                 ]
#             },
#             {
#                 'title': 'Golden Dusk',
#                 'images': [
#                     'images/signature set-up/R4C.jpg',
#                     'images/signature set-up/R4A.jpg',
#                     'images/signature set-up/R4E.jpg',
#                     'images/signature set-up/R4F.jpg',
#                     'images/signature set-up/R4B.jpg',
#                     'images/signature set-up/R4D.jpg',
#                 ]
#             },
#         ],
#     }    
#     return render(request, 'moredesign.html', {'sets': sets})



# # ✅ API for Mobile App to Submit Review
# @csrf_exempt
# def submit_review(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         name = data.get('name')
#         message = data.get('message')

#         if name and message:
#             Review.objects.create(username=name, comment=message, is_approved=False)
#             return JsonResponse({'message': 'Review submitted successfully'}, status=201)
#         else:
#             return JsonResponse({'error': 'Name and message are required'}, status=400)
#     return JsonResponse({'error': 'Invalid request method'}, status=405)


# # ✅ Moderator View for Pending Reviews
# @user_passes_test(is_moderator)
# def review_moderation(request):
#     pending_reviews = Review.objects.filter(is_approved=False)
#     return render(request, 'moderation/review_list.html', {'reviews': pending_reviews})


# # ✅ Approve a Review by ID
# @user_passes_test(is_moderator)
# def approve_review(request, review_id):
#     review = get_object_or_404(Review, id=review_id)
#     review.is_approved = True
#     review.save()
#     return redirect('review_moderation')


# @csrf_exempt
# @require_http_methods(["POST"])
# def signup(request):
#     try:
#         data = json.loads(request.body)
#         firstname = data.get('firstname')
#         lastname = data.get('lastname')
#         username = data.get('username')
#         email = data.get('email')
#         password = data.get('password')
#         mobile = data.get('mobile')  # Optional - only stored if you extend the User model

#         if User.objects.filter(username=username).exists():
#             return JsonResponse({'message': 'Username already exists'}, status=400)

#         user = User.objects.create_user(
#             username=username,
#             email=email,
#             password=password,
#             first_name=firstname,
#             last_name=lastname
#         )

#         response = JsonResponse({'message': 'User registered successfully'}, status=201)
#     except Exception as e:
#         response = JsonResponse({'message': 'Server error', 'error': str(e)}, status=500)

#     response["Access-Control-Allow-Origin"] = "https://nikescateringservices.com"
#     response["Access-Control-Allow-Credentials"] = "true"
#     return response