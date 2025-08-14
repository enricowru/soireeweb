# Generated manually for MobileReview and MobileReviewImage models
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_alter_eventstatusattachment_unique_together_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MobileReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=150, null=True)),
                ('rating', models.PositiveSmallIntegerField(default=5)),
                ('comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'mobile_review',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='MobileReviewImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='mobile_reviews/')),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='main.mobilereview')),
            ],
            options={
                'db_table': 'mobile_review_image',
            },
        ),
    ]
