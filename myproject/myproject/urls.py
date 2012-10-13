'''

Copyright (c) 2012, Kris Lamoureux
All rights reserved.

DJ-BaseSite is released under the New BSD Liscense.
Please take a momemt to read the short 3 Clause LICENSE file.

'''


from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('<%myproject%>.views',

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
	url(r'^$', 'index'),
	url(r'^login/$', 'login_user'),
	url(r'^logout/$', 'logout_user'),
	url(r'^register/$', 'register_user'),
	url(r'^activate/$', 'activate_user'),
	#url(r'^deactivate/$', 'activate_user'), Deactivate needs to be written.
)

urlpatterns += staticfiles_urlpatterns()