from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

from apps.shutthatdown.views import HomeView, QuoteView, StateView, BrowseView, SubmitView

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', HomeView.as_view()),
    url(r'^quote/(?P<quote>[0-9]+)?$', QuoteView.as_view()),
    url(r'^state/(?P<state>[a-zA-Z]{2})?$', StateView.as_view()),
    url(r'^browse/$', QuoteView.as_view()), # When no quote type is specified, show a random quote
    url(r'^browse/(?P<type>[a-z\-]+)$', BrowseView.as_view()),
    url(r'^submit/$', SubmitView.as_view()),
]
