import threading


class SSD1306(threading.Thread):
    def __init__(self):
        super(SSD1306, self).__init__()
