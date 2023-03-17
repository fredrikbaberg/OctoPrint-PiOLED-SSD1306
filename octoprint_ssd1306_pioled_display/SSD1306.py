import copy
import os
import sys
import threading
from time import sleep
from PIL import Image, ImageDraw, ImageFont

def _find_resource(file):
    # Find a resource in the same parent module as this module
    guesses = []
    for p in sys.path:
        f = os.path.join(p, os.path.dirname(__file__), file)
        guesses.append(f)
        if os.path.isfile(f):
            return f
    raise ValueError('Cannot find resource {} at {}'.format(file, guesses))


class SSD1306(threading.Thread):
    _lock = threading.Lock()
    _stop = False
    _rows = []
    _committed_rows = []
    
    def __init__(self, width=128, height=32, fontsize=8, refresh_rate=2):
        super(SSD1306, self).__init__()

        # Preparation
        self._height = height
        self._width = width
        self._fontsize = fontsize
        self._y_offset = 0
        # self._font = ImageFont.load_default()
        self._font = ImageFont.truetype(_find_resource('font/PressStart2P.ttf'), self._fontsize)
        self._refresh_rate = refresh_rate
        self._image = Image.new('L', (self._width, self._height))
        self._draw = ImageDraw.Draw(self._image)
        self._rows = [''] * round(self._height/self._fontsize) # Only allow as many rows as can fit.

    # Clear content.
    def clear(self):
        """
        Clear content.
        """
        for i in range(0, len(self._rows)):
            self._rows[i] = ''

    # Write content to row.
    def write_row(self, row, text):
        """
        Write data to row.
        """
        if(row < len(self._rows)):
            self._rows[row] = text

    def commit(self):
        """
        Send data to be shown on the display.
        """
        with self._lock:
            self._committed_rows = copy.copy(self._rows)
        print(self._committed_rows)

    def run(self):
        """
        Loop that updates what is shown on the display
        """
        while not self._stop:
            with self._lock:
                rows = copy.copy(self._committed_rows)
            # Clear image
            self._draw.rectangle((0, 0, self._width, self._height), fill=0)
            # Draw text on image.
            for (r, t) in enumerate(rows):
                self._draw.text((0, r * self._fontsize + self._y_offset), t, font=self._font, fill=200)
            # self._image.save('test.png')
            sleep(1/self._refresh_rate) # Avoid spamming the screen.

    def stop(self):
        self._stop = True
