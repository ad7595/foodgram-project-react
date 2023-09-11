from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

# handler404 = '_________.views.page_not_found'
# handler500 = '_________.views.server_error'
# handler403 = '_________.views.permission_denied'

# if settings.DEBUG:
#     urlpatterns += static(
#         settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
#     )
