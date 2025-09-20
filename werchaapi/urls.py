from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import RedirectView
from django.http import HttpResponse


def healthz(_):
    return HttpResponse("ok", content_type="text/plain")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/catalog/', include('catalog.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/blog/', include('blog.urls')),
    path('healthz', healthz),


]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

