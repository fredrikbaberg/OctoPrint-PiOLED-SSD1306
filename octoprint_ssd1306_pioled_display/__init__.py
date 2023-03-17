# coding=utf-8
from __future__ import absolute_import

import logging
import textwrap

import octoprint.plugin
from octoprint.events import Events

from .SSD1306 import SSD1306


class Ssd1306_pioled_displayPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.ShutdownPlugin,
):

    def __init__(self):
        self.display = None

    def on_startup(self, *args, **kwargs):
        self._logger.info('Initializing plugin')
        self.display = SSD1306(
            width=128,
            height=32,
            refresh_rate=1,
            logger=self._logger
        )
        self.display.start()
        self.display.write_row(0, 'Offline')
        self.display.commit()
        self._logger.info('Initialized.')

    def on_after_startup(self, *args, **kwargs):
        # self._printer.register_callback(self)
        pass

    def on_shutdown(self):
        # self._printer.unregister_callback(self)
        self.display.clear()
        self.display.commit()
        self.display.stop()

    # def on_event(self, event, payload):
    #     if(event == Events.PRINTER_STATE_CHANGED):
    #         self.display.write_row(1, '{event}, {payload}')
    # def on_printer_send_current_data(self, data, **kwargs):
    #     self._logger.debug('on_printer_send_current_data: %s', data)
    # def on_printer_add_temperature(self, data):
    #     self._logger.debug('on_printer_add_temperature: %s', data)

    def protocol_gcode_sent_hook(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
        """ Listen for gcode commands, specifically M117 (Set LCD message) """
        if (gcode is not None) and (gcode == 'M117'):
            self._logger.info('Intercepted M117 gcode: {}'.format(cmd))
            max_chars_per_line = round(
                self.display._width/6)  # Assume width=6px
            max_lines = 2  # Set number of available lines
            start_line = 1
            lines = textwrap.fill(
                text=' '.join(cmd.split(' ')[1:]),
                width=max_chars_per_line,
                max_lines=max_lines
            ).split('\n')
            self._logger.info('Split message: "%s"', lines)
            for i in range(0, max_lines):
                self.display.write_row(
                    start_line + i,
                    lines[i] if i < len(lines) else ''
                )
            self.display.commit()

    # ~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "ssd1306_pioled_display": {
                "displayName": self._plugin_name,
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "fredrikbaberg",
                "repo": "OctoPrint-PiOLED-SSD1306",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/fredrikbaberg/OctoPrint-PiOLED-SSD1306/archive/{target_version}.zip",

                "stable_branch": {
                    "name": "Stable",
                    "branch": "main",
                    "comittish": ["main"],
                },

                "prerelease_branches": [
                    {
                        "name": "Release Candidate",
                        "branch": "rc",
                        "comittish": ["rc", "main"],
                    }
                ]
            }
        }


# Set the Python version your plugin is compatible with below. Recommended is Python 3 only for all new plugins.
# OctoPrint 1.4.0 - 1.7.x run under both Python 3 and the end-of-life Python 2.
# OctoPrint 1.8.0 onwards only supports Python 3.
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Ssd1306_pioled_displayPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.comm.protocol.gcode.sent": __plugin_implementation__.protocol_gcode_sent_hook,
    }
