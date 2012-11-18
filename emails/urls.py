# -*- coding: utf-8 -*-

#from django.conf.urls.defaults import *
from django.conf.urls import url
from django.conf.urls import patterns
from django.utils.translation import ugettext_lazy as _

from django.conf.urls import patterns, include, url
from django.utils.translation import ugettext_lazy as _

urlpatterns = patterns('apps.mailing.emails.views',
    url(_(r'^pokaz/(?P<key>[\w\-_]+)$'), 'show_email', name='show')
)
