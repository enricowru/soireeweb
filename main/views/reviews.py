from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .auth import admin_required
from ..models import Review

@admin_required
def review_list(request):
    reviews = Review.objects.all()
    return render(request, 'custom_admin/review_list.html', {'reviews': reviews})

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