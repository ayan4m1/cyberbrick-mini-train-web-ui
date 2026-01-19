# CyberBrick Multi-Function Core Board

---

This is a project repository for RC controller applications and Timelapse controllers based on the [MicroPython](https://github.com/micropython/micropython) project, which works well on CyberBrick Multi-Function Core Board with Receiver/Transmitter Shield or Timelapse Kit.

This is fun, enjoy it!

## About this repositoty

---

This repository contains the following content:

- [docs/](docs/) -- user documentation in Sphinx reStructuredText format. This is used to generate the online documentation.
- [src/](src/) -- project engineering code, including application code projects for RC and Timelapse.
- [tools/](tools/) -- various tools, currently including visualization tools for advanced control of throttle speed curves in RC applications.

## How to use

---

### Mini Train application

In the `src/app_rc` folder, you can see the code used to implement web control of the Mini Train model. To use it, install Visual Studio Code, and then install the Pymakr extension in VS Code. Connect the Multi-Function Core Board and add the device under the Pymakr tab. Set your WiFi credentials in http_main.py, then connect to your device, use the "Stop Script" action, then "Sync Files to Device," and then reinstall the Core Board in the receiver board. Turn the model on and once you see the device on the network, you can access it over HTTP at its IP address on port 5000.
