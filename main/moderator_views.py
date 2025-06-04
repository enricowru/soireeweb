from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from .models import Event, EventTracker, ModeratorAccess, Moderator, User, Review
import random
import string
from datetime import datetime
import pytz


def login_view(request):
    message = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Hardcoded login for admin shortcut
        if username == "admin" and password == "1234":
            request.session['logged_in'] = True
            request.session['username'] = username
            request.session['is_moderator'] = True
            return redirect('review-list')  # or 'moderator-access'

        try:
            user = User.objects.get(username=username)
            if check_password(password, user.password):
                request.session['logged_in'] = True
                request.session['username'] = username
                if user.is_admin:
                    return redirect('admin-dashboard')
                elif user.is_moderator:
                    request.session['is_moderator'] = True
                    return redirect('moderator-access')
                else:
                    return redirect('home')
            else:
                message = 'Invalid username or password.'
        except User.DoesNotExist:
            message = 'Invalid username or password.'

    return render(request, 'login.html', {'message': message})


def moderator_access(request):
    username = request.session.get('username')
    is_moderator = request.session.get('is_moderator', False)
    if not (username and is_moderator):
        return redirect('login')

    try:
        moderator = Moderator.objects.get(username=username)
    except Moderator.DoesNotExist:
        return redirect('login')

    if 'moderator_ok' in request.session:
        del request.session['moderator_ok']

    code_ok = request.session.get('moderator_ok', False)
    error = ''

    if not code_ok:
        if request.method == 'POST' and 'code' in request.POST:
            code = request.POST.get('code')
            try:
                event = Event.objects.get(access_code=code)
                try:
                    ModeratorAccess.objects.get(event_id=event.id, moderator_username=username)
                    request.session['moderator_ok'] = True
                    request.session['current_event_id'] = event.id
                    code_ok = True
                except ModeratorAccess.DoesNotExist:
                    error = 'You do not have access to this event.'
            except Event.DoesNotExist:
                error = 'Invalid code.'

        if not code_ok:
            return render(request, 'moderator/moderator_code.html', {'error': error})

    current_event_id = request.session.get('current_event_id')
    if current_event_id:
        event = Event.objects.get(id=current_event_id)
        trackers = EventTracker.objects.filter(event=event).order_by('-timestamp')
        return render(request, 'moderator/event_tracker.html', {
            'event': event,
            'trackers': trackers
        })

    return redirect('moderator-access')


def admin_dashboard(request):
    if not request.session.get('logged_in', False):
        return redirect('login')

    events = Event.objects.all().order_by('-date')
    return render(request, 'moderator/dashboard.html', {'events': events})


def event_detail(request, event_id):
    if not request.session.get('logged_in', False):
        return redirect('login')

    event = Event.objects.get(id=event_id)
    trackers = EventTracker.objects.filter(event=event).order_by('-timestamp')
    moderators = ModeratorAccess.objects.filter(event=event)

    return render(request, 'moderator/event_detail.html', {
        'event': event,
        'trackers': trackers,
        'moderators': moderators
    })


def create_event(request):
    if not request.session.get('logged_in', False):
        return redirect('login')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        date_str = request.POST.get('date')
        access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        try:
            event_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            if settings.USE_TZ:
                event_date = pytz.timezone(settings.TIME_ZONE).localize(event_date)
                now = datetime.now(pytz.timezone(settings.TIME_ZONE))
            else:
                now = datetime.now()

            if event_date < now:
                messages.error(request, 'Event date and time cannot be in the past.')
                return render(request, 'moderator/create_event.html')
        except Exception as e:
            messages.error(request, f'Invalid date format: {e}')
            return render(request, 'moderator/create_event.html')

        Event.objects.create(
            title=title,
            description=description,
            date=event_date,
            access_code=access_code
        )

        messages.success(request, f'Event created! Access code: {access_code}')
        return redirect('admin-dashboard')

    return render(request, 'moderator/create_event.html')


def review_list(request):
    if not request.session.get('logged_in', False):
        return redirect('login')

    reviews = Review.objects.all().order_by('-date')
    return render(request, 'moderator/review_list.html', {
        'reviews': reviews
    })