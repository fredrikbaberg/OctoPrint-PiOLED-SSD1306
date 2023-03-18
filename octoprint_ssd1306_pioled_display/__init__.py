# coding=utf-8
from __future__ import absolute_import

# import logging
import textwrap

import octoprint.plugin
from octoprint.events import Events

from octoprint_ssd1306_pioled_display.helpers import format_seconds, format_temp
# from octoprint.printer import PrinterCallback

from .SSD1306 import SSD1306


class Ssd1306_pioled_displayPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.ShutdownPlugin,
    octoprint.plugin.EventHandlerPlugin,
    octoprint.printer.PrinterCallback,
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
        self._printer.register_callback(self)

    def on_shutdown(self):
        self._printer.unregister_callback(self)
        self.display.clear()
        self.display.commit()
        self.display.stop()

    def on_event(self, event, payload, *args, **kwargs):
        """ Display printer status events on the first line """
        self._logger.info('on_event: %s, %s', event, payload)

        if event == Events.ERROR:
            try:
                self.display.write_row(0, 'Error! {}'.format(payload['error']))
                self.display.commit()
            except:
                self._logger.debug('Display currently unavailable.')
        elif event == Events.PRINTER_STATE_CHANGED:
            try:
                self.display.write_row(0, payload['state_string'])
                if payload['state_id'] == 'OFFLINE':
                    # If the printer is offline, clear printer and job messages
                    self.display.clear_rows(start=1, end=2)
                self.display.commit()
            except:
                self._logger.debug('Display currently unavailable.')

    def on_printer_send_current_data(self, data, **kwargs):
        """ Display print progress on lines 1-? """
        self._logger.debug('on_printer_send_current_data: %s', data)
        completion = data['progress']['completion']

        match completion:
            case None:
                self.display.write_row(1,'')

        # if completion is None:
        #     # Job is complete or no job is started.
        #     self.display.clear_rows(1)
        # else:
        #     self.display.write_row(1, '{}% Completed'.format(int(completion)))
        #     # Show elapsed time and remaining time
        #     elapsed = data['progress']['printTime']
        #     self.display.write_row(
        #         2,
        #         '{} Elapsed'.format(format_seconds(elapsed))
        #     )

        #     remaining = data['progress']['printTimeLeft']
        #     if remaining is not None:
        #         self.display.write_row(3, '{} Left'.format(
        #             self._format_seconds(remaining)))
        #     else:
        #         self.display.clear_rows(3)

        self.display.commit()

    def on_printer_add_temperature(self, data):
        """ Display printer temperatures """
        self._logger.debug('on_printer_add_temperature: %s', data)

        msg = []
        for k in ['bed', 'tool0', 'tool1', 'tool2']:
            if k in data.keys():
                msg.append(format_temp(k, data[k]))
        try:
            self.display.write_row(2, ' '.join(msg))
            self.display.commit()
        except:
            self._logger.info(
                'Failed to send temperature(S) to display')

    def protocol_gcode_sent_hook(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
        """ Listen for gcode commands, specifically M117 (Set LCD message) """
        if (gcode is not None) and (gcode == 'M117'):
            self._logger.info('Intercepted M117 gcode: {}'.format(cmd))
            max_chars_per_line = 16  # Each char. is 8 px. wide
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
