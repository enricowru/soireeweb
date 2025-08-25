from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.models import User
import json
import time

from ..models import UserNotification, BookingRequest

@login_required
def user_notifications(request):
    """Get all user notifications for the current user"""
    notifications = UserNotification.objects.filter(user=request.user).order_by('-created_at')[:50]  # Latest 50 notifications
    
    notification_data = []
    for notification in notifications:
        notification_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'notification_type': notification.notification_type,
            'booking_id': notification.booking.id if notification.booking else None,
            'sender_name': notification.sender.get_full_name() if notification.sender else 'System',
            'is_read': notification.is_read,
            'created_at': notification.created_at.strftime('%b %d, %Y %H:%M'),
        })
    
    return JsonResponse({
        'success': True,
        'notifications': notification_data
    })

@login_required
@csrf_exempt
@require_POST
def mark_all_user_notifications_read(request):
    """Mark all notifications as read for the current user"""
    updated_count = UserNotification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    return JsonResponse({
        'success': True,
        'message': f'{updated_count} notifications marked as read'
    })

@login_required
@csrf_exempt
@require_POST
def mark_user_notification_read(request, notification_id):
    """Mark a specific notification as read for the current user"""
    try:
        notification = UserNotification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except UserNotification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})

@login_required
@csrf_exempt
@require_POST
def mark_user_booking_notifications_read(request):
    """Mark all notifications for a specific booking as read for the current user"""
    try:
        data = json.loads(request.body)
        booking_id = data.get('booking_id')
        
        if booking_id:
            updated_count = UserNotification.objects.filter(
                user=request.user,
                booking_id=booking_id,
                is_read=False
            ).update(is_read=True)
            
            return JsonResponse({
                'success': True,
                'message': f'{updated_count} booking notifications marked as read'
            })
        
        return JsonResponse({'success': False, 'error': 'Booking ID is required'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})

@login_required
def user_notifications_stream(request):
    """Server-Sent Events stream for real-time user notifications"""
    def event_stream():
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connected', 'message': 'User notification stream connected'})}\n\n"
        
        # Keep connection alive and send notifications
        last_notification_id = 0
        while True:
            try:
                # Check for new notifications for the current user
                new_notifications = UserNotification.objects.filter(
                    id__gt=last_notification_id,
                    user=request.user,
                    is_read=False
                ).order_by('id')
                
                for notification in new_notifications:
                    # Determine notification type for frontend
                    notification_type = 'admin_message'  # default
                    if notification.notification_type == 'booking_update':
                        notification_type = 'booking_update'
                    elif notification.notification_type == 'event_reminder':
                        notification_type = 'event_reminder'
                    elif notification.notification_type == 'payment_update':
                        notification_type = 'payment_update'
                    
                    data = {
                        'type': notification_type,
                        'id': notification.id,
                        'title': notification.title,
                        'message': notification.message,
                        'created_at': notification.created_at.strftime('%b %d, %Y %H:%M'),
                        'booking_id': notification.booking.id if notification.booking else None,
                        'sender_name': notification.sender.get_full_name() if notification.sender else 'System',
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

def create_user_notification(user, title, message, notification_type='admin_message', booking=None, sender=None):
    """Helper function to create user notifications"""
    try:
        notification = UserNotification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            booking=booking,
            sender=sender
        )
        return notification
    except Exception as e:
        print(f"Error creating user notification: {e}")
        return None

def send_notification_to_user(user_id, title, message, notification_type='admin_message', booking_id=None, sender_user=None):
    """Function to send notification to a specific user - can be called from admin views"""
    try:
        from ..models import UserNotification, User, BookingRequest
        
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
            sender=sender_user
        )
        
        return notification
    except (User.DoesNotExist, BookingRequest.DoesNotExist) as e:
        print(f"Error sending notification to user: {e}")
        return None

def send_notification_to_all_users(title, message, notification_type='admin_message', sender_user=None):
    """Function to send notification to all users - can be called from admin views"""
    try:
        from ..models import UserNotification, User
        
        users = User.objects.filter(is_active=True, is_staff=False)
        notifications_created = []
        
        for user in users:
            notification = UserNotification.objects.create(
                user=user,
                title=title,
                message=message,
                notification_type=notification_type,
                sender=sender_user
            )
            notifications_created.append(notification)
        
        return notifications_created
    except Exception as e:
        print(f"Error sending notification to all users: {e}")
        return []
