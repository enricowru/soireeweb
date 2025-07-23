from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponseServerError
import json, asyncio, threading
from .auth import login_required
from main.sse import booking_events
from ..models import BookingRequest, Chat, Message, User
from django.utils import timezone
from django.utils.html import format_html_join
import datetime as _dt

def booking_summary(booking) -> str:
    """
    Initial message to be sent after requesting a booking.
    """
    rows = [
        ("Date",      booking.event_date.strftime("%b %d %Y")),
        ("Type",      booking.event_type),
        ("Pax",       booking.pax),
        ("Venue",     booking.location),
        ("Package",   booking.package),
        ("Pasta",     booking.pasta or "—"),
        ("Drink",     booking.drink or "—"),
        ("Dishes",    ", ".join(booking.dish_list()) or "—"),
    ]
    # build a mini table (<dl>) — easy to style in chat
    return (
        "<strong>New booking received</strong><br>"
        "<dl class='mb-0'>" +
        format_html_join(
            "", "<dt class='fw-semibold mb-0'>{}</dt><dd class='mb-1'>{}</dd>", rows
        ) +
        "</dl>" +
        "<p>Please enter your name, contact information, and the names of the expected attendees. Thank you.</p>"
        )

def _fire_and_forget(chat_id: int, payload: dict):
    def _runner():
        asyncio.run(booking_events.push(chat_id, payload))
    threading.Thread(target=_runner, daemon=True).start()

@login_required
def editprofile(request):
    return render(request, 'editprofile.html')

@login_required
def bookhere(request):
    return render (request, 'bookhere.html')

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

    admin_user  = None
    # ---------- 1) make / fetch the admin chat ----------
    try:
        admin_user = User.objects.get(username="admin")
    except User.DoesNotExist:
        return HttpResponseServerError("Admin user 'admin' not found.")

    # one‑to‑one chat between this client and admin
    chat = Chat.objects.create(is_group_chat=False)
    chat.participants.add(request.user, admin_user)

    # ---------- 2) create BookingRequest linked to chat ----------
    event_date = _dt.date.fromisoformat(data["date"])

    booking = BookingRequest.objects.create(
        client      = request.user,
        chat        = chat,             
        event_date  = event_date,
        event_type  = data["event_type"],
        pax         = int(data["pax"]),
        location    = data["location"],
        color_hex   = data["color_hex"],
        package     = data["package"],
        dishes      = ", ".join(data["menu"].get("dishes", [])),
        pasta       = data["menu"].get("pasta", ""),
        drink       = data["menu"].get("drink", ""),
        raw_payload = data,
    )

    # ---------- 3) first system message ----------
    msg_html = booking_summary(booking)  # returns ready‑to‑display HTML

    Message.objects.create(
        chat   = chat,
        sender = admin_user,   # “system/admin” author
        content= msg_html,
        is_read= False,
    )

    # ---------- 4) push SSE (fire‑and‑forget) ----------
    _fire_and_forget(chat.id, {
        "type"   : "booking",
        "chatId" : chat.id,
        "html"   : msg_html,
        "label"  : booking.short_label(),
        "when"   : timezone.now().isoformat(),
    })

    return redirect("my_bookings")

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