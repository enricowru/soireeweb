from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from ..forms import EventForm, ModeratorEditForm, AdminEditForm
from ..models import Event, EventTracker, ModeratorAccess, Moderator, EventHistory
from .auth import admin_required
import random
import string
from django.contrib.auth import get_user_model
import json, asyncio
from django.http import StreamingHttpResponse
from main.sse import booking_events  

User = get_user_model()

@admin_required
def admin_dashboard(request):
    events = Event.objects.all().order_by('-date')
    return render(request, 'custom_admin/dashboard.html', {'events': events})

@admin_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'checkin':
            checkin_username = "Customer"
            checkin_code_used = event.checkin_code if event.checkin_code else 'N/A'
            
            EventTracker.objects.create(
                event=event,
                username=checkin_username,
                interaction_type='checkin',
                content=f'Check-in with code: {checkin_code_used}'
            )
            messages.success(request, f'Check-in recorded for {checkin_username}. Used Code: {checkin_code_used}')
        return redirect(reverse('event_detail', args=[event.id]))

    trackers = EventTracker.objects.filter(event=event).order_by('-timestamp')
    moderators = ModeratorAccess.objects.filter(event=event)

    return render(request, 'custom_admin/event_detail.html', {
        'event': event,
        'trackers': trackers,
        'moderators': moderators,
    })

@admin_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            event.checkin_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            guest_list = request.POST.get('guest_list', '[]')
            try:
                guests = json.loads(guest_list)
                for guest in guests:
                    guest['checked_in'] = False
                event.participants = guests
            except json.JSONDecodeError:
                event.participants = []
            
            event.save()
            messages.success(request, f'Event created successfully! Access code (Moderators): {event.access_code}. Check-in Code (Customers): {event.checkin_code}')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Error creating event. Please check the date.')
    else:
        form = EventForm()
    
    return render(request, 'custom_admin/create_event.html', {'form': form})

@admin_required
def grant_moderator_access(request, event_id):
    if request.method == 'POST':
        event = Event.objects.get(id=event_id)
        firstname = request.POST.get('moderator_firstname')
        
        user_with_moderator_profile = User.objects.filter(
            first_name=firstname, 
            moderator_profile__isnull=False
        ).first()

        if user_with_moderator_profile:
            if ModeratorAccess.objects.filter(event=event, moderator_username=user_with_moderator_profile.username).exists():
                messages.warning(request, f'Access already granted to {firstname} for this event.')
            else:
                ModeratorAccess.objects.create(event=event, moderator_username=user_with_moderator_profile.username)
                messages.success(request, f'Access granted to {firstname}')
        else:
            messages.error(request, f'No moderator found with first name: {firstname}')
    return redirect('event_detail', event_id=event_id)

@admin_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        EventHistory.objects.create(
            title=event.title,
            description=event.description,
            date=event.date,
            access_code=event.access_code,
            checkin_code=event.checkin_code,
            created_at=event.created_at,
            deleted_by=request.user
        )
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('admin_dashboard')
    return render(request, 'main/event_confirm_delete.html', {'event': event})

@admin_required
def event_history(request):
    history = EventHistory.objects.all().order_by('-deleted_at')
    return render(request, 'custom_admin/event_history.html', {'history': history})

@admin_required
def create_moderator(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'User with this username already exists.')
        else:
            user = User.objects.create_user(
                username=username, 
                password=password, 
                email=email
            )
            user.first_name = firstname
            user.last_name = lastname
            user.mobile = mobile
            user.save()

            Moderator.objects.create(user=user)
            messages.success(request, f'Moderator account created for {username}')
            return redirect('admin_dashboard')
    
    return render(request, 'custom_admin/create_moderator.html')

@admin_required
def view_all_moderators(request):
    moderators = Moderator.objects.all()
    return render(request, 'custom_admin/all_moderators.html', {'moderators': moderators})

@admin_required
def view_all_users(request):
    from .auth import USERS
    users = []
    for username, user_data in USERS.items():
        if not user_data.get('is_moderator') and not user_data.get('is_admin'):
            users.append({
                'username': username,
                'firstname': user_data.get('firstname', ''),
                'lastname': user_data.get('lastname', ''),
                'email': user_data.get('email', ''),
                'mobile': user_data.get('mobile', ''),
            })
    return render(request, 'custom_admin/all_users.html', {'users': users})

@admin_required
def delete_moderator(request, moderator_id):
    if request.method == 'POST':
        try:
            moderator = Moderator.objects.get(id=moderator_id)
            moderator.delete()
            messages.success(request, f'Moderator {moderator.username} deleted successfully!')
        except Moderator.DoesNotExist:
            messages.error(request, 'Moderator not found.')
    return redirect('view_all_moderators')

@admin_required
def delete_moderator_access(request, access_id, event_id):
    access = get_object_or_404(ModeratorAccess, id=access_id, event_id=event_id)
    access.delete()
    messages.success(request, 'Moderator access removed successfully.')
    return redirect('event_detail', event_id=event_id)

@admin_required
def moderator_edit(request, moderator_id):
    moderator = get_object_or_404(Moderator, id=moderator_id)
    user = moderator.user

    if request.method == 'POST':
        form = ModeratorEditForm(request.POST, user_instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Moderator profile updated successfully.')
            return redirect('view_all_moderators')
    else:
        form = ModeratorEditForm(user_instance=user)

    return render(request, 'custom_admin/moderator_edit.html', {
        'form': form,
        'moderator': moderator
    })

@admin_required
def admin_edit(request):
    user = request.user
    if not user.is_superuser:
        messages.error(request, 'You must be a superuser to access this page.')
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = AdminEditForm(request.POST, user_instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Admin profile updated successfully.')
            return redirect('admin_dashboard')
    else:
        form = AdminEditForm(user_instance=user)

    return render(request, 'custom_admin/admin_edit.html', {
        'form': form,
        'user': user
    })

@admin_required
def event_edit(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)

        if form.is_valid():
            updated_event = form.save(commit=False)

            guest_list_raw = request.POST.get('guest_list')

            # ✅ Only update guests if guest_list is valid JSON (not empty string or malformed)
            try:
                if guest_list_raw and guest_list_raw.strip() not in ['', '[]']:
                    guests = json.loads(guest_list_raw)
                    for guest in guests:
                        guest.setdefault('checked_in', False)
                    updated_event.participants = guests
                else:
                    # Leave guests untouched
                    updated_event.participants = event.participants
            except json.JSONDecodeError:
                # ✅ Don't block update — just skip updating participants
                messages.warning(request, "Guest list was ignored due to invalid format.")
                updated_event.participants = event.participants

            updated_event.save()
            messages.success(request, 'Event updated successfully.')
            return redirect(reverse('event_edit', args=[event.pk]))
        else:
            messages.error(request, 'Please correct the errors in the form.')

    else:
        form = EventForm(instance=event)

    return render(request, 'main/event_edit.html', {
        'form': form,
        'event': event
    })

@admin_required
def event_delete(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        EventHistory.objects.create(
            title=event.title,
            description=event.description,
            date=event.date,
            access_code=event.access_code,
            checkin_code=event.checkin_code,
            created_at=event.created_at,
            deleted_by=request.user
        )
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('admin_dashboard')
    return render(request, 'main/event_confirm_delete.html', {'event': event})  

async def booking_notifications(request):
    """
    URL:  /admin/bookings/stream/
    Keeps an open HTTP connection and pushes each booking event
    as a Server‑Sent‑Event line:  data: {json}\n\n
    """
    queue = booking_events.register()

    async def event_gen():
        try:
            while True:
                data = await queue.get()
                yield f"data: {json.dumps(data)}\n\n".encode()
        finally:
            booking_events.connections.discard(queue)

    resp = StreamingHttpResponse(
        event_gen(),
        content_type="text/event-stream",
    )
    resp["Cache-Control"]       = "no-cache"
    resp["X-Accel-Buffering"]   = "no"          # nginx
    return resp