import os
import hmac
import hashlib
import json
import re
import random
import string
import html

from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from .models import User, Customer
from django.db import IntegrityError


login_attempts = {}

def load_password_config():
    with open('config.json') as config_file:
        return json.load(config_file)

def home(request):
    return render(request, 'mainapp/home.html')

def is_password_valid(password):
    config = load_password_config()

    if len(password) < config['password_min_length']:
        return False, f"Password must be at least {config['password_min_length']} characters long."

    if config['require_uppercase'] and not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."

    if config['require_lowercase'] and not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."

    if config['require_numbers'] and not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number."

    if config['require_special'] and not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
        return False, "Password must contain at least one special character."

    for word in config['forbidden_words']:
        if word.lower() in password.lower():
            return False, f"Password cannot contain forbidden words like '{word}'."

    return True, ""

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        confirm_password = request.POST.get('password2')

        if password != confirm_password:
            return render(request, 'mainapp/register.html', {'error': 'Passwords do not match'})

        is_valid, error_message = is_password_valid(password)
        if not is_valid:
            return render(request, 'mainapp/register.html', {'error': error_message})

        if User.objects.filter(username=username).exists():
            return render(request, 'mainapp/register.html', {'error': 'Username already exists'})

        salt = os.urandom(16)
        password_hash = hmac.new(salt, password.encode(), hashlib.sha256).hexdigest()

        User.objects.create(
            username=username,
            email=email,
            salt=salt,
            password_hash=password_hash,
            previous_password_hash1="",
            previous_password_hash2="",
            previous_password_hash3=""
        )

        return redirect('login')

    return render(request, 'mainapp/register.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        now = timezone.now()

        if username in login_attempts:
            attempts, lock_until = login_attempts[username]
            if lock_until and now < lock_until:
                return render(request, 'mainapp/login.html', {'error': 'Account locked. Try again later.'})

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return render(request, 'mainapp/login.html', {'error': 'Invalid username or password.'})

        new_hash = hmac.new(user.salt, password.encode(), hashlib.sha256).hexdigest()

        if new_hash == user.password_hash:
            login_attempts.pop(username, None)
            return render(request, 'mainapp/system.html', {'username': html.escape(username)})
        else:
            attempts, lock_until = login_attempts.get(username, (0, None))
            attempts += 1
            if attempts >= 3:
                lock_until = now + timedelta(minutes=30)
            login_attempts[username] = (attempts, lock_until)
            return render(request, 'mainapp/login.html', {'error': 'Invalid username or password.'})

    return render(request, 'mainapp/login.html')

def add_customer(request):
    if request.method == 'POST':
        first_name = html.escape(request.POST.get('first_name'))
        last_name = html.escape(request.POST.get('last_name'))
        id_number = html.escape(request.POST.get('id_number'))

        customer = Customer.objects.create(
            first_name=first_name,
            last_name=last_name,
            id_number=id_number
        )

        return render(request, 'mainapp/system.html', {'new_customer': customer})

    return render(request, 'mainapp/add_customer.html')

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'mainapp/customer_list.html', {'customers': customers})

def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return render(request, 'mainapp/forgot_password.html', {'error': 'Username not found.'})

        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        sha1 = hashlib.sha1(random_string.encode()).hexdigest()

        request.session['reset_code'] = sha1
        request.session['reset_username'] = username

        send_mail(
            'Communication Ltd - Reset Password Code',
            f'Your reset code is: {sha1}',
            'hitltdproject@gmail.com',
            [user.email],
            fail_silently=False,
        )

        return redirect('verify_reset_code')  # ✅ שינוי → מעביר ישר למסך הקוד

    return render(request, 'mainapp/forgot_password.html')

def verify_reset_code(request):
    if request.method == 'POST':
        entered_code = request.POST.get('reset_code')
        saved_code = request.session.get('reset_code')

        if entered_code == saved_code:
            return redirect('reset_password')
        else:
            return render(request, 'mainapp/verify_reset_code.html', {'error': 'Invalid reset code.'})

    return render(request, 'mainapp/verify_reset_code.html')

def reset_password(request):
    if request.method == 'POST':
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        username = request.session.get('reset_username')

        if new_password1 != new_password2:
            return render(request, 'mainapp/reset_password.html', {'error': 'Passwords do not match.'})

        is_valid, error_message = is_password_valid(new_password1)
        if not is_valid:
            return render(request, 'mainapp/reset_password.html', {'error': error_message})

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return render(request, 'mainapp/reset_password.html', {'error': 'User not found.'})

        new_password_hash_check = hmac.new(user.salt, new_password1.encode(), hashlib.sha256).hexdigest()
        previous_hashes = [user.password_hash, user.previous_password_hash1, user.previous_password_hash2, user.previous_password_hash3]
        if new_password_hash_check in previous_hashes:
            return render(request, 'mainapp/reset_password.html', {'error': 'New password must be different from the last 3 passwords.'})

        user.previous_password_hash3 = user.previous_password_hash2
        user.previous_password_hash2 = user.previous_password_hash1
        user.previous_password_hash1 = user.password_hash

        new_salt = os.urandom(16)
        new_password_hash = hmac.new(new_salt, new_password1.encode(), hashlib.sha256).hexdigest()

        user.salt = new_salt
        user.password_hash = new_password_hash
        user.save()

        return redirect('login')

    return render(request, 'mainapp/reset_password.html')
