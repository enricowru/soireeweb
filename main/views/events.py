from django.shortcuts import render, get_object_or_404
from .auth import login_required
from ..models import BookingRequest, EventStatusLog, EventStatusAttachment, Chat
import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.dateformat import format as date_format

@login_required
def event_status(request, id):
    booking = get_object_or_404(BookingRequest, id=id)

    # Get the Event related to this booking (if exists)
    event = getattr(booking, 'event_set', None)
    event_date = None
    event_type = booking.event_type  # fallback

    if event:
        event_obj = booking.event_set.first()  # assuming one-to-one relationship
        if event_obj:
            event_date = event_obj.date
            event_type = event_obj.event_type if hasattr(event_obj, 'event_type') else event_type

    steps_def = [
        ('CREATED', 'Booking received and is created'),
        ('PAYMENT', 'Payment status update'),
        ('BACKDROP', 'Backdrop has been set up'),
        ('CATERING', 'Catering/buffet in progress'),
        ('LOGISTICS', 'Lights/sound/logistics update'),
    ]

    status_logs = {log.label: log for log in EventStatusLog.objects.filter(booking=booking)}

    attachments = {}
    for a in EventStatusAttachment.objects.filter(booking=booking):
        attachments.setdefault(a.status_log.label, []).append(a.file.url)

    step_objs = []
    step_json = []

    for label, description in steps_def:
        log = status_logs.get(label)

        is_done = False
        if log:
            if label == 'PAYMENT':
                total_due = log.total_due
                total_paid = sum(p.amount_paid for p in log.payment_transactions.all())
                is_done = total_due is not None and total_paid >= total_due
            else:
                is_done = log.status == EventStatusLog.Status.DONE

        img_urls = attachments.get(label, [])

        if img_urls:
            html = f'<p>{description}</p>'
            for url in img_urls:
                html += f'<img src="{url}" class="proof-thumb" alt="Proof image">'
        elif is_done:
            html = f'<p>{description}</p><p><em>No image uploaded.</em></p>'
        else:
            html = f'<div class="placeholder">Not yet completed.</div>'

        step_objs.append({
            'label': label,
            'get_label_display': label.title().replace('_', ' '),
            'description': description,
            'is_done': is_done,
        })

        step_json.append({
            'label': label,
            'title': label.title().replace('_', ' '),
            'html': html,
            'uploadable': False,
            'is_done': is_done,
            'status': log.status if log else None,
            # Pass the event date only for CREATED step
            'event_date': event_date.strftime('%b %d, %Y %I:%M %p') if event_date and label == 'CREATED' else None,
            'event_type': event_type if label == 'CREATED' else None,
        })

    return render(request, 'event_status.html', {
        'booking': booking,
        'status_steps': step_objs,
        'step_content_json': json.dumps(step_json),
    })

def api_booking_list(request):
    """Return a list of the logged-in client's bookings."""
    bookings = BookingRequest.objects.filter(client=request.user).order_by('-id')
    data = []
    for b in bookings:
        event_date_str = None
        
        # Logic based on status:
        # - For draft/pending: use BookingRequest.event_date (format: 2025-09-04)
        # - For other statuses: use Event.date if exists (format: 2025-08-27 16:00:00+00), fallback to BookingRequest.event_date
        if b.status.lower() in ['draft', 'pending']:
            # Use event_date from BookingRequest for draft/pending
            if b.event_date:
                # Format: 2025-09-04 → Sep 04, 2025
                month_names = [
                    '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
                ]
                event_date_str = f"{month_names[b.event_date.month]} {b.event_date.day:02d}, {b.event_date.year}"
        else:
            # For other statuses, try to get date from related Event first
            event = b.event_set.first() if hasattr(b, 'event_set') else None
            if event and hasattr(event, 'date') and event.date:
                # Format: 2025-08-27 16:00:00+00 → Aug 27, 2025 4:00PM
                month_names = [
                    '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
                ]
                hour = event.date.hour
                ampm = 'AM' if hour < 12 else 'PM'
                display_hour = hour if hour <= 12 else hour - 12
                if display_hour == 0:
                    display_hour = 12
                event_date_str = f"{month_names[event.date.month]} {event.date.day}, {event.date.year} {display_hour}:{event.date.minute:02d}{ampm}"
            elif b.event_date:
                # Fallback to BookingRequest.event_date
                month_names = [
                    '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
                ]
                event_date_str = f"{month_names[b.event_date.month]} {b.event_date.day:02d}, {b.event_date.year}"
        
        data.append({
            "id": b.id,
            "event_type": b.event_type,
            "status": b.status,
            "event_date": event_date_str,
        })
    return JsonResponse(data, safe=False)

def api_booking_status(request, id):
    """Return the stepper data for a specific booking."""
    booking = get_object_or_404(BookingRequest, id=id, client=request.user)

    event = booking.event_set.first() if hasattr(booking, 'event_set') else None
    event_date = event.date if event else None
    event_type = event.event_type if event and hasattr(event, 'event_type') else booking.event_type

    steps_def = [
        ('CREATED', 'Booking received and is created'),
        ('PAYMENT', 'Payment status update'),
        ('BACKDROP', 'Backdrop has been set up'),
        ('CATERING', 'Catering/buffet in progress'),
        ('LOGISTICS', 'Lights/sound/logistics update'),
    ]

    status_logs = {log.label: log for log in EventStatusLog.objects.filter(booking=booking)}

    attachments = {}
    for a in EventStatusAttachment.objects.filter(booking=booking):
        attachments.setdefault(a.status_log.label, []).append(a.display_url)  # use display_url for prod/dev

    step_json = []
    for label, description in steps_def:
        log = status_logs.get(label)
        is_done = False
        if log:
            if label == 'PAYMENT':
                total_due = log.total_due
                total_paid = sum(p.amount_paid for p in log.payment_transactions.all())
                is_done = total_due is not None and total_paid >= total_due
            else:
                is_done = log.status == EventStatusLog.Status.DONE

        step_json.append({
            'label': label,
            'title': label.title().replace('_', ' '),
            'description': description,
            'images': attachments.get(label, []),  # list of URLs
            'is_done': is_done,
            'status': log.status if log else None,
            'event_date': event_date.strftime('%b %d, %Y %I:%M %p') if event_date and label == 'CREATED' else None,
            'event_type': event_type if label == 'CREATED' else None,
        })

    return JsonResponse({
        "id": booking.id,
        "event_type": booking.event_type,
        "status": booking.status, 
        "event_date": event_date.strftime('%b %d, %Y %I:%M %p') if event_date else None,
        "steps": step_json
    })

def my_bookings_json(request):
    user = request.user

    # Active bookings
    active_bookings = list(
        BookingRequest.objects
            .filter(client=user, status__in=["draft", "confirmed"])
            .order_by("-created_at")
            .values(
                "id",
                "status",
                "event_type",
                "event_date",
                "created_at"
            )
    )

    # Past bookings
    past_bookings = list(
        BookingRequest.objects
            .filter(client=user, status="rejected")
            .order_by("-created_at")
            .values(
                "id",
                "status",
                "event_type",
                "event_date",
                "created_at"
            )
    )

    # Chats
    chats = (
        Chat.objects
            .filter(participants=user)
            .prefetch_related("participants", "messages__sender", "request_booking")
            .order_by("-updated_at")
    )

    first_chat = chats.first()
    first_booking = BookingRequest.objects.filter(chat=first_chat).first() if first_chat else None

    booking_date = first_booking.event_date if first_booking else None
    event_type   = first_booking.event_type if first_booking else ""

    first_messages = []
    if first_chat:
        first_messages = [
            {
                "id": m.id,
                "sender": m.sender.username,
                "mine": m.sender_id == user.id,
                "html": m.content,
                "ts": m.timestamp.isoformat(),
            }
            for m in first_chat.messages.select_related("sender")[:25]
        ]

    booking_meta = (
        f"{event_type} • {date_format(booking_date, 'M d, Y')}"
        if first_booking and booking_date else ""
    )

    data = {
        "active_bookings": active_bookings,
        "past_bookings": past_bookings,
        "first_chat": {
            "id": first_chat.id if first_chat else None,
            "participants": [p.username for p in first_chat.participants.all()] if first_chat else [],
            "messages": first_messages
        } if first_chat else None,
        "first_booking": {
            "id": first_booking.id,
            "event_type": event_type,
            "event_date": booking_date.isoformat() if booking_date else None
        } if first_booking else None,
        "booking_meta": booking_meta
    }

    return JsonResponse(data)