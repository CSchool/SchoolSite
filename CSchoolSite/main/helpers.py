import mimetypes
import os.path

from django.http import HttpResponse, HttpResponseServerError

from CSchoolSite.settings import FILESERVE_MEDIA_URL, FILESERVE_METHOD


def file_response(file):
    mime = mimetypes.MimeTypes()
    mime_type = mime.guess_type(file.path)[0]
    if FILESERVE_METHOD == "django":
        f = file.file
        f.open()
        content = f.read()
        f.close()
        response = HttpResponse(content, content_type=mime_type)
    elif FILESERVE_METHOD == "xsendfile":
        response = HttpResponse(content_type=mime_type)
        response['X-Sendfile'] = file.path.encode('utf-8')
        response['Content-Length'] = file.size
    elif FILESERVE_METHOD == "nginx":
        response = HttpResponse(content_type=mime_type)
        response['X-Accel-Redirect'] = os.path.join(FILESERVE_MEDIA_URL, file.name).encode('utf-8')
        response['Content-Length'] = file.size
    else:
        raise HttpResponseServerError
    return response
