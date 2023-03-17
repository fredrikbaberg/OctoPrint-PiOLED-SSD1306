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


def format_temp(self, tool, temp):
    tool_txt = tool[0].upper()
    if tool[-1].isdigit():
        tool_txt += tool[-1]
    target_dir = '_'
    if temp['target'] > 0:
        if abs(temp['target'] - temp['actual']) < 5:
            target_dir = '-'
        else:
            target_dir = '/' if temp['target'] > temp['actual'] else '\\'
    return '{}:{}{}'.format(tool_txt, int(temp['actual']), target_dir)
