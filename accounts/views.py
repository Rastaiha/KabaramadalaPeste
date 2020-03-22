from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.core.mail import send_mail, EmailMessage

from accounts.models import *
from accounts.forms import *

import json
import requests


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
    if request.method == 'POST' and check_bibot_response(request):
        form = SignUpForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.add_message(request, messages.ERROR, 'ایمیل تکراری')
            return render(request, 'auth/signup.html')
        member = Member.objects.create(
            first_name=request.POST['name'],
            username=request.POST['email'],  # TODO is it ok?
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
        email = EmailMessage(
            subject='ثبت‌نام در کابارآمادالاپسته',
            body='ثبت‌نام شما با موفقیت انجام شد.',
            from_email='Rastaiha <info@rastaiha.ir>',
            to=[member.email],
            headers={'Content-Type': 'text/plain'},
        )
        email.send()
        return redirect(reverse('homepage:homepage'))
    return render(request, 'auth/signup.html')
