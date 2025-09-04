#!/usr/bin/env python
"""
Test script to verify the validation fixes for registration and profile editing.
Run this script from the Django project root directory.
"""

import os
import sys
import django
from django.conf import settings

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from main.forms import UserRegistrationForm, UserProfileEditForm
from django.contrib.auth import get_user_model

User = get_user_model()

def test_mobile_validation():
    """Test mobile number validation"""
    print("Testing mobile number validation...")
    
    # Test valid mobile number
    valid_form = UserRegistrationForm({
        'first_name': 'John',
        'last_name': 'Doe',
        'username': 'testuser1',
        'email': 'test1@example.com',
        'password': 'TestPass123',
        'mobile': '09123456789'
    })
    
    print(f"Valid mobile (09123456789): {valid_form.is_valid()}")
    if not valid_form.is_valid():
        print(f"Errors: {valid_form.errors}")
    
    # Test invalid mobile number (letters)
    invalid_form1 = UserRegistrationForm({
        'first_name': 'John',
        'last_name': 'Doe',
        'username': 'testuser2',
        'email': 'test2@example.com',
        'password': 'TestPass123',
        'mobile': '0912345abcd'
    })
    
    print(f"Invalid mobile (0912345abcd): {invalid_form1.is_valid()}")
    if not invalid_form1.is_valid():
        print(f"Errors: {invalid_form1.errors.get('mobile', [])}")
    
    # Test invalid mobile number (wrong length)
    invalid_form2 = UserRegistrationForm({
        'first_name': 'John',
        'last_name': 'Doe',
        'username': 'testuser3',
        'email': 'test3@example.com',
        'password': 'TestPass123',
        'mobile': '091234567'  # Too short
    })
    
    print(f"Invalid mobile (091234567): {invalid_form2.is_valid()}")
    if not invalid_form2.is_valid():
        print(f"Errors: {invalid_form2.errors.get('mobile', [])}")
    
    # Test invalid mobile number (doesn't start with 09)
    invalid_form3 = UserRegistrationForm({
        'first_name': 'John',
        'last_name': 'Doe',
        'username': 'testuser4',
        'email': 'test4@example.com',
        'password': 'TestPass123',
        'mobile': '08123456789'
    })
    
    print(f"Invalid mobile (08123456789): {invalid_form3.is_valid()}")
    if not invalid_form3.is_valid():
        print(f"Errors: {invalid_form3.errors.get('mobile', [])}")

def test_email_validation():
    """Test email validation"""
    print("\nTesting email validation...")
    
    # Test valid email
    valid_form = UserRegistrationForm({
        'first_name': 'John',
        'last_name': 'Doe',
        'username': 'testuser5',
        'email': 'valid@example.com',
        'password': 'TestPass123',
    })
    
    print(f"Valid email (valid@example.com): {valid_form.is_valid()}")
    if not valid_form.is_valid():
        print(f"Errors: {valid_form.errors}")
    
    # Test invalid email
    invalid_form = UserRegistrationForm({
        'first_name': 'John',
        'last_name': 'Doe',
        'username': 'testuser6',
        'email': 'invalid-email',
        'password': 'TestPass123',
    })
    
    print(f"Invalid email (invalid-email): {invalid_form.is_valid()}")
    if not invalid_form.is_valid():
        print(f"Errors: {invalid_form.errors.get('email', [])}")

def test_password_validation():
    """Test password strength validation"""
    print("\nTesting password strength validation...")
    
    # Test valid strong password
    valid_form = UserRegistrationForm({
        'first_name': 'John',
        'last_name': 'Doe',
        'username': 'testuser7',
        'email': 'test7@example.com',
        'password': 'StrongPass123',
    })
    
    print(f"Valid strong password (StrongPass123): {valid_form.is_valid()}")
    if not valid_form.is_valid():
        print(f"Errors: {valid_form.errors}")
    
    # Test weak password (too short)
    weak_form1 = UserRegistrationForm({
        'first_name': 'John',
        'last_name': 'Doe',
        'username': 'testuser8',
        'email': 'test8@example.com',
        'password': 'weak',
    })
    
    print(f"Weak password (weak): {weak_form1.is_valid()}")
    if not weak_form1.is_valid():
        print(f"Errors: {weak_form1.errors.get('password', [])}")
    
    # Test password without numbers
    weak_form2 = UserRegistrationForm({
        'first_name': 'John',
        'last_name': 'Doe',
        'username': 'testuser9',
        'email': 'test9@example.com',
        'password': 'NoNumbers',
    })
    
    print(f"Password without numbers (NoNumbers): {weak_form2.is_valid()}")
    if not weak_form2.is_valid():
        print(f"Errors: {weak_form2.errors.get('password', [])}")
    
    # Test password without uppercase
    weak_form3 = UserRegistrationForm({
        'first_name': 'John',
        'last_name': 'Doe',
        'username': 'testuser10',
        'email': 'test10@example.com',
        'password': 'nouppercase123',
    })
    
    print(f"Password without uppercase (nouppercase123): {weak_form3.is_valid()}")
    if not weak_form3.is_valid():
        print(f"Errors: {weak_form3.errors.get('password', [])}")
    
    # Test password without lowercase
    weak_form4 = UserRegistrationForm({
        'first_name': 'John',
        'last_name': 'Doe',
        'username': 'testuser11',
        'email': 'test11@example.com',
        'password': 'NOLOWERCASE123',
    })
    
    print(f"Password without lowercase (NOLOWERCASE123): {weak_form4.is_valid()}")
    if not weak_form4.is_valid():
        print(f"Errors: {weak_form4.errors.get('password', [])}")

def test_profile_edit_validation():
    """Test profile editing validation"""
    print("\nTesting profile editing validation...")
    
    # Create a test user first
    test_user, created = User.objects.get_or_create(
        username='profiletest',
        defaults={
            'email': 'profiletest@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    # Test valid profile update
    valid_form = UserProfileEditForm({
        'first_name': 'Updated',
        'last_name': 'Name',
        'email': 'updated@example.com',
        'mobile': '09987654321'
    }, user_instance=test_user)
    
    print(f"Valid profile update: {valid_form.is_valid()}")
    if not valid_form.is_valid():
        print(f"Errors: {valid_form.errors}")
    
    # Test invalid mobile in profile update
    invalid_form = UserProfileEditForm({
        'first_name': 'Updated',
        'last_name': 'Name',
        'email': 'updated2@example.com',
        'mobile': 'invalid123'
    }, user_instance=test_user)
    
    print(f"Invalid mobile in profile update: {invalid_form.is_valid()}")
    if not invalid_form.is_valid():
        print(f"Errors: {invalid_form.errors.get('mobile', [])}")
    
    # Clean up
    if created:
        test_user.delete()

if __name__ == "__main__":
    print("=== Testing Validation Fixes ===")
    test_mobile_validation()
    test_email_validation()
    test_password_validation()
    test_profile_edit_validation()
    print("\n=== Testing Complete ===")
