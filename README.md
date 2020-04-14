# Fix CBD Firmware

This plugin works around issues with a firmware that identifies itself only with the string `CBD make it` in response
to `M115` - hence the name "CBD Firmware" due to a lack of alternatives - and which wrongly implements some parts of
the established communication protocol, causing severe issues when trying to communicate and print with it from
OctoPrint.

You can read more about this firmware and what printers are currently known to ship with it
[in this FAQ entry](https://faq.octoprint.org/warning-firmware-broken-cbd).

Installing this plugin should make any printers shipped with this broken firmware work with OctoPrint.

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/OctoPrint/OctoPrint-FixCBDFirmware/archive/master.zip
