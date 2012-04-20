
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
CLEVERCSS_SOURCE_ROOT = getattr(settings, 'CLEVERCSS_SOURCE_ROOT', \
        path.join(MEDIA_ROOT, 'clevercss'))
CLEVERCSS_SOURCE = getattr(settings, 'CLEVERCSS_SOURCE', \
        path.join(MEDIA_ROOT, 'clevercss'))
CLEVERCSS_OUTPUT = getattr(settings, 'CLEVERCSS_OUTPUT', \
        path.join(MEDIA_ROOT, 'css'))
CLEVERCSS_AUTOGENERATE = getattr(settings, 'CLEVERCSS_AUTOGENERATE', False)
CLEVERCSS_CONTEXTFILES = getattr(settings, 'CLEVERCSS_CONTEXTFILES', \
        path.join(CLEVERCSS_SOURCE, 'colors.ini'))


def get_ccss_file_list():
    """Returns a list of *.ccss files, excluding partials (filenames beginning
     with an underscore)"""
    source_dir = CLEVERCSS_SOURCE
    files = []
    # Gather a list of files that we will parse
    for filename in listdir(source_dir):
        # No partials allowed and only process filenames ending with 'ccss'
        if not filename.startswith('_') and filename.endswith('ccss'):
            fullname = path.join(source_dir, filename)
            if path.isfile(fullname): # No dirs/subdirs
                files.append(fullname)
    return files


def ini_to_context(filenames=CLEVERCSS_CONTEXTFILES):
    """Loads a config.ini-formatted file at filename and returns a flat context
    object that always returns strings for both keys and values (e.g. no 
    natives) -- see ConfigParser.RawConfigParser in the standard library for
    format details
    """
    context = {}

    # If a single filename was provided, recast as an iterable now
    if isinstance(filenames, (str, unicode)):
        filenames = (filenames, )

    for filename in filenames:
        cparser = RawConfigParser()
        try:
            fob = open(filename, 'rb')
        except IOError, msg:
            raise

        # Read in our configuration file
        cparser.readfp(fob, filename)

        sections = cparser.sections()
        for section in sections:
            items = cparser.items(section)
            for item in items:
                context[item[0]] = item[1]
    
    return context


def flatten_context(context=None):
    """Flattens a context file out to a dictionary of variable names and
    literal values. All variables are removed. This is handy for creating
    a "simpler" file for previewing the colours without generating the CSS,
    and for external use (such as providing color values for generating images.

    N.B. that sprite maps are not be returned, but the definitions for the
    sprites themselves are.
    """
    # If no context was passed, fetch one
    if isinstance(context, (str, unicode)): # Passed a file, not a dict?
        use_context = ini_to_context(context)
    else:
        use_context = context or ini_to_context()

    # Get a single file so the parser can resolve directory names.
    ccss_file = get_ccss_file_list()[0]

    # Create Parser and Context instances
    ps = clevercss.engine.Parser(fname=ccss_file)
    cxo = clevercss.Context(use_context)
    cxo.minified = False

    # Convert context into expressions that can be evaluated
    for key, value in cxo.iteritems():
        if isinstance(value, str):
            expr = ps.parse_expr(1, value)
            cxo[key] = expr

    # Loop over all the 'keys' in the context and evaluate their expression
    flat = {}
    for key, value in use_context.iteritems():
        expr = ps.parse_expr(1, value)

        # We can't return sprite maps. Sorry!
        if not isinstance(expr, clevercss.expressions.SpriteMap):
            keyvar = clevercss.expressions.Var(key)
            flat[key] = keyvar.to_string(cxo)

    return flat


def generate_css_from_ccss(context=None):
    """Parses CleverCSS source files in CLEVERCSS_SOURCE and generates CSS
    output, which is placed in CLEVERCSS_OUTPUT. Note that files beginning
    with an underscore will be ignored, as will any subdirectories."""
    # Get a list of CCSS files
    files = get_ccss_file_list()
    
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
            try:
                converted = clevercss.convert(srcfile.read(), use_context,
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
        """Deprecated."""
        raise DeprecationWarning("Please use django_cleaver.middleware."
                                 "RegenerateCleverOutputMiddleware instead")
