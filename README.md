# CyberBrick Mini Train custom application

This software, when flashed to a CyberBrick Multi-Function Core Board, will convert it into a custom web server for the [CyberBrick Motor Box for Mini Train](https://makerworld.com/en/models/1886257-cyberbrick-motor-box-for-mini-train-diorama). You can control the model from any device with a web browser without the need for a CyberBrick remote transmitter.

To use this:

1. Install [Visual Studio Code](https://code.visualstudio.com/) and [Node.js](https://nodejs.org/en/download/lts).
2. In VS Code, install the [Pymakr extension](https://marketplace.visualstudio.com/items?itemName=pycom.Pymakr).
3. In VS Code, open the `src/app_train` folder.
4. Connect the Multi-Function Core Board and add the device under the Pymakr tab.
5. Set your WiFi credentials in http_main.py.
6. In the Pymakr tab, connect to your device and use the "Stop Script" action, then "Sync Files to Device."
7. Reinstall the Core Board in the receiver board.
8. Turn the model on and wait ~10 seconds for WiFi connection.
9. Once you see the device on the network (its hostname will start with `mpy-` and end with `esp32c3`), you can access it over HTTP at its IP address on port 5000.
10. Use the provided web page to control the train speeds.

To revert back to the original RC application, simply use the CyberBrick app and reflash it when prompted.
