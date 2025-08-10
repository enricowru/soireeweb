from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..models import Event, EventTracker, ModeratorAccess, Moderator, Review
from ..utils import is_moderator
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(is_moderator)
def moderator_access(request):
    if not request.user.is_authenticated or not request.session.get('is_moderator', False):
        messages.error(request, 'You must be logged in as a moderator to access this page.')
        return redirect('login')

    try:
        moderator = Moderator.objects.get(user=request.user)
    except Moderator.DoesNotExist:
        messages.error(request, 'Your moderator profile was not found.')
        return redirect('logout')

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
                    ModeratorAccess.objects.get(event=event, moderator_username=request.user.username)
                    request.session['moderator_ok'] = True
                    request.session['current_event_id'] = event.id
                    code_ok = True
                except ModeratorAccess.DoesNotExist:
                    error = 'You do not have access to this event.'
            except Event.DoesNotExist:
                error = 'Invalid code.'
        if not code_ok:
            return render(request, 'moderator_code.html', {'error': error})

    current_event_id = request.session.get('current_event_id')
    if current_event_id:
        event = Event.objects.get(id=current_event_id)
        trackers = EventTracker.objects.filter(event=event).order_by('-timestamp')
        return render(request, 'event_tracker.html', {
            'event': event,
            'trackers': trackers,
            'moderator': moderator
        })

    return render(request, 'moderator_code.html', {'error': error})

@user_passes_test(is_moderator)
def review_moderation(request):
    pending_reviews = Review.objects.filter(is_approved=False)
    return render(request, 'moderation/review_list.html', {'reviews': pending_reviews})

@user_passes_test(is_moderator)
def approve_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.is_approved = True
    review.save()
    return redirect('review_moderation')