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

# Import notification helper
from .admin import create_booking_notification
    
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

    # Get ALL bookings regardless of status
    all_bookings = (BookingRequest.objects
                   .filter(client=user)
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
        "all_bookings": all_bookings,
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
    print(f"[DEBUG] Raw payload received: {raw}")
    
    try:
        data = json.loads(raw)
        print(f"[DEBUG] Parsed data: {data}")
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
    floorplan_path = None
    floorplan_display_name = None
    cloudinary_url = None
    
    if isinstance(data.get("location"), dict):
        venue = data["location"].get("venue", "")
        
        print(f"[DEBUG] Location data: {data.get('location')}")
        
        # Check if a floorplan was selected (URL from existing Cloudinary images)
        floorplan_filename = data["location"].get("floorplan_filename", "")
        floorplan_display_name = data["location"].get("floorplan_display_name", "")
        
        print(f"[DEBUG] floorplan_filename from frontend: '{floorplan_filename}'")
        print(f"[DEBUG] floorplan_display_name from frontend: '{floorplan_display_name}'")
        
        if floorplan_filename:
            # Use the filename directly as sent from frontend
            floorplan_path = floorplan_filename
            print(f"[DEBUG] Using floorplan filename: '{floorplan_path}'")
            
            # For production, we'll need the full URL for display purposes
            if settings.ENVIRONMENT == "prod" and floorplan_filename:
                # Reconstruct the Cloudinary URL from filename
                cloudinary_url = f"https://res.cloudinary.com/dlha5ojqe/image/upload/v1732438097/event_floorplans/{floorplan_filename}"
        else:
            print(f"[DEBUG] No floorplan_filename received")
            
        print(f"[DEBUG] Final values - venue: '{venue}', floorplan_path: '{floorplan_path}'")

    # ---------- 3) create BookingRequest ----------
    booking = BookingRequest.objects.create(
        client=request.user,
        chat=chat,
        celebrant_name=data.get("celebrant_name", ""),
        event_date=event_date,
        event_type=data.get("event_type", ""),
        pax=int(data.get("pax", 0)),
        venue=venue,
        floorplan=floorplan_path,
        floorplan_display_name=floorplan_display_name,
        cloudinary_url=cloudinary_url,
        color_motif=data.get("color_motif", ""),
        package=data.get("package", ""),
        dishes=", ".join(data.get("menu", {}).get("dishes", [])),
        pasta=data.get("menu", {}).get("pasta", ""),
        drink=data.get("menu", {}).get("drink", ""),
        raw_payload=data,
    )

    print(f"[DEBUG] Booking {booking.id} created with floorplan={booking.floorplan} cloudinary_url={booking.cloudinary_url}")

    # ---------- 3.5) Create admin notification ----------
    try:
        create_booking_notification(booking)
        print(f"[DEBUG] Notification created for booking {booking.id}")
    except Exception as e:
        print(f"[DEBUG] Failed to create notification: {e}")

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
    # Prepare venue display with floor plan if available
    venue_display = booking.venue
    if booking.floorplan_display_name:
        # Use the user-friendly display name (e.g., "Floor Plan 1")
        venue_display = f"{booking.venue} ({booking.floorplan_display_name})"
    elif booking.floorplan:
        # Fallback to filename if no display name is available (for old records)
        venue_display = f"{booking.venue} ({booking.floorplan})"

    rows = [
        ("Celebrant", booking.celebrant_name),
        ("Date", booking.event_date.strftime("%b %d %Y")),
        ("Type", booking.event_type),
        ("Pax", booking.pax),
        ("Venue", venue_display),
        ("Color Motif", booking.color_motif),
        ("Package", booking.package),
        ("Pasta", booking.pasta or "—"),
        ("Drink", booking.drink or "—"),
        ("Dishes", ", ".join(booking.dish_list()) or "—"),
    ]

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

def get_cloud_image_by_name(name) -> str:
    """Helper function to get images based on theme"""
    #Use Cloudinary
    cloud_img_public_ids = {
        # Wedding
        'wedding_100pax': 'wedding_100pax_mtujpw',
        'wedding_120pax': 'wedding_120pax_cnd4mj',
        'wedding_130pax': 'wedding_130pax_eamuys',
        'wedding_150pax': 'wedding_150pax_ftvdmh',
        'wedding_160pax': 'wedding_160pax_twyve5',
        'wedding_170pax': 'wedding_170pax_wb3mcl',
        'wedding_180pax': 'wedding_180pax_aotyby',
        'wedding_200pax': 'wedding_200pax_dsdfrl',
        'wedding_250pax': 'wedding_250pax_haxcqu',

        #Birthday
        'birthday_50pax': 'birthday_50pax_yjwdwl',
        'birthday_70pax': 'birthday_70pax_vew5ay',
        'birthday_80pax': 'birthday_80pax_vvu9g2',
        'birthday_100pax':'birthday_100pax_zheug3',
        'birthday_120pax':'birthday_120pax_r25otc',
        'birthday_130pax':'birthday_130pax_hz5unq',
        'birthday_150pax':'birthday_150pax_gtqtim',
        'birthday_170pax':'birthday_170pax_jtbtam',  
        'birthday_160pax':'birthday_160pax_b3ecp4',  
        'birthday_180pax': 'birthday_180_pax_hircrw',
        'birthday_200pax': 'birthday_200pax_gcjprl',

        #Kiddie Party
        'kiddieparty_50pax': 'kiddie_50pax_dpgjez',
        'kiddieparty_70pax': 'kiddie_70pax_hdawxz',
        'kiddieparty_80pax': 'kiddie_80pax_twgrmz',
        'kiddieparty_100pax': 'kiddie_100pax_z1jsn0',
        'kiddieparty_120pax': 'kiddie_120pax_soflwe',
        'kiddieparty_130pax': 'kiddie_130pax_yeyoka',
        'kiddieparty_150pax': 'kiddie_150pax_m7cdrz',
        'kiddieparty_160pax': 'kiddie_160pax_b5ezdz',
        'kiddieparty_170pax': 'kiddie_170pax_irkxsg',
        'kiddieparty_180pax': 'kiddie_180pax_knwwyp',
        'kiddieparty_200pax': 'kiddie_200pax_kmpgn4',

        #Christening
        'christening_50pax': 'christening_50pax_nxh9ke',
        'christening_70pax': 'christening_70pax_cyznmy',
        'christening_80pax': 'christening_80pax_slf4sl',
        'christening_100pax': 'christening_100pax_insvxv',
        'christening_120pax': 'christening_120pax_ua9yie',
        'christening_150pax': 'christening_150pax_idheaa',
        'christening_200pax': 'christening_200pax_t3vuye',

    }

    currentId = cloud_img_public_ids.get(name.lower().strip(), [])

    return cloudinary.utils.cloudinary_url('wedding_170pax_wb3mcl', secure=True)[0]