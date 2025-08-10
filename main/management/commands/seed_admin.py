from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with an initial admin user'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='admin').exists():
            user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                mobile='09123456789',
            )
            self.stdout.write(self.style.SUCCESS('✅ Admin user created!'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Admin user already exists.'))
