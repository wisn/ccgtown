from django.contrib import messages
from django.core import serializers
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

import bcrypt
import json
from nltk.tokenize import sent_tokenize, word_tokenize

from .models import Account, Project, Sentence
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
        acc = Account.objects.filter(email=email)
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
        prj.rules = ':- S, N, NP, VP'
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


def remove_project(request, project_uuid):
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
            msg = 'You are not allowed to remove the project.'
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse('projects'))

        try:
            prj.delete()
            msg = 'Project removed.'
            messages.add_message(request, messages.INFO, msg)
            return HttpResponseRedirect(reverse('projects'))
        except:
            msg = 'Can not remove project. Internal server error.'
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse('projects'))


def editor(request, project_uuid):
    user = request.session.get('user', None)
    if not user:
        msg = 'Please login before accessing Editor page.'
        messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect(reverse('login'))

    # pylint: disable=no-member
    prj = Project.objects.filter(uuid=project_uuid)
    if len(prj) == 0:
        msg = 'Project not found. Might be deleted.'
        messages.add_message(request, messages.ERROR, msg)
        return HttpResponseRedirect(reverse('projects'))

    prj = prj[0]
    sentences = Sentence.objects.filter(project=prj)
    snt_json = serializers.serialize('json', sentences)
    sentences = utils.reconstruct_sentences(sentences)

    if request.method == 'GET':
        context = {
            'page': {
                'title': prj.name,
            },
            'project': prj,
            'sentences': sentences,
            'snt_json': snt_json,
            'user': user,
        }
        return render(request, 'projects/editor.html', context)


def new_sentences(request, project_uuid):
    user = request.session.get('user', None)
    if not user:
        msg = 'Please login before accessing Editor page.'
        messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect(reverse('login'))

    if request.method == 'POST':
        # pylint: disable=no-member
        prj = Project.objects.filter(uuid=project_uuid)
        if len(prj) == 0:
            msg = 'Project not found. Might be deleted.'
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse('editor', args=(project_uuid,)))

        form = forms.NewSentencesForm(request.POST)
        if not form.is_valid():
            for field, errors in form.errors.items():
                for error in errors:
                    msg = '%s: %s' % (utils.capitalize_form(field), error)
                    messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse('editor', args=(project_uuid,)))

        prj = prj[0]
        count = 0

        sentences = request.POST.get('sentences')
        for tkn in sent_tokenize(sentences):
            words = word_tokenize(tkn)
            categories = [None] * len(words)
            try:
                snt = Sentence()
                snt.project = prj
                snt.words = words
                snt.categories = categories
                snt.derivations = []
                snt.save()
                count += 1
            except:
                pass

        try:
            prj.updated_at = timezone.now()
            prj.save()
        except:
            pass

        msg = 'Added %s new sentence(s).' % count
        messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect(reverse('editor', args=(project_uuid,)))


def add_changes(request, project_uuid):
    user = request.session.get('user', None)
    if not user:
        msg = 'Please login before accessing Editor page.'
        messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect(reverse('login'))

    if request.method == 'POST':
        changes = request.POST.get('changes')
        changes = json.loads(changes)

        msgs = []
        # pylint: disable=no-member
        project = Project.objects.get(uuid=project_uuid)
        c_prj = changes['project']
        c_snt = changes['sentences']

        if len(c_prj) > 0:
            project.updated_at = timezone.now()
            if 'name' in c_prj:
                project.name = c_prj['name']
            if 'status' in c_prj:
                project.status = c_prj['status']
            if 'rules' in c_prj:
                project.rules = c_prj['rules']
            try:
                project.save()
                msgs.append('Project updated.')
            except:
                msgs.append('Failed to update project.')

        if len(c_snt) > 0:
            count = 0
            for uuid in c_snt:
                # pylint: disable=no-member
                sentence = Sentence.objects.get(uuid=uuid)
                for index in c_snt[uuid]:
                    sentence.categories[int(index)] = c_snt[uuid][index]
                try:
                    sentence.updated_at = timezone.now()
                    sentence.save()
                    count += 1
                except:
                    pass

            if count > 0:
                msgs.append('Updated %s sentence(s).' % count)
                try:
                    project.updated_at = timezone.now()
                    project.save()
                except:
                    pass
            else:
                msgs.append('There is no sentence updated. Internal server error.')

        for msg in msgs:
            messages.add_message(request, messages.INFO, msg)

        return HttpResponseRedirect(reverse('editor', args=(project_uuid,)))


def remove_sentence(request, project_uuid, sentence_uuid):
    user = request.session.get('user', None)
    if not user:
        msg = 'Please login before accessing Editor page.'
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
            msg = 'You are not allowed to remove anything in this project.'
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse('projects'))

        # pylint: disable=no-member
        snt = Sentence.objects.filter(uuid=sentence_uuid)
        if len(snt) == 0:
            msg = 'Sentence does not exists.'
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse('editor', args=(project_uuid,)))

        snt = snt[0]
        try:
            snt.delete()
            msg = 'Sentence removed.'
            messages.add_message(request, messages.INFO, msg)
            prj.updated_at = timezone.now()
            prj.save()
            return HttpResponseRedirect(reverse('editor', args=(project_uuid,)))
        except:
            msg = 'Unable to remove sentence. Internal server error.'
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse('editor', args=(project_uuid,)))

