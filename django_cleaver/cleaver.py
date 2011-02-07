
# Python standard library
from os import path, listdir
from ConfigParser import RawConfigParser

# Third-party libraries
import clevercss
from clevercss.errors import *

# Application libraries
from dirwatch import watch_directories # ([paths,], func=callback, delay=1.0)

# Django settings
from django.conf import settings


# Retrieve execution parameters
MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT', False)
if not MEDIA_ROOT:
    raise ValueError("You must define a MEDIA_ROOT in settings.py!")
CLEVERCSS_SOURCE = getattr(settings, 'CLEVERCSS_SOURCE', \
        path.join(MEDIA_ROOT, 'clevercss'))
CLEVERCSS_OUTPUT = getattr(settings, 'CLEVERCSS_OUTPUT', \
        path.join(MEDIA_ROOT, 'css'))
CLEVERCSS_AUTOGENERATE = getattr(settings, 'CLEVERCSS_AUTOGENERATE', False)
CLEVERCSS_CONTEXTFILES = getattr(settings, 'CLEVERCSS_CONTEXTFILES', \
        path.join(CLEVERCSS_SOURCE, 'colors.ini'))


def ini_to_context(filenames=CLEVERCSS_CONTEXTFILES):
    """Loads a config.ini-formatted file at filename and returns a flat context
    object that always returns strings for both keys and values (e.g. no 
    natives) -- see ConfigParser.RawConfigParser in the standard library for
    format details
    """
    cparser = RawConfigParser()
    context = {}

    # If a single filename was provided, recast as an iterable now
    if isinstance(filenames, (str, unicode)):
        filenames = (filenames, )

    for filename in filenames:
        try:
            fob = open(filename, 'rb')
        except IOError, msg:
            raise
        try:
            config = RawConfigParser
        except Exception:
            raise

        # Read in our configuration file
        cparser.readfp(fob, filename)

        sections = cparser.sections()
        for section in sections:
            items = cparser.items(section)
            for item in items:
                context[item[0]] = item[1]
    
    return context


# Generate CSS from CleverCSS source files
def generate_css_from_ccss(context=None):
    """Parses CleverCSS source files in CLEVERCSS_SOURCE and generates CSS
    output, which is placed in CLEVERCSS_OUTPUT. Note that files beginning
    with an underscore will be ignored, as will any subdirectories."""
    source_dir = CLEVERCSS_SOURCE
    files = []
    # Gather a list of files that we will parse
    for filename in listdir(source_dir):
        # No partials allowed and only process filenames ending with 'ccss'
        if not filename.startswith('_') and filename.endswith('ccss'):
            fullname = path.join(source_dir, filename)
            if path.isfile(fullname): # No dirs/subdirs
                files.append(fullname)
    
    # If no context was passed, fetch one
    if isinstance(context, (str, unicode)): # Passed a file, not a dict?
        use_context = ini_to_context(context)
    else:
        use_context = context or ini_to_context()
    
    outfiles = []
    
    # Loop over found files and process them
    for filename in files:
        # Try to read the source file, handle exceptions, etc.
        try:
            srcfile = open(filename, 'r')
        except IOError, msg:
            raise
        try:
            converted = clevercss.convert(srcfile.read(), context=use_context, 
                    fname=filename)
        except (ParserError, EvalException), msg:
                raise ValueError, "Error in file %s: %s" % (filename, msg)
        finally:
            srcfile.close()

        # Try to dump output into targetfile
        targetname = path.basename(filename.rsplit('.', 1)[0] + '.css')
        targetfile = path.join(CLEVERCSS_OUTPUT, targetname)
        try:
            outfile = open(targetfile, 'w')
            outfiles.append(targetfile)
        except IOError, msg:
            raise
        try:
            outfile.write(converted)
            
        finally:
            outfile.close()

    # Done
    return outfiles
    

class RegenerateCleverOutputMiddleware(object):
    
    def process_request(self, request):
        """Intercepts a request to verify that files have not changed on disk,
        regenerates the CleverCSS output if required, then allows the request
        to continue. Can be inserted anywhere in the request chain."""
        if settings.DEBUG and CLEVERCSS_AUTOGENERATE:
            if request.path.find(settings.MEDIA_URL) == -1:
                def callback(arg1, arg2):
                    print "Regenerating CleverCSS output ..."
                    result = generate_css_from_ccss()
                    return False
                watch_directories([CLEVERCSS_SOURCE,], callback)
        return None



