from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

import bcrypt

from .models import Account, Project
import annotators.forms as forms
import annotators.utils as utils

def register(request):
    if request.session.get('user', None) != None:
        return HttpResponseRedirect(reverse('projects'))

    if request.method == 'GET':
        context = {
            'page': {
                'title': 'Register',
            },
        }
        return render(request, 'register.html', context)

    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        if not form.is_valid():
            for field, errors in form.errors.items():
                for error in errors:
                    msg = '%s: %s' % (utils.capitalize_form(field), error)
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

    if request.method == 'GET':
        context = {
            'page': {
                'title': 'Login',
            },
        }
        return render(request, 'login.html', context)

    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if not form.is_valid():
            for field, errors in form.errors.items():
                for error in errors:
                    msg = '%s: %s' % (utils.capitalize_form(field), error)
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

        fields = ('id', 'uuid', 'email', 'is_verified')
        json = utils.serialize_json([user], fields=fields)
        request.session['user'] = json[0]

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
    user = request.session.get('user', None)
    if not user:
        msg = 'Please login before accessing Projects page.'
        messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect(reverse('login'))

    if request.method == 'GET':
        # pylint: disable=no-member
        projects = Project.objects.filter(author=user['id'])
        context = {
            'page': {
                'title': 'Projects',
                'description': 'List of your CCGtown projects.',
            },
            'projects': projects,
            'user': user,
        }
        return render(request, 'projects/index.html', context)

    if request.method == 'POST':
        form = forms.CreateProjectForm(request.POST)
        if not form.is_valid():
            for field, errors in form.errors.items():
                for error in errors:
                    msg = '%s: %s' % (utils.capitalize_form(field), error)
                    messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse('projects'))

        prj = Project()
        prj.name = request.POST.get('project_name')
        # pylint: disable=no-member
        prj.author = Account.objects.get(id=user['id'])

        try:
            prj.save()
            msg = 'Project created.'
            messages.add_message(request, messages.INFO, msg)
            return HttpResponseRedirect(reverse('projects'))
        except:
            msg = 'Project creation failure. Internal server error'
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse('projects'))


def delete_project(request, project_uuid):
    user = request.session.get('user', None)
    if not user:
        msg = 'Please login before accessing Projects page.'
        messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect(reverse('login'))

    if request.method == 'POST':
        # pylint: disable=no-member
        prj = Project.objects.filter(uuid=project_uuid)
        if len(prj) == 0:
            msg = 'Project does not exists.'
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse('projects'))

        # pylint: disable=no-member
        acc = Account.objects.get(uuid=user['uuid'])
        prj = prj[0]
        if acc.uuid != prj.author.uuid:
            msg = 'You are not allowed to delete the project.'
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse('projects'))

        try:
            prj.delete()
            msg = 'Project deleted.'
            messages.add_message(request, messages.INFO, msg)
            return HttpResponseRedirect(reverse('projects'))
        except:
            msg = 'Can not delete project. Internal server error.'
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse('projects'))


def editor(request, project_uuid):
    user = request.session.get('user', None)
    if not user:
        msg = 'Please login before accessing Editor page.'
        messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect(reverse('login'))

    prj = Project.objects.filter(uuid=project_uuid)
    if len(prj) == 0:
        msg = 'Project not found. Might be deleted.'
        messages.add_message(request, messages.ERROR, msg)
        return HttpResponseRedirect(reverse('projects'))

    prj = prj[0]
    if request.method == 'GET':
        context = {
            'page': {
                'title': prj.name,
            },
            'project': prj,
            'user': user,
        }
        return render(request, 'projects/editor.html', context)

