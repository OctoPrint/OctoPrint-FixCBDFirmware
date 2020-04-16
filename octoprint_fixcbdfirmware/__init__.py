# coding=utf-8
from __future__ import absolute_import, unicode_literals

import octoprint.plugin

import re

class FixCBDFirmwarePlugin(octoprint.plugin.OctoPrintPlugin):

	REGEX_XYZ0 = re.compile(r"(?P<axis>[XYZ])(?=[XYZ]|\s|$)")
	REGEX_XYZE0 = re.compile(r"(?P<axis>[XYZE])(?=[XYZE]|\s|$)")

	def initialize(self):
		self._logger.info("Plugin active, working around broken 'CBD make it' firmware")

	def rewrite_sending(self, comm_instance, phase, cmd, cmd_type, gcode, subcode=None, *args, **kwargs):
		if gcode == "M110":
			# firmware chokes on N parameters with M110, fix that
			self._log_replacement(cmd, "M110")
			return "M110"
		elif gcode == "G28":
			# firmware chokes on X, Y & probably Z parameter, rewrite to X0, Y0, Z0
			rewritten = self.REGEX_XYZ0.sub("\g<axis>0 ", cmd).strip()
			self._log_replacement(cmd, rewritten)
			return rewritten
		elif gcode in ["M18", "M84"]:
			# firmware chokes on X, Y, Z and E parameter, rewrite to X0, Y0, Z0, E0
			rewritten = self.REGEX_XYZE0.sub("\g<axis>0 ", cmd).strip()
			self._log_replacement(cmd, rewritten)
			return rewritten

	def rewrite_received(self, comm_instance, line, *args, **kwargs):
		line = self._rewrite_wait_to_busy(line)
		line = self._rewrite_identifier(line)
		return line

	def _rewrite_wait_to_busy(self, line):
		# firmware wrongly assumes "wait" to mean "busy", fix that
		if line == "wait" or line.startswith("wait"):
			self._log_replacement("wait", "echo:busy processing")
			return "echo:busy processing"
		else:
			return line

	def _rewrite_identifier(self, line):
		# change identifier to signal stuff is fixed so that printer safety no longer triggers
		rewritten = None

		if "CBD make it" in line:
			rewritten = line.replace("CBD make it", "CBD made it, foosel fixed it")
		elif "ZWLF make it" in line:
			rewritten = line.replace("ZWLF make it", "ZWLF made it, foosel fixed it")

		if rewritten:
			self._log_replacement(line, rewritten)
			return rewritten

		return line

	def _log_replacement(self, orig, repl):
		self._logger.info("Replacing {} with {}".format(orig, repl))
		self._log_to_terminal("{} -> {}".format(orig, repl))

	def _log_to_terminal(self, *lines, **kwargs):
		prefix = kwargs.pop(b"prefix", "Repl:")
		if self._printer:
			self._printer.log_lines(*list(map(lambda x: "{} {}".format(prefix, x),
			                                  lines)))

	##~~ Softwareupdate hook

	def get_update_information(self):
		return dict(
			fixcbdfirmware=dict(
				displayName="Fix CBD Firmware Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="OctoPrint",
				repo="OctoPrint-FixCBDFirmware",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/OctoPrint/OctoPrint-FixCBDFirmware/archive/{target_version}.zip"
			)
		)

__plugin_name__ = "Fix CBD Firmware Plugin"
__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = FixCBDFirmwarePlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
		"octoprint.comm.protocol.gcode.received": (__plugin_implementation__.rewrite_received, 1),
		"octoprint.comm.protocol.gcode.sending": (__plugin_implementation__.rewrite_sending, 1)
	}

