from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from ..models import MobilePost, Comment, Like
import json

# -------------------------------
# 🔓 Public: Get All Posts
# -------------------------------
@csrf_exempt
def get_all_posts(request):
    """Return all mobile posts.

    Assumes each post has at least one valid image (enforced via admin constraint), so no
    defensive skipping logic is required here anymore.
    """
    user = getattr(request, 'user', AnonymousUser())
    posts = MobilePost.objects.all().order_by('-created_at')
    data = []
    for post in posts:
        image_urls = [img.image.url for img in post.images.all()]
        data.append({
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'created_at': post.created_at.isoformat(),
            'images': image_urls,
            'like_count': post.likes.count(),
            'comment_count': post.comments.count(),
            'is_liked': post.likes.filter(user=user).exists() if user.is_authenticated else False,
        })
    return JsonResponse({'posts': data}, status=200)


# -------------------------------
# 🔓 Public: Get Post Details
# -------------------------------
@csrf_exempt
def get_post_detail(request, post_id):
    try:
        post = MobilePost.objects.get(id=post_id)
    except MobilePost.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)

    comments = post.comments.select_related('user').order_by('-created_at')
    user = getattr(request, 'user', AnonymousUser())

    response = {
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'created_at': post.created_at.isoformat(),
        'images': [img.image.url for img in post.images.all()],
        'like_count': post.likes.count(),
        'comment_count': post.comments.count(),
        'is_liked': post.likes.filter(user=user).exists() if user.is_authenticated else False,
        'comments': [{
            'id': c.id,
            'user': c.user.get_full_name() or c.user.username,
            'content': c.content,
            'created_at': c.created_at.isoformat()
        } for c in comments]
    }
    return JsonResponse(response, status=200)

# -------------------------------
# 🔐 POST: Toggle Like
# -------------------------------
@csrf_exempt
@require_http_methods(["POST"])
def toggle_like(request, post_id):
    user = getattr(request, 'user', AnonymousUser())
    if not user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        post = MobilePost.objects.get(id=post_id)
    except MobilePost.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)

    existing = Like.objects.filter(post=post, user=user).first()
    if existing:
        existing.delete()
        return JsonResponse({'message': 'Post unliked', 'liked': False}, status=200)
    else:
        Like.objects.create(post=post, user=user)
        return JsonResponse({'message': 'Post liked', 'liked': True}, status=200)

# -------------------------------
# 🔐 POST: Submit Comment
# -------------------------------
@csrf_exempt
@require_http_methods(["POST"])
def submit_comment(request, post_id):
    user = getattr(request, 'user', AnonymousUser())
    if not user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        if not content:
            return JsonResponse({'error': 'Comment cannot be empty'}, status=400)

        post = MobilePost.objects.get(id=post_id)
        Comment.objects.create(post=post, user=user, content=content)
        return JsonResponse({'message': 'Comment added successfully'}, status=201)
    except MobilePost.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
