"""
Django management command to test email configuration
Usage: python manage.py test_email [email_address]
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from main.utils.email_debug import test_email_configuration, send_test_email, diagnose_email_password


class Command(BaseCommand):
    help = 'Test email configuration and send test email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            help='Email address to send test email to',
        )
        parser.add_argument(
            '--diagnose',
            action='store_true',
            help='Run email configuration diagnosis',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting email configuration test...')
        )
        
        # Run diagnosis if requested
        if options['diagnose']:
            self.stdout.write("\n" + "="*50)
            self.stdout.write("RUNNING EMAIL DIAGNOSIS")
            self.stdout.write("="*50)
            diagnose_email_password()
        
        # Test email configuration
        self.stdout.write("\n" + "="*50)
        self.stdout.write("TESTING EMAIL CONFIGURATION")
        self.stdout.write("="*50)
        
        success, message = test_email_configuration()
        
        if success:
            self.stdout.write(
                self.style.SUCCESS(f'✓ {message}')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'✗ {message}')
            )
            return
        
        # Send test email if address provided
        if options['to']:
            self.stdout.write("\n" + "="*50)
            self.stdout.write(f"SENDING TEST EMAIL TO {options['to']}")
            self.stdout.write("="*50)
            
            success, message = send_test_email(options['to'])
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {message}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ {message}')
                )
        else:
            self.stdout.write(
                self.style.WARNING('Use --to=email@example.com to send a test email')
            )
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write("EMAIL TEST COMPLETED")
        self.stdout.write("="*50)