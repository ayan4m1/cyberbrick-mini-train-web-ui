# -*-coding:utf-8-*-
#
# The CyberBrick Codebase License, see the file LICENSE for details.
#
# Copyright (c) 2025 MakerWorld
#

import sys
import gc
import machine
import uasyncio
import time
import ulogger

sys.path.append("/app")
sys.path.append("/bbl")
if '.frozen' in sys.path:
    sys.path.remove('.frozen')
    sys.path.append('.frozen')

wifi_ssid = 'qux'        # WiFi station ID
wifi_psk = 'changeme'    # WiFi pre-shared key
train_speeds = [0, 0, 0, 0]

from bbl.motors import MotorsController
from bbl.servos import ServosController

motors = MotorsController()
servos = ServosController()

class Clock(ulogger.BaseClock):
    def __init__(self):
        self.start = time.time()

    def __call__(self) -> str:
        inv = time.time() - self.start
        return '%d' % (inv)

async def main():
    rst_c = machine.reset_cause()
    log_clock = Clock()
    log_handler_to_term = ulogger.Handler(
        level=ulogger.INFO,
        colorful=True,
        fmt="&(time)%-&(level)%-&(msg)%",
        clock=log_clock,
        direction=ulogger.TO_TERM,
    )
    log_handler_to_file = ulogger.Handler(
        level=ulogger.INFO,
        fmt="&(time)%-&(level)%-&(msg)%",
        clock=log_clock,
        direction=ulogger.TO_FILE,
        file_name="./log/logging",
        index_file_name="./log/log_index.txt",
        max_file_size=10240
    )
    logger = ulogger.Logger(name=__name__, handlers=(log_handler_to_term, log_handler_to_file))
    rc2str = {
        getattr(machine, i): i
        for i in ('PWRON_RESET',
                  'HARD_RESET',
                  'WDT_RESET',
                  'DEEPSLEEP_RESET',
                  'SOFT_RESET')
    }
    reset_cause = rc2str.get(rst_c, str(rst_c))

    logger.info(f'[MAIN]{reset_cause}')
    del rc2str

    from network import WLAN, STA_IF
    wlan = WLAN(STA_IF)
    wlan.active(True)

    while not wlan.isconnected():
        logger.info("[WIFI]Retry connect")
        wlan.connect(wifi_ssid, wifi_psk)
        await uasyncio.sleep(5)
    logger.info("[WIFI]Connected!")
    gc.collect()

    from microdot import Microdot
    http_server = Microdot()

    @http_server.route('/')
    async def index(request):
        global train_speeds

        return f'''
<!DOCTYPE html>
<html>
    <head>
        <title>Mini Train RC Control</title>
    </head>
    <body>
        <h1>Mini Train RC Control</h1>
        <form action="/control" method="POST">
            <p>Train 1 @ <input type="number" min="-100" max="100" step="5" name="rpmList[]" value="{train_speeds[0]}" />% RPM</p>
            <p>Train 2 @ <input type="number" min="-100" max="100" step="5" name="rpmList[]" value="{train_speeds[1]}" />% RPM</p>
            <p>Train 3 @ <input type="number" min="-100" max="100" step="5" name="rpmList[]" value="{train_speeds[2]}" />% RPM</p>
            <p>Train 4 @ <input type="number" min="-100" max="100" step="5" name="rpmList[]" value="{train_speeds[3]}" />% RPM</p>
            <p><button type="submit">Update</button></p>
        </form>
    </body>
</html>
''', 200, { 'Content-Type': 'text/html' }

    @http_server.route('/control', methods=['POST'])
    async def control(request):
        global train_speeds, motors, servos

        new_speeds = request.form.getlist('rpmList[]')

        train_speeds[0] = int(new_speeds[0])
        train_speeds[1] = int(new_speeds[1])
        train_speeds[2] = int(new_speeds[2])
        train_speeds[3] = int(new_speeds[3])

        motors.set_speed(1, round((train_speeds[0] / 1e2) * 2048))
        motors.set_speed(2, round((train_speeds[1] / 1e2) * 2048))
        servos.set_speed(3, train_speeds[2])
        servos.set_speed(4, train_speeds[3])

        return '', 302, { 'Location': '/' }

    await uasyncio.create_task(http_server.start_server())


if __name__ == "__main__":
    uasyncio.run(main())
