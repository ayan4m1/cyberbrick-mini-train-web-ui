# CyberBrick Mini Train custom application

This software, when flashed to a CyberBrick Multi-Function Core Board, will convert it into a custom web server for the [CyberBrick Motor Box for Mini Train](https://makerworld.com/en/models/1886257-cyberbrick-motor-box-for-mini-train-diorama).

You can control all aspects of the model from any device with a web browser without the need for a CyberBrick remote transmitter. Configuration is saved to flash and loaded on startup, so your settings persist between boots.

## Screenshot

![screenshot of web ui](./docs/screenshot.png)

## Installation

<!-- markdownlint-disable MD029 -->

1. Install [Visual Studio Code](https://code.visualstudio.com/), [Node.js](https://nodejs.org/en/download/lts), and [Git for Windows](https://git-scm.com/install/windows).
2. In VS Code, install the [Pymakr extension](https://marketplace.visualstudio.com/items?itemName=pycom.Pymakr).
3. In VS Code, open the `src/app_train` folder.
4. Remove the Multi-Function Core Board from the model and connect it to your computer. You should see a green LED assuming the RC application has been flashed.
5. Set your WiFi credentials in http_main.py. **NOTE**: The ESP32 only supports 2.4Ghz networks.
6. If you want to have multiple units on a single network, set the hostname to a unique value.
7. Open a terminal in VS Code and run `./build.sh` (if Bash), `build.bat` if cmd, or `.\build.bat` if PowerShell.
8. Click on the Pymakr tab in VS Code.

![the pymakr tab in vs code](./docs/pymakr-tab.png)

9. Click "Add Devices," then check the box for USB Serial Device and click OK.

![the "add devices" button](./docs/pymakr-add-device.png)

10. Click the Connect Device icon.

![the pymakr connect icon](./docs/pymakr-connect.png)

11. If the MFCB LED is solid green, click the "..." menu and select "Stop script."

![the pymakr stop script menu](./docs/pymakr-stop-script.png)

12. The MFCB LED should be flashing purple now. Click the "Sync project to device" icon and wait for the files to copy.

![the pymakr sync project icon](./docs/pymakr-sync.png)

13. Disconnect the MFCB from your computer and reinstall it in the receiver board.
14. Turn the model on and wait ~10 seconds for WiFi connection.
15. Once you see the device on the network, you can access it over HTTP at its IP address or at [http://motorbox.local/](http://motorbox.local/). If you customized the hostname in step 6, use that instead of `motorbox`.
16. Use the provided web page to control the train speeds, direction, update speed, and volcano LED.

## Uninstallation

To revert back to the original RC application, simply use the CyberBrick app to send the Motor Box configuration to the receiver and reflash it when prompted.

## Known Issues

If you submit the form twice at once (i.e. clicking Update twice without waiting for the page to refresh) the web server can become stuck. If so, you will need to turn the model off and back on again.
