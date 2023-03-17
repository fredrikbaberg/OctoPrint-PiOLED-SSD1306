# coding=utf-8
from __future__ import absolute_import
import logging

import octoprint.plugin

from octoprint.events import Events
from .SSD1306 import SSD1306


class Ssd1306_pioled_displayPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.ShutdownPlugin,
    # octoprint.plugin.EventHandlerPlugin,
):
    
    def __init__(self):
        self.display = None

    def on_after_startup(self, *args, **kwargs):
        self._logger.info('Prepare display')
        self.display = SSD1306(
            width=128,
            height=32,
            refresh_rate=120,
        )
        self.display.write_row(0, 'Offline')
        self.display.commit()
        self.display.start()
        # self._printer.register_callback(self)

    def on_shutdown(self):
        self.display.stop()
        self.display.clear()
        self.display.commit()
        # self._printer.unregister_callback(self)

    # def on_event(self, event, payload):
    #     if(event == Events.PRINTER_STATE_CHANGED):
    #         self.display.write_row(1, '{event}, {payload}')

    # def on_printer_send_current_data(self, data, **kwargs):
    #     self._logger.debug('on_printer_send_current_data: %s', data)

    # def on_printer_add_temperature(self, data):
    #     self._logger.debug('on_printer_add_temperature: %s', data)

    def handle_connect_hook(self, *args, **kwargs):
        self._logger.info('handle_connect')
        self.display.write_row(0, 'Connecting')
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
        "octoprint.printer.handle_connect": __plugin_implementation__.handle_connect_hook
    }
