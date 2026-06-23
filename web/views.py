"""Views for the web app.

Views stay thin: parse the request, call a service, render a template. Business
logic belongs in `web.services`, not here.
"""

from django.shortcuts import render

from web import services


def home(request):
    context = {
        "greeting": services.greeting(request.GET.get("name", "")),
        "messages": services.recent_messages(),
    }
    return render(request, "web/home.html", context)
