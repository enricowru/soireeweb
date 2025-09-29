from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponseServerError, JsonResponse
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

def format_color_motif_display(color_motif_str):
    """Format color motif for display - handles both old string format and new JSON array"""
    if not color_motif_str:
        return "—"
    
    try:
        # Try to parse as JSON array (new format)
        colors = json.loads(color_motif_str)
        if isinstance(colors, list):
            return " → ".join(colors)  # Display as "Color1 → Color2 → Color3"
        else:
            return color_motif_str  # Fallback to string display
    except (json.JSONDecodeError, TypeError):
        # If it's not valid JSON, treat as old string format
        return color_motif_str
    
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
        
        # Check for floorplan data - could be regular floorplan or AI-generated
        floorplan_filename = data["location"].get("floorplan_filename", "")
        floorplan_display_name = data["location"].get("floorplan_display_name", "")
        ai_estimations = data["location"].get("ai_estimations", "")
        uploaded_cloudinary_url = data["location"].get("cloudinary_url", "")
        
        print(f"[DEBUG] floorplan_filename from frontend: '{floorplan_filename}'")
        print(f"[DEBUG] floorplan_display_name from frontend: '{floorplan_display_name}'")
        print(f"[DEBUG] ai_estimations from frontend: '{ai_estimations}'")
        print(f"[DEBUG] uploaded_cloudinary_url from frontend: '{uploaded_cloudinary_url}'")
        
        # Handle uploaded image with AI analysis
        if uploaded_cloudinary_url and ai_estimations:
            # Store filename in floorplan field and Cloudinary URL in cloudinary_url field
            floorplan_path = floorplan_filename
            cloudinary_url = uploaded_cloudinary_url
            # The floorplan_display_name will contain the actual AI estimation results
            print(f"[DEBUG] Using uploaded image with AI analysis")
        # Handle AI-generated floorplan (dimensions only)
        elif ai_estimations and not uploaded_cloudinary_url:
            # Store filename in floorplan field, leave cloudinary_url empty
            floorplan_path = floorplan_filename  # Use filename instead of AI estimations
            cloudinary_url = None  # No image URL for dimensions-only plans
            # The floorplan_display_name will contain the actual AI estimation results
            print(f"[DEBUG] Using dimensions with AI analysis - storing filename")
        elif floorplan_filename:
            # Regular floorplan - use the filename directly as sent from frontend
            floorplan_path = floorplan_filename
            print(f"[DEBUG] Using floorplan filename: '{floorplan_path}'")
            
            # For production, we'll need the full URL for display purposes
            if settings.ENVIRONMENT == "prod" and floorplan_filename:
                # Reconstruct the Cloudinary URL from filename
                cloudinary_url = f"https://res.cloudinary.com/dlha5ojqe/image/upload/v1732438097/event_floorplans/{floorplan_filename}"
        else:
            print(f"[DEBUG] No floorplan data received")
            
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
        color_motif=json.dumps(data.get("color_motif", [])),
        theme_name=data.get("theme_name", ""),
        theme_urls=data.get("theme_urls", []),
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

    # Update chat's updated_at field to reflect new message
    chat.save(update_fields=['updated_at'])

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
        ("Color Motif", format_color_motif_display(booking.color_motif)),
        ("Package", booking.package),
        ("Pasta", booking.pasta or "—"),
        ("Drink", booking.drink or "—"),
        ("Dishes", ", ".join(booking.dish_list()) or "—"),
    ]

    return (
        "Booking request received. Please wait for the admin to reply."
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

@login_required
def user_booking_details_api(request, booking_id):
    """API endpoint to get booking details for the user's own bookings"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    try:
        # Ensure user can only access their own bookings - use 'client' field not 'user'
        booking = get_object_or_404(BookingRequest, id=booking_id, client=request.user)
        
        # Color names mapping (same as in bookhere.html) - make case-insensitive
        color_images_raw = {
            'Orange': 'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757770591/orange_beq6g2.jpg',
            'Red': 'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757770587/red_ddg0wx.jpg',
            'Royal Blue': 'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757770577/royalblue_bhz1ow.jpg',
            'Rust Red': 'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757770507/rustred_q2fgz8.jpg',
            'Yellow': 'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757770509/yellow_v2d7ma.jpg',
            'Dark Green': 'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757770513/darkgreen_zunnwu.jpg',
            'Gray': 'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757770517/gray_b9dlwb.jpg',
            'Lake Blue': 'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757770521/lakeblue_zsjili.jpg',
            'Brown': 'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757770525/brown_kg72gb.jpg',
            'Champagne': 'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757770529/champagne_rwkvv5.jpg',
            'Pink': 'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757770533/pink_b9wuoq.jpg',
            'Light Pink': 'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757770537/lightpink_jb3gqb.jpg',
            'Off White': 'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757770541/offwhite_qu62zb.jpg',
            'Gold': 'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757770545/gold_cpuahs.jpg',
            'Purple': 'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757770549/purple_nsrd84.jpg',
            'White': 'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757770553/white_aupuke.jpg',
            'Sky Blue': 'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757770557/skyblue_i6mdz7.jpg',
            'Dark Yellow': 'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757770561/darkyellow_d0pxgh.jpg',
            'Olive Green': 'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757770565/olivegreen_ijgrtv.jpg',
            'Mint': 'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757770569/mint_h8nbh0.jpg',
            'Skin Pink': 'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757770573/skinpink_ibuunv.jpg'
        }
        
        # Create case-insensitive mapping
        color_images = {}
        for color_name, url in color_images_raw.items():
            color_images[color_name] = url
            color_images[color_name.lower()] = url
            color_images[color_name.upper()] = url
        
        # Food names mapping (same as in bookhere.html)
        food_names = {
            # Beef dishes
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757782677/beefwithgravysauce_qyrcsv.jpg': 'Beef with Gravy Sauce',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757782677/beefbroccolli_c3hbve.jpg': 'Beef Brocolli',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757782677/beefkarekare_n317oe.jpg': 'Beef Kare-Kare',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757782676/lenguapastel_ofenul.jpg': 'Lengua Pastel',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757782676/potroastbeef_tfekkp.jpg': 'Pot Roast Beef',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757782676/beefcaldereta_ellvq7.jpg': 'Beef Caldereta',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757782675/garlicbeef_othv0q.jpg': 'Garlic Beef',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757782675/beefteriyaki_yhszrn.jpg': 'Beef Teriyaki',
            
            # Pork dishes
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757783626/hawaiianspareribs_ouwkwg.jpg': 'Hawaiian Spare Ribs',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757783626/lenguapastel_kodvks.jpg': 'Lengua Pastel',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757783625/lechonkawali_v3v04s.jpg': 'Lechon Kawali',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757783624/karekarebagnet_paezmf.jpg': 'Kare-Kare Bagnet',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757783623/roastporkraisinsauce_zcyjjj.jpg': 'Roast Pork Raisin Sauce',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757783623/porkteriyaki_iyrgu2.jpg': 'Pork Teriyaki',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757783623/grilledliempo_fdq0kp.jpg': 'Grilled Liempo',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757783623/roastporkhawaiian_hbkpf1.jpg': 'Roast Pork Hawaiian',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757783622/porkmorcon_p5sdud.jpg': 'Pork Morcon',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757783622/porkhamonado_noxvzn.jpg': 'Pork Hamonado',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757783622/porkcaldereta_lddwze.jpg': 'Pork Caldereta',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757783622/porkmenudo_mimd9h.jpg': 'Pork Menudo',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757783621/porkbbq_hrudyt.jpg': 'Pork BBQ',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757783621/lumpiangshanghai_p4ralv.jpg': 'Lumpiang Shanghai',
            
            # Chicken dishes
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757784429/chickenpastel_mgfrq5.jpg': 'Chicken Pastel',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757784418/chickenbbq_lkpnac.jpg': 'Chicken BBQ',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757784417/orangechicken_jo3vc3.jpg': 'Orange Chicken',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757784416/chickenlollipop_z9dwso.jpg': 'Chicken Lollipop',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757784415/butteredchicken_hgsxnr.jpg': 'Buttered Chicken',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757784415/chickencordonbleu_y9qjjw.jpg': 'Chicken Cordon Bleu',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757784415/honeyglazedchicken_d4evdv.jpg': 'Honey Glazed Chicken',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757784414/breadedfriedchicken_agzutr.jpg': 'Breaded Fried Chicken',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757784414/hongkongchicken_ymcmk3.jpg': 'Hong Kong Chicken',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757784413/royalchicken_tmd2ja.jpg': 'Royal Chicken',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757784413/chickenteriyaki_azw467.jpg': 'Chicken Teriyaki',
            
            # Seafood dishes
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757784686/squidlemonsauce_o5rhz6.jpg': 'Squid Lemon Sauce',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757784680/fishwithchilisauce_gd0icq.jpg': 'Fish with Chili Sauce',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757784678/miexedseafoodsvegetables_puvtvi.jpg': 'Mixed Seafoods & Vegetables',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757784678/fishtartarsauce_ln7vfb.jpg': 'Fish Tartar Sauce',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757784677/fishtofu_rsofxm.jpg': 'Fish Tofu',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757784677/tempura_g0w6dz.jpg': 'Tempura',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757784676/calamares_hhy97q.jpg': 'Calamares',
            
            # Pasta dishes
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757785111/pancit_pnh4ho.jpg': 'Pancit',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757785111/fettucinealfredo_ytvr6y.jpg': 'Fettuccine Alfredo',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757785110/linguine_g4nteu.jpg': 'Linguine',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757785110/lasagnarolls_b0esab.jpg': 'Lasagna Rolls',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757785109/bakedmac_dlltkg.jpg': 'Baked Mac',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757785109/rigatoni_wko7vk.jpg': 'Rigatoni',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757785109/spaghetti_gzwqbu.jpg': 'Spaghetti',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757785107/penne_twzzq9.jpg': 'Penne',
            
            # Drinks
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757785373/pineapplejuice_svj2xb.jpg': 'Pineapple Juice',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757785364/orangejuice_jtybgq.jpg': 'Orange Juice',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757785363/lemontea_k3bvj4.jpg': 'Lemon Tea',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757785362/fourseasons_yocljk.jpg': 'Four Seasons',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757785362/bluelemonade_pwthcl.jpg': 'Blue Lemonade',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757785362/cucumberlemonade_fciacg.jpg': 'Cucumber Lemonade',
            'https://res.cloudinary.com/dzjrdqkiw/image/upload/v1757785360/redtea_atzt39.jpg': 'Red Tea'
        }
        
        # Create reverse mapping (name to URL) for finding images
        name_to_url = {name: url for url, name in food_names.items()}
        
        # Parse dishes into a list 
        dishes_list = [dish.strip() for dish in booking.dishes.split(',') if dish.strip()] if booking.dishes else []
        
        # Create dishes with images
        dishes_with_images = []
        for dish_name in dishes_list:
            dish_url = name_to_url.get(dish_name, '')
            dishes_with_images.append({
                'name': dish_name,
                'image_url': dish_url
            })
        
        # Add pasta and drink with images if they exist
        pasta_image = name_to_url.get(booking.pasta, '') if booking.pasta else ''
        drink_image = name_to_url.get(booking.drink, '') if booking.drink else ''
        
        # Get color motif as a list with images
        color_motif_list = []
        color_motif_with_images = []
        if booking.color_motif:
            # Split by arrow or comma to handle different formats
            colors = booking.color_motif.replace(' → ', ',').replace('→', ',').split(',')
            color_motif_list = [color.strip() for color in colors if color.strip()]
            
            # Create colors with images
            for color_name in color_motif_list:
                # Try exact match first, then case-insensitive variations
                color_image = (color_images.get(color_name) or 
                             color_images.get(color_name.lower()) or 
                             color_images.get(color_name.upper()) or 
                             color_images.get(color_name.title()) or '')

                color_motif_with_images.append({
                    'name': color_name,
                    'image_url': color_image
                })
        
        data = {
            'event_type': booking.event_type or '',
            'event_date': booking.event_date.strftime('%B %d, %Y') if booking.event_date else '',
            'celebrant_name': booking.celebrant_name or '',
            'pax': str(booking.pax) if booking.pax else '',
            'venue': booking.venue or '',
            'color_motif': format_color_motif_display(booking.color_motif) or '',
            'color_motif_list': color_motif_list,
            'color_motif_with_images': color_motif_with_images,
            'package': booking.package or '',
            'dishes': booking.dishes or '',
            'dishes_list': dishes_list,
            'dishes_with_images': dishes_with_images,
            'pasta': booking.pasta or '',
            'pasta_image': pasta_image,
            'drink': booking.drink or '',
            'drink_image': drink_image,
            'theme_name': booking.theme_name or '',
            'theme_urls': booking.theme_urls or [],
            'floorplan_name': booking.floorplan_display_name or '',
            'floorplan_url': booking.display_url,
        }
        
        return JsonResponse(data)
    except BookingRequest.DoesNotExist:
        return JsonResponse({'error': 'Booking not found or access denied'}, status=404)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in user_booking_details_api: {error_details}")
        return JsonResponse({'error': str(e), 'details': error_details}, status=500)