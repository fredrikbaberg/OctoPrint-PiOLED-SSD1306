# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
from .SSD1306 import SSD1306


class Ssd1306_pioled_displayPlugin(
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin
):

    # ~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return {
            # put your plugin's default settings here
        }

    # ~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": ["js/ssd1306_pioled_display.js"],
            "css": ["css/ssd1306_pioled_display.css"],
            "less": ["less/ssd1306_pioled_display.less"]
        }

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


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
# __plugin_name__ = "Ssd1306_pioled_display Plugin"


# Set the Python version your plugin is compatible with below. Recommended is Python 3 only for all new plugins.
# OctoPrint 1.4.0 - 1.7.x run under both Python 3 and the end-of-life Python 2.
# OctoPrint 1.8.0 onwards only supports Python 3.
# __plugin_pythoncompat__ = ">=3,<4"  # Only Python 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Ssd1306_pioled_displayPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }