import copy
import threading
from time import sleep

import adafruit_ssd1306
import busio
from PIL import Image, ImageDraw, ImageFont
try:
    from board import SCL, SDA
except:
    pass

from octoprint_ssd1306_pioled_display.helpers import find_resource


class SSD1306(threading.Thread):
    _lock = threading.Lock()
    _stop = False
    daemon = True
    _rows = []
    _committed_rows = []

    def __init__(self, width=128, height=32, fontsize=8, refresh_rate=1, logger=None):
        super(SSD1306, self).__init__()

        # Setup variables
        self._height = height
        self._width = width
        self._fontsize = fontsize
        self._y_offset = 0
        self._logger = logger
        self._refresh_rate = refresh_rate
        # self._font = ImageFont.load_default()
        self._font = ImageFont.truetype(find_resource(
            'font/PressStart2P.ttf'), self._fontsize)
        self._image = Image.new('1', (self._width, self._height))
        self._draw = ImageDraw.Draw(self._image)
        # Only allow as many rows as can fit on screen.
        self._rows = [''] * round(self._height/self._fontsize)

        try:
            i2c = busio.I2C(SCL, SDA)
            self._display = adafruit_ssd1306.SSD1306_I2C(
                self._width, self._height, i2c)
        except:
            self.log('Failed to initialize display')

    # Clear content.
    def clear(self):
        """ Clear content """
        for i in range(0, len(self._rows)):
            self._rows[i] = ''

    # Write content to row.
    def write_row(self, row, text):
        """ Write data to row """
        if (row < len(self._rows)):
            self._rows[row] = text

    def commit(self):
        """ Send data to be shown on the display. """
        with self._lock:
            self._committed_rows = copy.copy(self._rows)
        self.log(self._committed_rows)

    def run(self):
        """ Loop that update what is shown on the display """
        while not self._stop:
            with self._lock:
                rows = copy.copy(self._committed_rows)
            # Clear display
            self._draw.rectangle((0, 0, self._width, self._height), fill=0)
            # Draw text on image
            for (r, t) in enumerate(rows):
                self._draw.text(
                    (0, r * self._fontsize + self._y_offset), t, font=self._font, fill=200)
            try:
                # Send image to display
                self._display.image(self._image)
                # Show
                self._display.show()
            except:
                self.log('Failed to send to display')
            sleep(1/self._refresh_rate)

    def stop(self):
        """ Stop thread when done with current iteration. """
        self._stop = True

    def log(self, message):
        """ Log message """
        if self._logger != None:
            self._logger.log(message)
        else:
            print(message)
