
# Django modules
from django.core.management.base import BaseCommand

# Application modules
from django_cleaver.cleaver import flatten_context


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        """Runs the CleverCSS compiler without actually compiling any CSS;
        just reads the context file(s) and spits out a dictionary of evaluated
        context variables for use elsewhere.
        """
        flat_context = flatten_context()
        print flat_context