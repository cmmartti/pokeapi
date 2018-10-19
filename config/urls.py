# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url

from pokemon_v2 import urls as pokemon_v2_urls

urlpatterns = [
    url(r'^', include(pokemon_v2_urls)),
]
