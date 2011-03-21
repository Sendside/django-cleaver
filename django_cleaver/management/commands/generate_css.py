
# Python Standard Library
# from optparse import make_option

# Django modules
from django.core.management.base import BaseCommand
# from django.conf import settings

# Application modules
from django_cleaver.cleaver import generate_css_from_ccss


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        """Runs the CleverCSS compiler against all found media files in the
        CLEVERCSS_SOURCE directory. Partials (e.g. "_filename.ccss") are 
        ignored."""
        outfiles = generate_css_from_ccss()
        for filename in outfiles:
            print "Output compiled CSS file %s" % (filename,)


