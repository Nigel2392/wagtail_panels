from django.shortcuts import get_object_or_404
from django.http import StreamingHttpResponse, HttpResponseForbidden
from django.contrib.contenttypes.models import ContentType
from wagtail import hooks

from django.urls import path, include

def file_iterator(file, chunk_size=8192):
    while True:
        chunk = file.read(chunk_size)
        if not chunk:
            break
        yield chunk

def download_panel(request, content_type_pk, object_pk, field_name):
    if not request.user.has_perm('wagtailadmin.access_admin'):
        return HttpResponseForbidden()
    
    content_type = get_object_or_404(ContentType, pk=content_type_pk)
    model = content_type.model_class()
    obj = get_object_or_404(model, pk=object_pk)
    field = getattr(obj, field_name)

    permissions = getattr(obj, f'get_{field}_permissions', None)
    if callable(permissions):
        permissions = permissions()

    if permissions:
        if isinstance(permissions, str):
            permissions = (permissions,)
        if not request.user.has_perms(permissions):
            return HttpResponseForbidden()
    
    if callable(field):
        field = field()

    response = StreamingHttpResponse(file_iterator(field.file))
    response['Content-Length'] = field.size
    response['Content-Disposition'] = f'attachment; filename="{field.name}"'
    return response


urlpatterns = [
    path('download/<int:content_type_pk>/<int:object_pk>/<slug:field_name>/', download_panel, name="panel"),
]

@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        path('download_panel/', include((urlpatterns, 'download_panel'), namespace='download_panel'), name='download_panel'),
    ]

