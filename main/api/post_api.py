from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from ..models import MobilePost, Comment, Like
from django.db import connection
import json

# -------------------------------
# 🔓 Public: Get All Posts
# -------------------------------
@csrf_exempt
def get_all_posts(request):
    """Return all mobile posts with resilient image handling.

    Production data currently includes some MobilePostImage rows whose FileField has no
    underlying file. Accessing .url on such rows raises ValueError. We defensively skip
    those so the endpoint always responds 200 with remaining valid images.
    """
    user = getattr(request, 'user', AnonymousUser())
    posts = MobilePost.objects.all().order_by('-created_at')
    data = []
    for post in posts:
        # First try Cloudinary URLs directly from DB (column may not be in model definition)
        cloud_urls = []
        try:
            with connection.cursor() as cur:
                cur.execute("""
                    SELECT cloudinary_url
                    FROM mobile_post_image
                    WHERE post_id = %s AND COALESCE(cloudinary_url,'') <> ''
                    ORDER BY id ASC
                """, [post.id])
                cloud_urls = [r[0] for r in cur.fetchall() if r[0]]
        except Exception:
            cloud_urls = []

        image_urls = cloud_urls
        if not image_urls:
            # Fallback to file-based images (legacy path)
            for img in post.images.all():
                f = getattr(img, 'image', None)
                if not f:
                    continue
                try:
                    if getattr(f, 'name', ''):
                        image_urls.append(f.url)
                except Exception:
                    continue
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

    # Detail view: prefer cloudinary_url list
    try:
        with connection.cursor() as cur:
            cur.execute("""
                SELECT cloudinary_url
                FROM mobile_post_image
                WHERE post_id = %s AND COALESCE(cloudinary_url,'') <> ''
                ORDER BY id ASC
            """, [post.id])
            image_urls = [r[0] for r in cur.fetchall() if r[0]]
    except Exception:
        image_urls = []

    if not image_urls:
        # Fallback to file-based storage if no cloudinary urls
        image_urls = []
        for img in post.images.all():
            f = getattr(img, 'image', None)
            if not f:
                continue
            try:
                if getattr(f, 'name', ''):
                    image_urls.append(f.url)
            except Exception:
                continue

    response = {
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'created_at': post.created_at.isoformat(),
        'images': image_urls,
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
    print(f"DEBUG: toggle_like called for post_id={post_id}")
    print(f"DEBUG: request.user = {request.user}")
    print(f"DEBUG: request.user.is_authenticated = {getattr(request.user, 'is_authenticated', 'No attr')}")
    print(f"DEBUG: request.META.get('HTTP_COOKIE') = {request.META.get('HTTP_COOKIE', 'No cookies')}")
    
    user = getattr(request, 'user', AnonymousUser())
    if not user.is_authenticated:
        print(f"DEBUG: User not authenticated, returning 401")
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        post = MobilePost.objects.get(id=post_id)
        print(f"DEBUG: Found post: {post.title}")
    except MobilePost.DoesNotExist:
        print(f"DEBUG: Post {post_id} not found")
        return JsonResponse({'error': 'Post not found'}, status=404)

    existing = Like.objects.filter(post=post, user=user).first()
    if existing:
        existing.delete()
        print(f"DEBUG: Unliked post {post_id} for user {user.username}")
        return JsonResponse({'message': 'Post unliked', 'liked': False}, status=200)
    else:
        Like.objects.create(post=post, user=user)
        print(f"DEBUG: Liked post {post_id} for user {user.username}")
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
