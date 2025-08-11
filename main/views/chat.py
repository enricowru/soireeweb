from .auth import login_required
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from ..models import User
from ..models import Chat
from ..models import Message
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import StreamingHttpResponse, HttpResponseNotAllowed
from main.sse import booking_events  
from asgiref.sync import async_to_sync
import json
import asyncio
from channels.layers import get_channel_layer

@csrf_exempt
def send_booking_message(request, id):

    if request.method != "POST":
        print("Wrong method:", request.method)
        return HttpResponseBadRequest("Only POST allowed.")

    try:

        body = json.loads(request.body)

        message_content = body.get("message")
        if not message_content:
            return HttpResponseBadRequest("Missing message")


        chat = get_object_or_404(Chat, id=id)

        message_obj = Message.objects.create(
            chat=chat,
            sender=request.user,
            content=message_content,
            is_read=False,
        )


        data = {
            "id": message_obj.id,
            "chat_id": chat.id,
            "message": message_obj.content,
            "sender": {
                "id": request.user.id,
                "username": request.user.username,
            },
            "timestamp": message_obj.timestamp.isoformat(),
        }

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"booking_{id}",
            {
                "type": "booking_message",
                "data": data
            }
        )

        return JsonResponse({"status": "sent", "data": data})

    except Exception as e:
        print("Error occurred:", e)
        return HttpResponseBadRequest(str(e))

@login_required
def create_chat(request):
    if request.method == 'POST':
        chat_type = request.POST.get('chat_type')
        
        if chat_type == 'direct':
            user_id = request.POST.get('user_id')
            other_user = get_object_or_404(User, id=user_id)
            
            # Check if chat already exists
            existing_chat = Chat.objects.filter(
                participants=request.user
            ).filter(
                participants=other_user
            ).filter(
                is_group_chat=False
            ).first()
            
            if existing_chat:
                return redirect('chat_detail', chat_id=existing_chat.id)
            
            chat = Chat.objects.create(is_group_chat=False)
            chat.participants.add(request.user, other_user)
            
        else:  # group chat
            name = request.POST.get('group_name')
            participant_ids = request.POST.getlist('participants')
            
            chat = Chat.objects.create(
                is_group_chat=True,
                name=name
            )
            chat.participants.add(request.user)
            chat.participants.add(*participant_ids)
        
        return redirect('chat_detail', chat_id=chat.id)
    
    return redirect('chat_list')

@login_required
def send_message(request):
    if request.method == 'POST':
        chat_id = request.POST.get('chat_id')
        content = request.POST.get('message')
        
        chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
        
        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            content=content
        )
        
        # Update chat's updated_at timestamp
        chat.save()  # This will update the updated_at field
        
        return JsonResponse({
            'success': True,
            'message': {
                'content': message.content,
                'timestamp': message.timestamp.strftime('%H:%M')
            }
        })
    
    return JsonResponse({'success': False}, status=400)

@login_required
def chat_list(request):
    raw_chats = Chat.objects.filter(participants=request.user).order_by('-updated_at')
    available_users = User.objects.exclude(id=request.user.id)

    enriched_chats = []
    active_chat = raw_chats.first() if raw_chats.exists() else None
    active_other_user = None

    for chat in raw_chats:
        if chat.is_group_chat:
            other_user = None
        else:
            other_user = chat.participants.exclude(id=request.user.id).first()

        enriched_chat = {
            'chat': chat,
            'other_user': other_user,
        }

        enriched_chats.append(enriched_chat)

        if chat == active_chat:
            active_other_user = other_user

    return render(request, 'main/chat.html', {
        'chats': enriched_chats,
        'active_chat': active_chat,
        'active_other_user': active_other_user,
        'available_users': available_users,
    })



@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
    chats = Chat.objects.filter(participants=request.user).order_by('-updated_at')
    available_users = User.objects.exclude(id=request.user.id)
    
    chat.messages.filter(~Q(sender=request.user), is_read=False).update(is_read=True)
    
    return render(request, 'main/chat.html', {
        'chats': chats,
        'active_chat': chat,
        'available_users': available_users
    })

@login_required
def chat_messages_json(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
    qs   = chat.messages.select_related("sender").order_by("timestamp")
    data = [{
        "html" : m.content,                
        "mine" : m.sender_id == request.user.id,
        "ts"   : m.timestamp.isoformat()
    } for m in qs]
    return JsonResponse(data, safe=False)