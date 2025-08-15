from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponseServerError
import json, asyncio
from .auth import login_required
from ..models import BookingRequest, Chat, Message, User
from django.utils import timezone
from django.utils.html import format_html_join
import datetime as _dt
from django.contrib.auth.decorators import login_required
from channels.layers import get_channel_layer
import json, uuid, datetime as _dt
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.html import format_html, format_html_join

# Optional: only import cloudinary in prod
if settings.ENVIRONMENT == "prod":
    import cloudinary.uploader
    
def save_floorplan_with_custom_name(uploaded_file, booking_id):
    """
    Save the uploaded floorplan image either locally (dev) or to Cloudinary (prod).
    Returns the value to store in booking.floorplan.
    """
    ext = uploaded_file.name.split('.')[-1]
    filename = f"booking_{booking_id}_{uuid.uuid4().hex[:8]}.{ext}"

    if settings.ENVIRONMENT == "prod":
        public_id = f"booking_floorplans/{filename}"
        upload_result = cloudinary.uploader.upload(uploaded_file, public_id=public_id)
        return upload_result["secure_url"]  # full URL
    else:
        path = f"booking_floorplans/{filename}"
        saved_path = default_storage.save(path, uploaded_file)
        return saved_path  # just path, no MEDIA_URL prefix


@login_required
def editprofile(request):
    return render(request, 'editprofile.html')

@login_required
def bookhere(request):
    return render (request, 'bookhere.html')

@login_required
def my_bookings(request):
    user = request.user

    active = (BookingRequest.objects
              .filter(client=user, status__in=["draft", "confirmed"])
              .order_by("-created_at"))

    past = (BookingRequest.objects
            .filter(client=user, status="rejected")
            .order_by("-created_at"))


    chats = (
        Chat.objects
            .filter(participants=user)                 
            .prefetch_related(
                "participants",
                "messages__sender",
                "request_booking"
            )
            .order_by("-updated_at")
    )

    first_chat = chats.first()
    first_booking = BookingRequest.objects.filter(chat=first_chat).first()
    booking = BookingRequest.objects.filter(chat=first_chat).first()

    booking_date = booking.event_date if booking else None
    event_type   = booking.event_type if booking else ""

    first_messages = (
        first_chat.messages.select_related("sender")[:25] if first_chat else []
    )

    booking_meta = f"{event_type} • {booking_date.strftime('%b %d, %Y')} " if booking and booking_date else ""

    context = {
        "active_bookings": active,
        "past_bookings": past,
        "first_chat": first_chat,
        "first_messages": first_messages,
        "first_booking": first_booking, 
        "booking_meta": booking_meta, 
    }

  
    return render(request, "my_bookings.html", context)

@login_required
def bookhere_submit(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed")

    # ---------- parse JSON ----------
    raw = request.POST.get("payload") or "{}"
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Bad JSON")

    # ---------- 1) make / fetch the admin chat ----------
    try:
        admin_user = User.objects.get(username="admin")
    except User.DoesNotExist:
        return HttpResponseServerError("Admin user 'admin' not found.")

    chat = Chat.objects.create(is_group_chat=False)
    chat.participants.add(request.user, admin_user)

    # ---------- 2) prepare booking fields ----------
    event_date = _dt.date.fromisoformat(data["date"])
    venue = ""
    floorplan_url = None
    if isinstance(data.get("location"), dict):
        venue = data["location"].get("venue", "")
        floorplan_file = request.FILES.get("floorplan-payload")
        
        # Always log what we see, even if None
        print(f"[DEBUG] floorplan_file: {floorplan_file}")

        if floorplan_file:
            print(f"[DEBUG] Received floorplan file: {floorplan_file.name} ({floorplan_file.size} bytes)")
            saved_value = save_floorplan_with_custom_name(floorplan_file, chat.id)
            print(f"[DEBUG] save_floorplan_with_custom_name returned: {saved_value}")
            floorplan_url = saved_value  # now always a string (local path or URL)

    # ---------- 3) create BookingRequest ----------
    booking = BookingRequest.objects.create(
        client=request.user,
        chat=chat,
        celebrant_name=data.get("celebrant_name", ""),
        event_date=event_date,
        event_type=data.get("event_type", ""),
        pax=int(data.get("pax", 0)),
        venue=venue,
        floorplan=floorplan_url,
        color_motif=data.get("color_motif", ""),
        package=data.get("package", ""),
        dishes=", ".join(data.get("menu", {}).get("dishes", [])),
        pasta=data.get("menu", {}).get("pasta", ""),
        drink=data.get("menu", {}).get("drink", ""),
        raw_payload=data,
    )

    print(f"[DEBUG] Booking {booking.id} created with floorplan={booking.floorplan}")

    # ---------- 4) first system message ----------
    msg_html = booking_summary(booking)

    Message.objects.create(
        chat=chat,
        sender=admin_user,
        content=msg_html,
        is_read=False,
    )

    # ---------- 5) push via WebSocket ----------
    ws_payload = {
        "type": "booking_message",
        "data": {
            "type": "booking",
            "chatId": chat.id,
            "html": msg_html,
            "label": booking.short_label(),
            "when": timezone.now().isoformat(),
            "sender": {"id": admin_user.id, "username": admin_user.username},
        },
    }
    _push_ws_event(chat.id, ws_payload)

    return redirect("my_bookings")

def booking_summary(booking) -> str:
    # Compute display URL
    floorplan_url = None
    if booking.floorplan:
        if settings.ENVIRONMENT == "prod":
            floorplan_url = booking.floorplan
        else:
            floorplan_url = f"{settings.MEDIA_URL}{booking.floorplan}"

    rows = [
        ("Celebrant", booking.celebrant_name),
        ("Date", booking.event_date.strftime("%b %d %Y")),
        ("Type", booking.event_type),
        ("Pax", booking.pax),
        ("Venue", booking.venue),
        ("Color Motif", booking.color_motif),
        ("Package", booking.package),
        ("Pasta", booking.pasta or "—"),
        ("Drink", booking.drink or "—"),
        ("Dishes", ", ".join(booking.dish_list()) or "—"),
    ]

    # Add floorplan image row only if present
    if floorplan_url:
        rows.append((
            "Floor Plan",
            format_html(
                '<img src="{}" alt="Floor plan" style="max-width:300px;border:1px solid #ccc;border-radius:4px;">',
                floorplan_url
            )
        ))

    return (
        "<strong>New booking received</strong><br>"
        "<dl class='mb-0'>"
        + format_html_join(
            "", "<dt class='fw-semibold mb-0'>{}</dt><dd class='mb-1'>{}</dd>", rows
        )
        + "</dl>"
        + "<p>Please enter your name, contact information, and the names of the expected attendees. Thank you.</p>"
    )


def _push_ws_event(chat_id: int, payload: dict):
    """
    Sends the payload to all WebSocket clients in the booking group.
    """
    channel_layer = get_channel_layer()

    async def _send():
        await channel_layer.group_send(f"booking_{chat_id}", payload)

    asyncio.run(_send())