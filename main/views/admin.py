from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from ..forms import EventForm, AdminEditForm
from ..models import Event, EventHistory, Chat, BookingRequest, EventStatusLog, EventStatusAttachment, BookingRequest, PaymentTransaction
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
            access_code=event.access_code,
            checkin_code=event.checkin_code,
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
            "mobile":    getattr(getattr(u, "profile", None), "mobile", ""),
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
    return render(request, "custom_admin/booking_request_chat.html", {
        "bookings": bookings
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
