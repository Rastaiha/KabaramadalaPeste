from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required

from accounts.models import *
from accounts.forms import *

import json
import requests
import random


def check_bibot_response(request):
    if request.POST.get('bibot-response') is not None:
        if request.POST.get('bibot-response') != '':
            r = requests.post('https://api.bibot.ir/api1/siteverify/', data={
                'secretkey': '9270bf6cd4a087673ca9e86666977a30',
                'response': request.POST['bibot-response']
            })
            if r.json()['success']:
                return True
            else:
                messages.error(request, 'کپچا به درستی حل نشده است!')
                return False
        else:
            messages.error(request, 'کپچا به درستی حل نشده است!')
            return False
    return False


def signup(request):
    # if request.user.is_authenticated:
    #     raise Http404
    if request.method == 'POST' and check_bibot_response(request):
        form = SignUpForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.add_message(request, messages.ERROR, 'ایمیل تکراری')
            return render(request, 'auth/signup.html')

        file = open('animals.txt', 'r', encoding='UTF-8')
        animals = file.read().strip().split('\n')
        file.close()
        file = open('adjectives.txt', 'r', encoding='UTF-8')
        adjectives = file.read().strip().split('\n')
        file.close()

        username = random.choice(animals) + ' ' + random.choice(adjectives)
        while Member.objects.filter(username__exact=username).count() > 0:
            username = random.choice(animals) + ' ' + random.choice(adjectives)

        member = Member.objects.create(
            first_name=request.POST['name'],
            username=username,
            email=request.POST['email']
        )
        member.set_password(request.POST['password'])
        participant = Participant.objects.create(
            member=member,
            gender=request.POST['gender'],
            city=request.POST['city'],
            school=request.POST['school'],
            phone_number=request.POST['phone'],
            document=form.cleaned_data['document']
        )
        member.save()
        participant.save()
        # send_mail('ثبت‌نام در کابارآمادالاپسته', 'ثبت‌نام شما با موفقیت انجام شد.', 'info@rastaiha.ir', [member.email])
        # email = EmailMessage(
        #     subject='ثبت‌نام در کابارآمادالاپسته',
        #     body='ثبت‌نام شما با موفقیت انجام شد.',
        #     from_email='Rastaiha <info@rastaiha.ir>',
        #     to=[member.email],
        #     headers={'Content-Type': 'text/plain'},
        # )
        # email.send()
        html_content = render_to_string('auth/signup_confirm_mail.html', {'user': member})
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives('تایید ثبت‌نام اولیه', text_content, 'Rastaiha <info@rastaiha.ir>', [member.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return redirect(reverse('homepage:homepage'))
    return render(request, 'auth/signup.html')


def login(request):
    if request.user.is_authenticated:
        raise Http404
    if request.method == "POST":
        print(request.POST)
        if not check_bibot_response(request):
            return render(request, 'auth/login.html')
        members = Member.objects.filter(email__exact=request.POST.get('email'))
        if members.count() == 0:
            messages.error(request, 'ایمیل یا رمز عبور غلط است.')
            return render(request, 'auth/login.html')
        member = members[0]
        username = member.username
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('homepage:homepage')
        else:
            messages.error(request, 'ایمیل یا رمز عبور غلط است.')
            return render(request, 'auth/login.html')
    return render(request, 'auth/login.html')


@login_required
def logout(request):
    auth_logout(request)
    return redirect('homepage:homepage')
