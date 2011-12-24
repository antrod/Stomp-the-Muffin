from django.conf.urls.defaults import *
from matrix import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('matrix.ms.views',
    (r'^m/activegame$', 'get_active_game'),
    (r'^m/(?P<game_id>\d+?)/(?P<photo_file>.+?)$', 'register'),
    (r'^m/go/(?P<permalink>.+?)$', 'go'),
    (r'^m/play/(?P<permalink>.+?)$', 'play'),
    (r'^m/kill/(?P<permalink>.+?)$', 'attempt_kill'),
    (r'^m/feedback$', 'take_feedback'),
    (r'^m/prize$', 'prize'),
    
    (r'^m/adminstart$', 'admin_start'),
    (r'^m/startgame/(?P<game_id>\d+?)$', 'start_game'),
    (r'^m/status/(?P<game_id>\d+?)$', 'status'),
    (r'^m/report/(?P<game_id>\d+?)$', 'feedback_report'),
    (r'^m/getfeedback/(?P<game_id>\d+?)$', 'send_feedback_request'),
    (r'^m/prune/(?P<game_id>\d+?)$', 'prune_inactives'),
    (r'^m/actives/(?P<game_id>\d+?)$', 'list_actives'),
    (r'^m/playerstatus/(?P<permalink>.+?)$', 'player_status'),
    (r'^m/makeinactive/(?P<permalink>.+?)$', 'make_inactive')
    )

urlpatterns += patterns('',
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)))

urlpatterns += staticfiles_urlpatterns()