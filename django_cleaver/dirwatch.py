#!/usr/env python

"""
Presented as a recipe for watching directories in an OS-agnostic manner. Not
hyper-performant, but will only be used on development machines.

Watches one or more paths for changes at a regular delay interval (in seconds),
executing callback callback when changes are detected.

Derived from code written by Andrew M. Kuchling, no licence stated.
http://www.amk.ca/python/simple/dirwatch.html
"""

import os, time
from django.core.cache import cache

def watch_directories(paths, callback):
    """(paths:[str], callback:callable, delay:float)
    Continuously monitors the paths and their subdirectories
    for changes.  If any files or directories are modified,
    the callable 'callback' is called with a list of the modified paths of both
    files and directories.  'callback' can return a Boolean value
    for rescanning; if it returns True, the directory tree will be
    rescanned without calling callback() for any found changes.
    (This is so callback() can write changes into the tree and prevent itself
    from being immediately called again.)
    """
    # Deal with paths sent as strings instead of a list!
    if isinstance(paths, (str, unicode)):
        paths = [paths,]

    # Main loop
    pa = "cleaver_paths"
    rs = "cleaver_rescan"
    cl = "cleaver_changed_list"
    rf = "cleaver_remaining_files"
    af = "cleaver_all_files"
    
    cache_lifetime = 60 * 60 * 1
    if cache.get(rs) is not None:
        rescan = cache.get(rs)
        if rescan == 0:
            rescan = False
        changed_list = []
        all_files = cache.get(af)
        remaining_files = all_files.copy()
        all_files = {}
        
    else:
        # Cache has expired/does not exist; make sure we regenerate.
        rescan = False
        changed_list = []
        all_files = {}
        remaining_files = all_files.copy()
        cache.set(rs, rescan, cache_lifetime)
        cache.set(cl, changed_list, cache_lifetime)
        cache.set(rf, remaining_files, cache_lifetime)
        cache.set(af, all_files, cache_lifetime)
        
    # Basic principle: all_files is a dictionary mapping paths to
    # modification times.  We repeatedly crawl through the directory
    # tree rooted at 'path', doing a stat() on each file and comparing
    # the modification time.

    def f(unused, dirname, files):
        # Traversal callbacktion for directories
        for filename in files:
            path = os.path.join(dirname, filename)

            try:
                t = os.stat(path)
            except os.error:
                # If a file has been deleted between os.path.walk()
                # scanning the directory and now, we'll get an
                # os.error here.  Just ignore it -- we'll report
                # the deletion on the next pass through the main loop.
                continue

            mtime = remaining_files.get(path)
            if mtime is not None:
                # Record this file as having been seen
                del remaining_files[path]
                # File's mtime has been changed since we last looked at it.
                if t.st_mtime > mtime:
                    changed_list.append(path)
            else:
                # No recorded modification time, so it must be
                # a brand new file.
                changed_list.append(path)

            # Record current mtime of file.
            all_files[path] = t.st_mtime

    for path in paths:
        os.path.walk(path, f, None)
    removed_list = remaining_files.keys()
    
    if rescan:
        rescan = False
    elif changed_list or removed_list:
        rescan = callback(changed_list, removed_list)
    
    # Store values now
    cache.set(rs, rescan, cache_lifetime)
    cache.set(cl, changed_list, cache_lifetime)
    cache.set(rf, remaining_files, cache_lifetime)
    cache.set(af, all_files, cache_lifetime)


