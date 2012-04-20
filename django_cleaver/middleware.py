
# Django settings
from django.conf import settings

# Project modules
from cleaver import (CLEVERCSS_SOURCE, CLEVERCSS_AUTOGENERATE,
                     generate_css_from_ccss, watch_directories)
from imagecreator import generate_images

class RegenerateCleverOutputMiddleware(object):

    def process_request(self, request):
        """Intercepts a request to verify that files have not changed on disk,
        regenerates the CleverCSS output if required, then allows the request
        to continue. Can be inserted anywhere in the request chain."""
        if settings.DEBUG and CLEVERCSS_AUTOGENERATE:
            if request.path.find(settings.MEDIA_URL) == -1:
                def callback(arg1, arg2):
                    print "Regenerating CleverCSS output ..."
                    # Generate CSS (more likely to produce an error ...)
                    generate_css_from_ccss()
                    print "Regenerating Images ..."
                    # Generate images next
                    generate_images()
                    return False
                watch_directories([CLEVERCSS_SOURCE,], callback)
        return None
