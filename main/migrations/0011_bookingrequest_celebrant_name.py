# Added celebrant_name field to BookingRequest
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_mobilereview_mobilereviewimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingrequest',
            name='celebrant_name',
            field=models.CharField(max_length=150, blank=True, null=True),
        ),
    ]
