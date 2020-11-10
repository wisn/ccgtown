from django.core import serializers
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

import bcrypt

from .forms import LoginForm, RegisterForm
from .models import Account
from .utils import capitalize_form

def register(request):
    if request.session.get('user', None) != None:
        return HttpResponseRedirect(reverse('projects'))

    context = {
        'page': {
            'title': 'Register',
        },
    }

    if request.method == 'GET':
        return render(request, 'register.html', context)

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if not form.is_valid():
            for field, errors in form.errors.items():
                for error in errors:
                    msg = '%s: %s' % (capitalize_form(field), error)
                    messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse('register'))

        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirmation = request.POST.get('password_confirmation')

        if password != password_confirmation:
            msg = 'Password field and Password Confirmation field must be the same!'
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse('register'))

        # pylint: disable=no-member
        acc = Account.objects.filter(email = email)
        if len(acc) != 0:
            msg = '%s already registered.' % email
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse('register'))

        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('UTF-8'), salt)

        acc = Account()
        acc.email = email
        acc.password = hashed.decode('UTF-8')

        try:
            acc.save()
            msg = 'Account registered. You may now login.'
            messages.add_message(request, messages.INFO, msg)
            return HttpResponseRedirect(reverse('login'))
        except:
            msg = 'Can not register the account. Internal server error.'
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse('register'))


def login(request):
    if request.session.get('user', None) != None:
        return HttpResponseRedirect(reverse('projects'))

    context = {
        'page': {
            'title': 'Login',
        },
    }

    if request.method == 'GET':
        return render(request, 'login.html', context)

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if not form.is_valid():
            for field, errors in form.errors.items():
                for error in errors:
                    msg = '%s: %s' % (capitalize_form(field), error)
                    messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse('login'))

        email = request.POST.get('email')
        password = request.POST.get('password')
        msg = 'Email and/or password mismatched.'

        # pylint: disable=no-member
        acc = Account.objects.filter(email = email)
        if len(acc) == 0:
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse('login'))

        user = acc[0]
        if not bcrypt.checkpw(password.encode('UTF-8'), user.password.encode('UTF-8')):
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse('login'))

        msg = 'Welcome to CCGtown! Here is your project list.'
        messages.add_message(request, messages.INFO, msg)

        request.session['user'] = serializers.serialize('json', [user])[0]
        return HttpResponseRedirect(reverse('projects'))


def logout(request):
    try:
        del request.session['user']
    except:
        pass

    msg = 'You have logged out.'
    messages.add_message(request, messages.INFO, msg)
    return HttpResponseRedirect(reverse('login'))


def projects(request):
    if request.session.get('user', None) == None:
        msg = 'Please login before accessing Projects page.'
        messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect(reverse('login'))

    context = {
        'page': {
            'title': 'Projects',
            'description': 'List of your CCGtown projects.',
        },
    }
    return render(request, 'projects/index.html', context)
