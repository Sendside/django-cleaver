
# Python standard library
from os import path, listdir
from ConfigParser import ConfigParser

# Third-party libraries
from imagecraft import ImageGenerator

# Django settings
from django.conf import settings

# This module
from cleaver import ini_to_context, flatten_context


# Retrieve execution params
MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT', False)
if not MEDIA_ROOT:
    raise ValueError("You must define a MEDIA_ROOT in settings.py!")
CLEVERCSS_SOURCE = getattr(settings, 'CLEVERCSS_SOURCE', \
                           path.join(MEDIA_ROOT, 'clevercss'))
CLEVERCSS_AUTOGENERATE = getattr(settings, 'CLEVERCSS_AUTOGENERATE', False)
CLEVERCSS_CONTEXTFILES = getattr(settings, 'CLEVERCSS_CONTEXTFILES', False)
if not CLEVERCSS_CONTEXTFILES:
    raise ValueError("You must define CLEVERCSS_CONTEXTFILES in settings.py!")
CLEVERCSS_IMAGE_JOBS = getattr(settings, "CLEVERCSS_IMAGE_JOBS", None)
CLEVERCSS_IMAGE_SOURCE = getattr(settings, "CLEVERCSS_IMAGE_SOURCE", None)
CLEVERCSS_IMAGE_OUTPUT = getattr(settings, "CLEVERCSS_IMAGE_OUTPUT", None)

# Throw errors if information is missing
if not CLEVERCSS_CONTEXTFILES:
    raise ValueError("You must define CLEVERCSS_CONTEXTFILES")
if not CLEVERCSS_IMAGE_SOURCE:
    raise ValueError("You must define CLEVERCSS_IMAGE_SOURCE")
if not CLEVERCSS_IMAGE_OUTPUT:
    raise ValueError("You must define CLEVERCSS_IMAGE_OUTPUT")


class DynamicImageGenerator(ImageGenerator):
    """Dynamically generates images by using arguments instead of constants"""

    #layers = None
    _default_source_path = CLEVERCSS_IMAGE_SOURCE
    _default_output_path = CLEVERCSS_IMAGE_OUTPUT
    image_format = 'PNG'

    def __init__(self, color_dict, source_path=None, output_path=None,
                 layers=(), output_filename=None):
        """Constructor"""
        self.layers = layers
        self.output_filename = output_filename
        super(DynamicImageGenerator, self).__init__(color_dict, source_path,
                                                    output_path)


def generate_images():
    """Reads the context file and uses it to execute all CLEVERCSS_IMAGE_JOBS
    specified in a settings file"""
    # If there are no jobs, die
    if not CLEVERCSS_IMAGE_JOBS:
        return

    context = flatten_context(ini_to_context())

    # Unpack SortedDict with tuple for values 
    for filename, values in CLEVERCSS_IMAGE_JOBS.items():
        layers = values.values()
        DynamicImageGenerator(context, layers=layers,
                              output_filename=filename).render()

