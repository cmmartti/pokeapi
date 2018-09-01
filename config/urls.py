# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, RedirectView
from graphene_django.views import GraphQLView

from pokemon import urls as pokemon_urls
from pokemon_v2 import urls as pokemon_v2_urls
from pokemon_graphql.schema import schema

# Update to Django 1.11 requires below to be implemented
# https://stackoverflow.com/questions/38744285/django-urls-error-view-must-be-a-callable-or-a-list-tuple-in-the-case-of-includ

urlpatterns = [

    url(r'^admin/', include(admin.site.urls)),
    url(r"^stripe/donation", "config.views.stripe_donation"),
    # url(r'^media/(?P<path>.*)',
    #     'django.views.static.serve',
    #     {'document_root': settings.MEDIA_ROOT}
    # ),
    # url(r'^static/(?P<path>.*)',
    #     'django.views.static.serve',
    #     {'document_root': settings.STATIC_ROOT}
    # ),
    url(r'^$', 'config.views.home'),

    url(r'^docsv1/$', RedirectView.as_view(url='/docs/v1'), name='v1_redirect'),
    url(r'^docsv2/$', RedirectView.as_view(url='/docs/v2'), name='v2_redirect'),

    url(r'^docs/v1/$',
        TemplateView.as_view(template_name='pages/docsv1.html'),
        name="docs_v1"
    ),
    url(r'^docs/v2/$',
        TemplateView.as_view(template_name='pages/docsv2.html'),
        name="docs_v2"
    ),
    url(r'^docs/graphql/$',
        TemplateView.as_view(template_name='pages/docs-graphql.html'),
        name="docs_graphql"
    ),
    url(r'^explore/graphql/$',
        TemplateView.as_view(template_name='pages/explore_graphql.html'),
        name="explore_graphql"
    ),

    url(r'^404/$', TemplateView.as_view(template_name='404.html'), name="404"),
    url(r'^500/$', TemplateView.as_view(template_name='500.html'), name="500"),
    url(r'^about/$', 'config.views.about'),
    url(r'^', include(pokemon_urls)),
    url(r'^', include(pokemon_v2_urls)),
    url(r'^graphql', csrf_exempt(GraphQLView.as_view(graphiql=False, schema=schema))),

] # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
