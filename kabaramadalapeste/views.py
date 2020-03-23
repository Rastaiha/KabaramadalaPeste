from django.shortcuts import render


def game(request):
    return render(request, 'kabaramadalapeste/game.html', {
        'without_nav': True,
        'without_footer': True,
    })


def exchange(request):
    return render(request, 'kabaramadalapeste/exchange.html', {
        'without_nav': True,
        'without_footer': True,
    })
