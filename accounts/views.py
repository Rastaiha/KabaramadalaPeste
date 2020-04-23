from django.shortcuts import render
from django.http import JsonResponse, Http404, HttpResponse
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.template.loader import render_to_string
from django.utils.html import strip_tags, strip_spaces_between_tags
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text

from accounts.tokens import account_activation_token
from accounts.models import *
from accounts.forms import *

from homepage.models import *

from zeep import Client

import requests
import re
import random
import datetime


MERCHANT = '8b469980-683d-11ea-806a-000c295eb8fc'
payment_amount = int(settings.REGISTRATION_FEE)


class ZarinpalClient:
    instance = None

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
        return cls.instance


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


def _redirect_homepage_with_action_status(action='payment', status=settings.OK_STATUS):
    response = redirect(reverse('homepage:homepage'))
    response['Location'] += '?%s=%s' % (action, status)
    return response


def signup(request):
    if request.user.is_authenticated:
        raise Http404
    if not SiteConfiguration.get_solo().is_signup_enabled:
        return redirect('homepage:homepage')
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
            email=request.POST['email'],
            is_active=False,
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

        html_content = strip_spaces_between_tags(render_to_string('auth/signup_email.html', {
            'user': member,
            'base_url': request.build_absolute_uri(reverse('homepage:homepage'))[:-1],
            'token': account_activation_token.make_token(member),
            'uid': urlsafe_base64_encode(force_bytes(member.pk))
        }))
        text_content = re.sub('<style[^<]+?</style>', '', html_content)
        text_content = strip_tags(text_content)

        msg = EmailMultiAlternatives('تایید ثبت‌نام اولیه', text_content, 'Rastaiha <info@rastaiha.ir>', [member.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return _redirect_homepage_with_action_status('signup', settings.OK_STATUS)
    return render(request, 'auth/signup.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        member = Member.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Member.DoesNotExist):
        member = None
    if member is not None and account_activation_token.check_token(member, token):
        member.is_active = True
        member.save()
        auth_login(request, member)
        # return redirect('home')
        return _redirect_homepage_with_action_status('activate', settings.OK_STATUS)
    elif member is not None and member.is_active:
        return _redirect_homepage_with_action_status('activate', settings.HELP_STATUS)
    else:
        return _redirect_homepage_with_action_status('activate', settings.ERROR_STATUS)


def login(request):
    if request.user.is_authenticated and SiteConfiguration.get_solo().is_game_running:
        return redirect('kabaramadalapeste:game')
    if request.method == "POST":
        members = Member.objects.filter(email__exact=request.POST.get('email'))
        if members.count() == 0:
            messages.error(request, 'ایمیل یا رمز عبور غلط است.')
            return render(request, 'auth/login.html')
        member = members[0]
        if not member.is_active:
            messages.error(request, 'به ایمیلت سر بزن و اول حسابت رو فعال کن')
            return render(request, 'auth/login.html')
        username = member.username
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('kabaramadalapeste:game')
        else:
            messages.error(request, 'ایمیل یا رمز عبور غلط است.')
            return render(request, 'auth/login.html')
    return render(request, 'auth/login.html')


@login_required
def logout(request):
    auth_logout(request)
    return redirect('accounts:login')


def verify(request):
    if request.GET.get('Status') == 'OK':
        result = ZarinpalClient.get_instance().service.PaymentVerification(
            MERCHANT, request.GET['Authority'], payment_amount
        )
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
            return _redirect_homepage_with_action_status("payment", settings.OK_STATUS)
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
            return _redirect_homepage_with_action_status("payment", settings.OK_STATUS)
            # return HttpResponse('Transaction submitted : ' + str(result.Status))
        else:
            payment_attempt.status = str(result.Status)
            payment_attempt.desc = 'Transaction failed.'
            payment_attempt.save()
            return _redirect_homepage_with_action_status("payment", settings.ERROR_STATUS)
            # return HttpResponse('Transaction failed.\nStatus: ' + str(result.Status))
    else:
        return _redirect_homepage_with_action_status("payment", settings.ERROR_STATUS)
        # return HttpResponse('Transaction failed or canceled by user')


@login_required
def send_request(request):
    if not request.user.is_participant:
        raise Http404
    if request.user.participant.is_activated:
        raise Http404
    if not SiteConfiguration.get_solo().is_signup_enabled:
        return redirect('homepage:homepage')
    callback_url = request.build_absolute_uri(reverse('accounts:verify'))
    result = ZarinpalClient.get_instance().service.PaymentRequest(
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


@login_required
def survey(request):
    return redirect('https://docs.google.com/forms/d/e/1FAIpQLScxNEMOwHQQ7LBdcKQ_Y68EJWcOqdj8ysCjgjOK-VZgf_PQ_Q/viewform')
