from time import sleep
from SSD1306 import SSD1306

# Simple test of SSD1306

display = SSD1306(width=128, height=32, refresh_rate=120)

# Can clear values
display.clear()

# Can write rows without breaking
for i in range(0, 10):
    display.write_row(i, 'Line {}; '.format(i)*i)
    display.commit()

# Can run in thread
display.clear()
display.start()
for i in range(0, 2+len(display._rows)):
    display.write_row(i, 'Line {}'.format(i))
    display.commit()
    sleep(1/display._refresh_rate)
display.clear()
display.commit()
sleep(1/display._refresh_rate)
display.stop()