from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import MobilePost, MobilePostImage
from ..forms import MobilePostForm
from .admin import admin_required
import os
from django.conf import settings
import uuid

# 🔧 Helper to save image with a predictable name
def save_image_with_custom_name(uploaded_file, post_id, index):
    ext = uploaded_file.name.split('.')[-1]
    filename = f"post_{post_id}_{uuid.uuid4().hex[:8]}_{index}.{ext}"
    path = os.path.join('mobile_posts', filename)

    full_path = os.path.join(settings.MEDIA_ROOT, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    return path

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

            for idx, img in enumerate(valid_images):
                path = save_image_with_custom_name(img, post.id, idx)
                MobilePostImage.objects.create(post=post, image=path)

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

            # Delete images user marked for removal
            for image in post.images.all():
                if f'remove_image_{image.id}' in request.POST:
                    # Also remove the actual file
                    if image.image and os.path.isfile(image.image.path):
                        os.remove(image.image.path)
                    image.delete()

            # Save new uploaded images
            for idx, img in enumerate(valid_images):
                path = save_image_with_custom_name(img, post.id, idx)
                MobilePostImage.objects.create(post=post, image=path)

            messages.success(request, "Mobile post updated.")
            return redirect('mobile_post_list')
    else:
        form = MobilePostForm(instance=post)

    return render(request, 'posts/mobile_post_form.html', {
        'form': form,
        'edit': True,
        'post': post,
    })


# ✅ Delete post (with media file deletion)
@login_required
@admin_required
def mobile_post_delete(request, post_id):
    post = get_object_or_404(MobilePost, id=post_id)

    # Delete associated image files
    for image in post.images.all():
        if image.image and os.path.isfile(image.image.path):
            os.remove(image.image.path)

    post.delete()
    messages.success(request, "Mobile post and images deleted.")
    return redirect('mobile_post_list')

# View a single mobile post (optional, can skip)
@login_required
@admin_required
def mobile_post_detail(request, post_id):
    post = get_object_or_404(MobilePost, id=post_id)
    comments = post.comments.select_related('user').order_by('-created_at')
    user = request.user
    is_owner = post.created_by == user  # Ensure MobilePost has `created_by`
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

