import os
import sys


def find_resource(file):
    # Find a resource in the same parent module as this module
    guesses = []
    for p in sys.path:
        f = os.path.join(p, os.path.dirname(__file__), file)
        guesses.append(f)
        if os.path.isfile(f):
            return f
    raise ValueError('Cannot find resource {} at {}'.format(file, guesses))

def format_seconds(self, seconds):
        h = int(seconds / 3600)
        m = int((seconds - h * 3600) / 60)
        return '{}h {}m'.format(h, m) if h > 0 else '{}m'.format(m)
