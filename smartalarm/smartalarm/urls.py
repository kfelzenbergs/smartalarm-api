"""smartalarm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from smartalarm_api.views.views import *
from smartalarm_api.views.auth_views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', UserLoginView.as_view()),
    url(r'^profile/$', UserProfileView.as_view()),
    url(r'^trackers/$', TrackersView.as_view(), name='tracker-list'),
    url(r'^tripstats/$', TripStatsView.as_view()),
    url(r'^trips/$', TripsView.as_view()),
    url(r'^zones/$', ZonesView.as_view()),
    url(r'^stats_gateway/$', StatsGatewayView.as_view()),
    url(r'^event_gateway/$', EventGatewayView.as_view()),
    url(r'^stats_history_gateway/$', StatsHistoryGatewayView.as_view()),
    url(r'^calls_callback/$', CallsCallbackView.as_view()),
]
