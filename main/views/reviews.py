from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .auth import admin_required
from ..models import Review

@admin_required
def bookmark_count(request):
    """Get current number of bookmarked reviews"""
    count = Review.objects.filter(is_bookmarked=True).count()
    return JsonResponse({'count': count})

@admin_required
def review_list(request):
    """List all reviews for admin management"""
    reviews = Review.objects.all()
    return render(request, 'custom_admin/review_list.html', {'reviews': reviews})

@admin_required
def review_detail(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return JSON response for AJAX requests
        data = {
            'id': review.id,
            'user': review.user.get_full_name() or review.user.username,
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'is_approved': review.is_approved,
            'is_bookmarked': review.is_bookmarked,
            'images': review.get_images()
        }
        return JsonResponse(data)
    return render(request, 'custom_admin/review_detail.html', {'review': review})

@admin_required
def review_bookmark_toggle(request, review_id):
    """Toggle bookmark status of a review"""
    if request.method == 'POST':
        review = get_object_or_404(Review, id=review_id)
        
        # Check if we're trying to bookmark and already have 10 bookmarked
        if not review.is_bookmarked:
            current_bookmarked_count = Review.objects.filter(is_bookmarked=True).count()
            if current_bookmarked_count >= 10:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'Maximum of 10 reviews can be bookmarked for the homepage'
                    })
                messages.error(request, 'Maximum of 10 reviews can be bookmarked for the homepage.')
                return redirect('review_list')
        
        review.is_bookmarked = not review.is_bookmarked
        review.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'is_bookmarked': review.is_bookmarked,
                'message': 'Bookmarked' if review.is_bookmarked else 'Bookmark removed'
            })
        
        action = 'bookmarked' if review.is_bookmarked else 'removed from bookmarks'
        messages.success(request, f'Review {action} successfully.')
        return redirect('review_list')
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@admin_required
def review_approve(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.is_approved = True
    review.save()
    messages.success(request, 'Review approved successfully.')
    return redirect('review_list')

@admin_required
def review_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review deleted successfully.')
        return redirect('review_list')
    return render(request, 'custom_admin/review_confirm_delete.html', {'review': review})