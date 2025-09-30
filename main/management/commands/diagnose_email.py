"""
Django management command to diagnose email issues in production
"""
from django.core.management.base import BaseCommand
from main.utils.email_debug import comprehensive_email_diagnosis, get_render_optimized_email_settings


class Command(BaseCommand):
    help = 'Diagnose email configuration and connectivity issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-send',
            type=str,
            help='Send a test email to the specified address',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting email diagnosis...'))
        
        try:
            # Run comprehensive diagnosis
            success = comprehensive_email_diagnosis()
            
            if success:
                self.stdout.write(self.style.SUCCESS('✓ Email diagnosis completed successfully!'))
            else:
                self.stdout.write(self.style.ERROR('❌ Email diagnosis found issues'))
                
                # Show recommended settings
                self.stdout.write('\n' + '='*50)
                self.stdout.write(self.style.WARNING('RECOMMENDED SETTINGS FOR RENDER:'))
                recommended = get_render_optimized_email_settings()
                for key, value in recommended.items():
                    if 'PASSWORD' in key:
                        value = '*' * len(str(value)) if value else 'NOT SET'
                    self.stdout.write(f'{key}: {value}')
            
            # Send test email if requested
            if options['test_send']:
                from main.utils.email_debug import send_test_email
                test_success, test_message = send_test_email(options['test_send'])
                if test_success:
                    self.stdout.write(self.style.SUCCESS(f'✓ {test_message}'))
                else:
                    self.stdout.write(self.style.ERROR(f'❌ {test_message}'))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Diagnosis failed: {e}'))