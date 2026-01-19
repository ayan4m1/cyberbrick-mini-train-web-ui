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

To use this:

1. Install [Visual Studio Code](https://code.visualstudio.com/) and [Node.js](https://nodejs.org/en/download/lts).
2. In VS Code, install the [Pymakr extension](https://marketplace.visualstudio.com/items?itemName=pycom.Pymakr).
3. Open the `src/app_train` folder.
4. Connect the Multi-Function Core Board and add the device under the Pymakr tab.
5. Set your WiFi credentials in http_main.py.
6. In the Pymakr tab, connect to your device and use the "Stop Script" action, then "Sync Files to Device."
7. Reinstall the Core Board in the receiver board.
8. Turn the model on and wait ~10 seconds for WiFi connection.
9. Once you see the device on the network, you can access it over HTTP at its IP address on port 5000.
10. Use the provided web page to control the train speeds.
