from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from ..forms import EventForm, AdminEditForm
from ..models import Event, EventHistory, Chat, BookingRequest, EventStatusLog, EventStatusAttachment, BookingRequest, PaymentTransaction, AdminNotification, UserNotification
from .auth import admin_required
from django.contrib.auth import get_user_model
import json
from django.http import StreamingHttpResponse, JsonResponse
from main.sse import booking_events  
from asgiref.sync import async_to_sync
from django.utils.timezone import localtime, now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
import os
import uuid
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.timezone import now
from django.conf import settings
import cloudinary.uploader
import time

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
            
            # EventTracker.objects.create(
            #     event=event,
            #     username=checkin_username,
            #     interaction_type='checkin',
            #     content=f'Check-in with code: {checkin_code_used}'
            # )
            # messages.success(request, f'Check-in recorded for {checkin_username}. Used Code: {checkin_code_used}')
        return redirect(reverse('event_detail', args=[event.id]))

    # trackers = EventTracker.objects.filter(event=event).order_by('-timestamp')

    return render(request, 'custom_admin/event_detail.html', {
        'event': event,
        # 'trackers': trackers,
    })

@admin_required
def create_event(request):
    if request.method == 'POST':
        chat_id = request.POST.get('chat')  # not 'booking'
        if not chat_id:
            messages.error(request, "Chat ID is missing.")
            form = EventForm()
            return render(request, 'custom_admin/create_event.html', {'form': form}, status=400)

        booking = get_object_or_404(BookingRequest, chat_id=chat_id)
        form = EventForm(request.POST)

        if form.is_valid():
            event = form.save(commit=False)
            event.booking = booking
            
            print("Saving event:", event.title, event.description, event.date, "Booking ID:", booking.id)
            
            try:
                event.save()
                
                # Update booking status here (adjust field name accordingly)
                booking.status = 'CREATED'  # or whatever your status field and value are
                booking.save(update_fields=['status'])

                # Create or update the EventStatusLog for 'CREATED' label as DONE
                log, created = EventStatusLog.objects.get_or_create(
                    booking=booking,
                    label='CREATED',
                    defaults={'status': EventStatusLog.Status.DONE}
                )
                if not created:
                    log.status = EventStatusLog.Status.DONE
                    log.save(update_fields=['status'])
                
                # Create user notification for Step 1: Booking Request Approved and Created
                create_booking_status_notification(booking, log, request.user)

                print(f"Event saved with ID: {event.id}")
                messages.success(request, "Event created successfully!")
                return redirect('admin_dashboard')

            except Exception as e:
                print("Error saving event:", e)
                messages.error(request, f"Error saving event: {e}")
                return render(request, 'custom_admin/create_event.html', {'form': form}, status=400)
        else:
            print("Form errors:", form.errors)
            messages.error(request, "Error creating event. Please check the form.")
            return render(request, 'custom_admin/create_event.html', {'form': form}, status=400)
    else:
        form = EventForm()
        return render(request, 'custom_admin/create_event.html', {'form': form})

@admin_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        EventHistory.objects.create(
            title=event.title,
            description=event.description,
            date=event.date,
            access_code=getattr(event, 'access_code', None),
            checkin_code=getattr(event, 'checkin_code', None),
            created_at=event.created_at,
            deleted_by=request.user
        )
        event.delete()
        messages.success(request, 'Event removed successfully!')
        return redirect('admin_dashboard')
    return render(request, 'main/event_confirm_delete.html', {'event': event})

@admin_required
def event_history(request):
    history = EventHistory.objects.all().order_by('-deleted_at')
    return render(request, 'custom_admin/event_history.html', {'history': history})

# @admin_required
# def create_moderator(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         firstname = request.POST.get('firstname')
#         lastname = request.POST.get('lastname')
#         email = request.POST.get('email')
#         mobile = request.POST.get('mobile')

#         if User.objects.filter(username=username).exists():
#             messages.error(request, 'User with this username already exists.')
#         else:
#             user = User.objects.create_user(
#                 username=username, 
#                 password=password, 
#                 email=email
#             )
#             user.first_name = firstname
#             user.last_name = lastname
#             user.mobile = mobile
#             user.save()

#             Moderator.objects.create(user=user)
#             messages.success(request, f'Moderator account created for {username}')
#             return redirect('admin_dashboard')
    
#     return render(request, 'custom_admin/create_moderator.html')

# @admin_required
# def view_all_moderators(request):
#     moderators = Moderator.objects.all()
#     return render(request, 'custom_admin/all_moderators.html', {'moderators': moderators})


@admin_required
def view_all_users(request):
    """
    Show all users except:
      • hard‑coded admin usernames
      • anyone who has a Moderator row
    """

    # 1) build a subquery that tells us whether a Moderator row exists
    # mod_exists = Moderator.objects.filter(user=OuterRef("pk"))

    # 2) base queryset
    qs = (
        User.objects
        # .annotate(is_moderator=Exists(mod_exists))
        .exclude(Q(username__iexact="admin"))
        .order_by("username")
    )

    # 3) build simple list for template
    users = [
        {
            "username":  u.username,
            "firstname": u.first_name,
            "lastname":  u.last_name,
            "email":     u.email,
            "mobile":    u.mobile or "",  # mobile is directly on User model
        }
        for u in qs
    ]

    return render(request, "custom_admin/all_users.html", {"users": users})

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

@admin_required
def admin_edit(request):
    user = request.user
    if not user.is_superuser:
        messages.error(request, 'You must be a superuser to access this page.')
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = AdminEditForm(request.POST, user_instance=user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Admin profile updated successfully.')
                return redirect('admin_edit')  # Redirect to same page to refresh
            except Exception as e:
                messages.error(request, f'Error updating profile: {str(e)}')
        else:
            # Add form errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.title()}: {error}')
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
            updated_event = form.save()
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


def booking_notifications(request):
    """
    URL:  /admin/bookings/stream/
    Keeps an open HTTP connection and pushes each booking event
    as a Server‑Sent‑Event line:  data: {json}\n\n
    """
    queue = booking_events.register()

    def event_gen():
        try:
            while True:
                data = async_to_sync(queue.get)() 
                yield f"data: {json.dumps(data)}\n\n".encode()
        finally:
            booking_events.connections.discard(queue)

    resp = StreamingHttpResponse(
        event_gen(),
        content_type="text/event-stream",
    )
    resp["Cache-Control"]       = "no-cache"
    return resp


@admin_required      
def admin_booking_list(request):
    """
    GET /admin/load-chats?limit=50
    Returns newest‑updated chats as JSON.
    """
    limit = int(request.GET.get("limit", 100))

    chats = (
        Chat.objects
        .prefetch_related("request_booking", "participants")
        .order_by("-updated_at")[:limit]
    )

    out = []
    for chat in chats:
        # request_booking is a manager → take first() (or loop if >1)
        booking = chat.request_booking.first()
        if not booking:
            continue

        client = booking.client
        out.append({
            "chat_id":     chat.id,
            "booking_id":  booking.id,
            "event_type":  booking.event_type,
            "event_date":  booking.event_date.isoformat(),
            "client_name": client.get_full_name() or client.username,
            "last_updated": localtime(chat.updated_at).isoformat(timespec="seconds"),
        })

    return JsonResponse(out, safe=False)

@admin_required
def booking_requests(request):
    bookings = BookingRequest.objects.select_related("chat").all().order_by("-created_at")
    selected_booking_id = request.GET.get('booking')  # Get booking ID from URL parameter
    return render(request, "custom_admin/booking_request_chat.html", {
        "bookings": bookings,
        "selected_booking_id": selected_booking_id
    })
  
@admin_required
def booking_requests_status(request, id):
    booking = get_object_or_404(BookingRequest, chat_id=id)
    client = get_object_or_404(User, id=booking.client_id)
    event = Event.objects.filter(booking=booking).first()

    steps_def = [
        ('CREATED', 'Booking received and is created'),
        ('PAYMENT', 'Payment status update'),
        ('BACKDROP', 'Backdrop has been set up'),
        ('CATERING', 'Catering/buffet in progress'),
        ('LOGISTICS', 'Lights/sound/logistics update'),
    ]

    status_logs = {
        log.label: log for log in EventStatusLog.objects.filter(booking=booking)
    }

    # Group attachments by status label
    attachments = {}
    for a in EventStatusAttachment.objects.filter(booking=booking):
        url = a.display_url  # <-- use display_url property
        if url:  # only append if URL exists
            attachments.setdefault(a.status_log.label, []).append(url)

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
                is_done = (log.status == EventStatusLog.Status.DONE)

        img_urls = attachments.get(label, [])
        if img_urls:
            html = f'<p>{description}</p>'
            for url in img_urls:
                html += f'<img src="{url}" class="proof-thumb" alt="Proof image">'
        elif is_done:
            html = f'<p>{description}</p><p><em>No image uploaded.</em></p>'
        else:
            html = f'<div class="placeholder">Not yet completed.</div>'

        if label == 'PAYMENT' and log:
            total_paid_display = sum(p.amount_paid for p in log.payment_transactions.all())
            html += f'<p><strong>Total Due:</strong> {log.total_due or "N/A"}</p>'
            html += f'<p><strong>Total Paid:</strong> {total_paid_display}</p>'

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
            'uploadable': True,
            'is_done': is_done,
            # Event date in AM/PM format for CREATED
            'event_date': event.date.strftime('%b %d, %Y %I:%M %p') if event and label == 'CREATED' else None,
            # Booking details for CREATED
            'booking_details': {
                'event_type': booking.event_type,
                'location': booking.venue,
                'pax': booking.pax,
                'package': booking.package,
                'dish_list': booking.dish_list(), 
                'pasta': booking.pasta,
                'drink': booking.drink,
            } if label == 'CREATED' else None,
        })

    # Optional: extra event JSON for JS
    event_data = {
        'date': event.date.isoformat() if event else None,
        'event_title': event.title if event else None,
        'description': getattr(event, 'description', None),
        'event_logs': [
            {
                'label': log.label,
                'status': log.status,
                'total_due': getattr(log, 'total_due', None),
            }
            for log in EventStatusLog.objects.filter(booking=booking)
        ],
        'payment_transactions': [
            {
                'amount_paid': p.amount_paid,
                'payment_date': p.payment_date.isoformat() if p.payment_date else None
            }
            for p in (status_logs.get('PAYMENT').payment_transactions.all() if status_logs.get('PAYMENT') else [])
        ],
    }

    return render(request, 'custom_admin/booking_requests_status.html', {
        'booking': booking,
        'client': client,
        'status_steps': step_objs,
        'step_content_json': json.dumps(step_json, cls=DjangoJSONEncoder),
        'event_json': json.dumps(event_data, cls=DjangoJSONEncoder),
        'event': event,
    })
  
@csrf_exempt
@admin_required
@require_POST
def mark_step_done(request, id):
    try:
        label = request.POST['label']
        booking = get_object_or_404(BookingRequest, id=id)

        # --- Get or create EventStatusLog ---
        log, created = EventStatusLog.objects.get_or_create(
            booking=booking,
            label=label,
            defaults={'status': EventStatusLog.Status.DONE}
        )

        # --- PAYMENT Step ---
        if label == EventStatusLog.Label.PAYMENT:
            total_due = request.POST.get('total_due')
            if total_due is not None:
                log.total_due = float(total_due)

            amount_paid_str = request.POST.get('amount_paid')
            if amount_paid_str is None:
                return HttpResponseBadRequest("Missing amount_paid")
            amount_paid = float(amount_paid_str)

            # Only increment PaymentTransaction
            PaymentTransaction.objects.create(
                status_log=log,
                amount_paid=amount_paid,
                payment_date=now(),
            )

            # Update status based on total_paid
            total_paid = sum(pt.amount_paid for pt in log.payment_transactions.all())
            if log.total_due is not None and total_paid >= log.total_due:
                log.status = EventStatusLog.Status.DONE
            else:
                log.status = EventStatusLog.Status.PARTIALLY_PAID

        # --- Non-PAYMENT Steps ---
        else:
            log.status = request.POST.get('status', EventStatusLog.Status.DONE)

        log.save()

        # Create user notification for booking status update
        create_booking_status_notification(booking, log, request.user)

        # --- Handle file uploads for ALL steps ---
        for f in request.FILES.getlist('proof'):
            if not f or not f.name:
                continue  # skip empty files

            ext = os.path.splitext(f.name)[-1]
            unique_filename = f"booking_{booking.id}_{label.lower()}_{uuid.uuid4().hex}{ext}"

            if settings.ENVIRONMENT == "prod":
                # Cloudinary upload
                public_id = f"event_attachments/{unique_filename}"
                upload_result = cloudinary.uploader.upload(f, public_id=public_id)
                url_to_save = upload_result["secure_url"]

                # Prevent duplicates
                if not EventStatusAttachment.objects.filter(
                    booking=booking,
                    status_log=log,
                    cloudinary_url=url_to_save
                ).exists():
                    EventStatusAttachment.objects.create(
                        booking=booking,
                        status_log=log,
                        cloudinary_url=url_to_save,
                        uploaded_at=now()
                    )
            else:
                # Dev: store locally
                file_to_save = ContentFile(f.read(), name=unique_filename)
                if not EventStatusAttachment.objects.filter(
                    booking=booking,
                    status_log=log,
                    file=unique_filename
                ).exists():
                    EventStatusAttachment.objects.create(
                        booking=booking,
                        status_log=log,
                        file=file_to_save,
                        uploaded_at=now()
                    )

        return JsonResponse({'success': True, 'status': log.status})

    except KeyError:
        return HttpResponseBadRequest("Missing label or file")
    except ValueError:
        return HttpResponseBadRequest("Invalid numeric value for amount or total_due")


# ✅ Admin Notification API Endpoints
@admin_required
def admin_notifications(request):
    """Get all admin notifications"""
    notifications = AdminNotification.objects.all()[:50]  # Latest 50 notifications
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'notification_type': notification.notification_type,
            'is_read': notification.is_read,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'booking_id': notification.booking.id if notification.booking else None,
            'user_id': notification.user.id if notification.user else None,
            'user_name': notification.user.get_full_name() if notification.user else None,
        })
    
    return JsonResponse({
        'success': True,
        'notifications': notifications_data
    })


@admin_required
@csrf_exempt
@require_POST
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    AdminNotification.objects.filter(is_read=False).update(is_read=True)
    return JsonResponse({'success': True})

@admin_required
@csrf_exempt
@require_POST
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    try:
        notification = AdminNotification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except AdminNotification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})

@admin_required
@csrf_exempt
@require_POST
def mark_booking_notifications_read(request):
    """Mark all notifications for a specific booking as read"""
    try:
        import json
        data = json.loads(request.body)
        booking_id = data.get('booking_id')
        
        if not booking_id:
            return JsonResponse({'success': False, 'error': 'Booking ID required'})
        
        # Mark all notifications for this booking as read
        updated_count = AdminNotification.objects.filter(
            booking_id=booking_id,
            is_read=False
        ).update(is_read=True)
        
        return JsonResponse({
            'success': True,
            'updated_count': updated_count
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@admin_required
def admin_notifications_stream(request):
    """Server-Sent Events stream for real-time notifications"""
    def event_stream():
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connected', 'message': 'Notification stream connected'})}\n\n"
        
        # Keep connection alive and send notifications
        last_notification_id = 0
        while True:
            try:
                # Check for new notifications
                new_notifications = AdminNotification.objects.filter(
                    id__gt=last_notification_id,
                    is_read=False
                ).order_by('id')
                
                for notification in new_notifications:
                    # Determine notification type for frontend
                    notification_type = 'new_booking'  # default
                    if notification.notification_type == 'message_received':
                        notification_type = 'new_message'
                    elif notification.notification_type == 'payment_received':
                        notification_type = 'payment_received'
                    
                    data = {
                        'type': notification_type,
                        'id': notification.id,
                        'title': notification.title,
                        'message': notification.message,
                        'created_at': notification.created_at.strftime('%b %d, %Y %H:%M'),
                        'booking_id': notification.booking.id if notification.booking else None,
                        'user_id': notification.user.id if notification.user else None,
                        'chat_id': None  # We'll add this if needed for direct chat navigation
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                    last_notification_id = notification.id
                
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                break
    
    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'
    response['Access-Control-Allow-Origin'] = '*'
    return response


def create_booking_notification(booking_request):
    """Helper function to create notification when new booking is submitted"""
    try:
        user_name = booking_request.client.get_full_name() or booking_request.client.username
        
        notification = AdminNotification.objects.create(
            title="New Booking Request",
            message=f"New booking request from {user_name} for {booking_request.event_type}",
            notification_type='new_booking',
            booking=booking_request,
            user=booking_request.client
        )
        
        return notification
    except Exception as e:
        print(f"Error creating notification: {e}")
        return None


def create_message_notification(message, chat=None):
    """Helper function to create notification when new message is received"""
    try:
        from ..models import AdminNotification, BookingRequest
        
        # Only create admin notification for INCOMING messages (from users to admin)
        # Do NOT notify admin about their own outgoing messages
        if message.sender.is_staff:
            return None  # Don't create admin notification for admin's own messages
        
        sender_name = message.sender.get_full_name() or message.sender.username
        
        # Try to find if this chat belongs to a booking
        booking_request = None
        if chat:
            try:
                booking_request = BookingRequest.objects.get(chat=chat)
            except BookingRequest.DoesNotExist:
                booking_request = None
        
        # Create notification for incoming message from user
        notification = AdminNotification.objects.create(
            title=f"New Message from {sender_name}",
            message=f"{sender_name}: {message.content[:100]}{'...' if len(message.content) > 100 else ''}",
            notification_type='message_received',
            booking=booking_request,
            user=message.sender
        )
        
        return notification
    except Exception as e:
        print(f"Error creating message notification: {e}")
        return None

def create_booking_status_notification(booking, status_log, admin_user=None):
    """Create user notification when booking status is updated"""
    try:
        from ..models import UserNotification
        
        # Use provided admin user or default to first staff user
        if not admin_user:
            admin_user = User.objects.filter(is_staff=True).first()
        
        # Define notification messages for each step
        notification_data = {
            'CREATED': {
                'title': 'Booking Request Approved and Created',
                'message': f'Your booking request for {booking.event_type} on {booking.event_date.strftime("%B %d, %Y")} has been approved and created! Our team will start working on your event.',
                'type': 'booking_update'
            },
            'PAYMENT': {
                'title': 'Payment Update',
                'message': None,  # Will be set based on payment status
                'type': 'payment_update'
            },
            'BACKDROP': {
                'title': 'Backdrop Setup Complete',
                'message': f'Great news! The backdrop for your {booking.event_type} event has been set up and is ready. Everything is looking beautiful for your special day!',
                'type': 'booking_update'
            },
            'CATERING': {
                'title': 'Catering/Buffet Update',
                'message': f'Your catering and buffet setup for the {booking.event_type} event is now in progress. Our culinary team is preparing everything according to your specifications.',
                'type': 'booking_update'
            },
            'LOGISTICS': {
                'title': 'Lights/Sound/Logistics Update',
                'message': f'All lights, sound, and logistics for your {booking.event_type} event have been set up and tested. Everything is ready for your special occasion!',
                'type': 'booking_update'
            }
        }
        
        # Handle special case for payment notifications
        if status_log.label == 'PAYMENT':
            total_paid = sum(float(pt.amount_paid) for pt in status_log.payment_transactions.all())
            total_due = float(status_log.total_due) if status_log.total_due else 0
            
            if status_log.status == 'DONE':
                notification_data['PAYMENT']['title'] = 'Full Payment Received'
                notification_data['PAYMENT']['message'] = f'Thank you! We have received your full payment of ₱{total_paid:,.2f} for your {booking.event_type} booking. Your event is now fully confirmed!'
            elif status_log.status == 'PARTIALLY_PAID':
                remaining = total_due - total_paid
                notification_data['PAYMENT']['title'] = 'Partial Payment Received'
                notification_data['PAYMENT']['message'] = f'We have received your partial payment of ₱{total_paid:,.2f}. Remaining balance: ₱{remaining:,.2f}. Please complete the payment to finalize your booking.'
        
        # Get the notification data for this step
        step_data = notification_data.get(status_log.label)
        if not step_data or not step_data['message']:
            return None
        
        # Create the user notification
        notification = UserNotification.objects.create(
            user=booking.client,
            sender=admin_user,
            title=step_data['title'],
            message=step_data['message'],
            notification_type=step_data['type'],
            booking=booking
        )
        
        print(f"Created booking status notification: {notification.title} for user {booking.client.username}")
        return notification
        
    except Exception as e:
        print(f"Error creating booking status notification: {e}")
        return None

# ✅ User Notification Functions for Admin
@admin_required
def send_notification_to_user_view(request):
    """Admin view to send notification to a specific user"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        title = request.POST.get('title')
        message = request.POST.get('message')
        notification_type = request.POST.get('notification_type', 'admin_message')
        booking_id = request.POST.get('booking_id')
        
        try:
            user = User.objects.get(id=user_id)
            booking = None
            if booking_id:
                booking = BookingRequest.objects.get(id=booking_id)
            
            notification = UserNotification.objects.create(
                user=user,
                title=title,
                message=message,
                notification_type=notification_type,
                booking=booking,
                sender=request.user
            )
            
            messages.success(request, f'Notification sent to {user.get_full_name() or user.username}')
            return JsonResponse({'success': True, 'message': 'Notification sent successfully'})
            
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
        except BookingRequest.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Booking not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # GET request - show form
    users = User.objects.filter(is_active=True, is_staff=False)
    bookings = BookingRequest.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/send_user_notification.html', {
        'users': users,
        'bookings': bookings
    })

@admin_required
def send_notification_to_all_users_view(request):
    """Admin view to send notification to all users"""
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        notification_type = request.POST.get('notification_type', 'admin_message')
        
        try:
            users = User.objects.filter(is_active=True, is_staff=False)
            notifications_created = []
            
            for user in users:
                notification = UserNotification.objects.create(
                    user=user,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    sender=request.user
                )
                notifications_created.append(notification)
            
            messages.success(request, f'Notification sent to {len(notifications_created)} users')
            return JsonResponse({'success': True, 'message': f'Notification sent to {len(notifications_created)} users'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # GET request - show form
    return render(request, 'custom_admin/send_notification_all_users.html')

def create_user_booking_notification(booking_request, title, message, notification_type='booking_update'):
    """Helper function to create user notifications for booking updates"""
    try:
        notification = UserNotification.objects.create(
            user=booking_request.client,  # Use client instead of user
            title=title,
            message=message,
            notification_type=notification_type,
            booking=booking_request,
            sender=None  # System notification
        )
        return notification
    except Exception as e:
        print(f"Error creating user booking notification: {e}")
        return None

def create_user_message_notification(message, chat):
    """Helper function to create user notifications when admin sends a message"""
    try:
        # Get the booking request from the chat
        booking_request = getattr(chat, 'booking_request', None)
        if not booking_request:
            return None
        
        # Only create notification if the message is from staff/admin
        if not message.sender.is_staff:
            return None
        
        sender_name = message.sender.get_full_name() or message.sender.username
        
        notification = UserNotification.objects.create(
            user=booking_request.client,  # Use client instead of user
            title=f"New message from {sender_name}",
            message=f"{sender_name}: {message.content[:100]}{'...' if len(message.content) > 100 else ''}",
            notification_type='admin_message',
            booking=booking_request,
            sender=message.sender
        )
        
        return notification
    except Exception as e:
        print(f"Error creating user message notification: {e}")
        return None
