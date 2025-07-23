from django.shortcuts import render
from .auth import login_required
from django.shortcuts import render, get_object_or_404
from ..models import BookingRequest, EventStatusLog, EventStatusAttachment
import json
from django.shortcuts import get_object_or_404

@login_required
def event_status(request, id):
    booking = get_object_or_404(BookingRequest, id=id)

    steps_def = [
        ('CREATED', 'Booking received and is created'),
        ('PAYMENT', 'Payment status update'),
        ('BACKDROP', 'Backdrop has been set up'),
        ('CATERING', 'Catering/buffet in progress'),
        ('LOGISTICS', 'Lights/sound/logistics update'),
    ]

    status_logs = {
        log.label: log for log in EventStatusLog.objects.filter(booking=booking)
    }

    attachments = {}
    for a in EventStatusAttachment.objects.filter(booking=booking):
        attachments.setdefault(a.status_log.label, []).append(a.file.url)

    step_objs = []
    step_json = []

    for label, description in steps_def:
        log = status_logs.get(label)
        is_done = log and log.status == EventStatusLog.Status.DONE
        img_urls = attachments.get(label, [])

        if img_urls:
            html = f'<p>{description}</p>'
            for url in img_urls:
                html += f'<img src="{url}" class="proof-thumb" alt="Proof image">'
        elif is_done:
            html = f'<p>{description}</p><p><em>No image uploaded.</em></p>'
        else:
            html = f'<div class="placeholder">Not yet completed.</div>'

        step_objs.append({
            'label': label,
            'get_label_display': label.title().replace('_', ' '),
            'description': description,
            'is_done': is_done,
        })

        step_json.append({
            'label': label,
            'title': label.title().replace('_', ' '),
            'html': html,
            'uploadable': False,
            'is_done': is_done,
        })

    return render(request, 'event_status.html', {
        'booking': booking,
        'status_steps': step_objs,
        'step_content_json': json.dumps(step_json),
    })