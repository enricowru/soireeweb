from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import default_storage
from ..models import MobilePost, MobilePostImage
from ..forms import MobilePostForm
from .admin import admin_required
from django.core.files.storage import default_storage
import cloudinary.uploader
from django.conf import settings
import uuid
from django.core.files.storage import default_storage
from decouple import config

# cloudinary.config( 
#     cloud_name = config('CLOUDINARY_CLOUD_NAME'), 
#     api_key = config('CLOUDINARY_API_KEY'), 
#     api_secret = config('CLOUDINARY_API_SECRET'), # Click 'View API Keys' above to copy your API secret
#     secure=True
# )

def save_image_with_custom_name(uploaded_file, post_id, index):
    """
    Returns a dict with either local 'image' (dev) or 'cloudinary_url' (prod).
    """
   

    ext = uploaded_file.name.split('.')[-1]
    filename = f"post_{post_id}_{uuid.uuid4().hex[:8]}_{index}.{ext}"

    if settings.ENVIRONMENT == "prod":
        # Cloudinary upload
        public_id = f"mobile_posts/{filename}"
        upload_result = cloudinary.uploader.upload(uploaded_file, public_id=public_id)
        return {"cloudinary_url": upload_result["secure_url"]}
    else:
        # Local dev
        path = f"mobile_posts/{filename}"
        saved_path = default_storage.save(path, uploaded_file)
        return {"image": saved_path}


# ✅ List posts
@login_required
@admin_required
def mobile_post_list(request):
    posts = MobilePost.objects.all().order_by('-created_at')
    return render(request, 'posts/mobile_posts_list.html', {'posts': posts})


# ✅ Create post
@login_required
@admin_required
def mobile_post_create(request):
    if request.method == 'POST':
        form = MobilePostForm(request.POST)
        images = request.FILES.getlist('images')
        valid_images = [img for img in images if img.content_type.startswith('image/')]
        if not valid_images:
            form.add_error(None, "Please upload at least one valid image file.")

        if form.is_valid():
            post = form.save(commit=False)
            post.created_by = request.user
            post.save()

            for idx, img in enumerate(valid_images, start=1):
                result = save_image_with_custom_name(img, post.id, idx)
                MobilePostImage.objects.create(
                    post=post,
                    **result  # safe: result is either {"image": ...} or {"cloudinary_public_id": ...}
                )

            messages.success(request, "Mobile post created successfully.")
            return redirect('mobile_post_list')
    else:
        form = MobilePostForm()

    return render(request, 'posts/mobile_post_form.html', {'form': form})

# ✅ Edit post
@login_required
@admin_required
def mobile_post_edit(request, post_id):
    post = get_object_or_404(MobilePost, id=post_id)

    if request.method == 'POST':
        form = MobilePostForm(request.POST, instance=post)
        images = request.FILES.getlist('images')
        valid_images = [img for img in images if img.content_type.startswith('image/')]

        if form.is_valid():
            form.save()

            # Delete images marked for removal
            remove_image_ids = request.POST.getlist('remove_images[]')
            for image in post.images.filter(id__in=remove_image_ids):
                if image.image:
                    image.image.delete(save=False)
                if settings.ENVIRONMENT == "prod" and image.cloudinary_url:
                    try:
                        public_id = image.cloudinary_url.split('/')[-1].split('.')[0]
                        cloudinary.uploader.destroy(public_id)
                    except Exception:
                        pass  # Continue even if Cloudinary deletion fails
                image.delete()

            # Save new uploaded images
            for idx, img in enumerate(valid_images, start=1):
                result = save_image_with_custom_name(img, post.id, idx)
                MobilePostImage.objects.create(post=post, **result)


            messages.success(request, "Mobile post updated.")
            return redirect('mobile_post_list')
    else:
        form = MobilePostForm(instance=post)

    return render(request, 'posts/mobile_post_form.html', {
        'form': form,
        'edit': True,
        'post': post,
    })


# ✅ Delete post
@login_required
@admin_required
def mobile_post_delete(request, post_id):
    post = get_object_or_404(MobilePost, id=post_id)

    for image in post.images.all():
        if image.image:
            image.image.delete(save=False)
        image.delete()

    post.delete()
    messages.success(request, "Mobile post and images deleted.")
    return redirect('mobile_post_list')


# ✅ Post detail
@login_required
@admin_required
def mobile_post_detail(request, post_id):
    post = get_object_or_404(MobilePost, id=post_id)
    comments = post.comments.select_related('user').order_by('-created_at')
    user = request.user
    is_owner = post.created_by == user
    is_liked = post.likes.filter(user=user).exists()
    like_count = post.likes.count()

    if request.method == 'POST' and 'toggle_like' in request.POST and not is_owner:
        like, created = post.likes.get_or_create(user=user)
        if not created:
            like.delete()
        return redirect('mobile_post_detail', post_id=post_id)

    return render(request, 'posts/mobile_post_details.html', {
        'post': post,
        'comments': comments,
        'is_liked': is_liked,
        'like_count': like_count,
        'is_owner': is_owner,
    })
