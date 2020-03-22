from django.shortcuts import render
from django.http import JsonResponse, Http404, HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.template.loader import render_to_string
from django.utils.html import strip_tags, strip_spaces_between_tags
from django.contrib.auth.decorators import login_required
from django.conf import settings

from accounts.models import *
from accounts.forms import *

from zeep import Client

import requests
import re
import random
import datetime


MERCHANT = '8b469980-683d-11ea-806a-000c295eb8fc'
payment_amount = int(settings.REGISTRATION_FEE)
client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')


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
    if request.user.is_authenticated:
        raise Http404
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

        html_content = strip_spaces_between_tags(render_to_string('auth/signup_email.html', {'user': member}))
        text_content = re.sub('<style[^<]+?</style>', '', html_content)
        text_content = strip_tags(text_content)

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


def _redirect_homepage_with_payment_status(status):
    response = redirect(reverse('homepage:homepage'))
    response['Location'] += '?payment=%s' % status
    return response


def verify(request):
    if request.GET.get('Status') == 'OK':
        result = client.service.PaymentVerification(MERCHANT, request.GET['Authority'], payment_amount)
        payment_attempt = PaymentAttempt.objects.get(
            participant__member__email__exact=request.user.email,
            authority__exact=request.GET['Authority']
        )
        payment_attempt.verify_datetime = datetime.datetime.now()
        if result.Status == 100:
            request.user.participant.is_activated = True
            request.user.participant.save()
            html_content = render_to_string('auth/payment_success.html',
                                            {'user': request.user, 'refid': result.RefID})
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives('تایید پرداخت', text_content,
                                         'Rastaiha <info@rastaiha.ir>', [request.user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            payment_attempt.red_id = str(result.RefID)
            payment_attempt.desc = 'Transaction success.'
            payment_attempt.save()
            return _redirect_homepage_with_payment_status(settings.OK_STATUS)
            # return HttpResponse('Transaction success.\nRefID: ' + str(result.RefID))
        elif result.Status == 101:
            request.user.participant.is_activated = True
            request.user.participant.save()
            html_content = render_to_string('auth/payment_success.html',
                                            {'user': request.user})
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives('تایید پرداخت', text_content,
                                         'Rastaiha <info@rastaiha.ir>', [request.user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            payment_attempt.status = str(result.Status)
            payment_attempt.desc = 'Transaction submitted.'
            payment_attempt.save()
            return _redirect_homepage_with_payment_status(settings.OK_STATUS)
            # return HttpResponse('Transaction submitted : ' + str(result.Status))
        else:
            payment_attempt.status = str(result.Status)
            payment_attempt.desc = 'Transaction failed.'
            payment_attempt.save()
            return _redirect_homepage_with_payment_status(settings.ERROR_STATUS)
            # return HttpResponse('Transaction failed.\nStatus: ' + str(result.Status))
    else:
        return _redirect_homepage_with_payment_status(settings.ERROR_STATUS)
        # return HttpResponse('Transaction failed or canceled by user')


@login_required
def send_request(request):
    if not request.user.is_participant:
        raise Http404
    if request.user.participant.is_activated:
        raise Http404
    callback_url = request.build_absolute_uri(reverse('accounts:verify'))
    result = client.service.PaymentRequest(
        MERCHANT,
        payment_amount,
        'ثبت‌نام در رویداد «در جست‌وجوی کابارآمادالاپسته»',
        CallbackURL=callback_url
    )
    payment_attempt = PaymentAttempt.objects.create(
        request_datetime=datetime.datetime.now(),
        desc='Transaction failed or canceled by user.',
        participant=request.user.participant,
        authority=str(result.Authority)
    )
    payment_attempt.save()
    if result.Status == 100:
        return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority))
    else:
        return HttpResponse('Error code: ' + str(result.Status))
