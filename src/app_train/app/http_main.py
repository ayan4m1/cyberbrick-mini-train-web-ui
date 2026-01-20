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
from random import random

sys.path.append("/app")
sys.path.append("/bbl")
if '.frozen' in sys.path:
    sys.path.remove('.frozen')
    sys.path.append('.frozen')

wifi_ssid = 'qux'        # WiFi station ID
wifi_psk = 'changeme'    # WiFi pre-shared key
train_speeds = [0, 0, 0, 0]
train_random_speed = [False, False, False, False]
update_speed = 1

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
        global train_speeds, train_random_speed, update_speed

        return f'''
<!DOCTYPE html>
<html>
    <head>
        <title>Mini Train RC Control</title>
        <script type="text/javascript">
document.addEventListener('DOMContentLoaded', () => {{
    for (let i = 1; i <= 4; i++) {{
        document.querySelector(`#randomize${{i}}`).onclick = () => {{
            document.querySelector(`#rpm${{i}}`).readOnly = !document.querySelector(`#rpm${{i}}`).readOnly;
        }};
    }}
}});
        </script>
    </head>
    <body>
        <h1>Mini Train RC Control</h1>
        <form action="/control" method="POST">
            <p>
                Train 1 @ <input type="number" min="-100" max="100" step="5" name="rpmList[]" value="{train_speeds[0]}" id="rpm1" />% RPM
                <input type="checkbox" name="randomize[]" value="1" id="randomize1" {'checked' if train_random_speed[0] else ''}/>
                <label for="randomize1">Randomize</label>
            </p>
            <p>
                Train 2 @ <input type="number" min="-100" max="100" step="5" name="rpmList[]" value="{train_speeds[1]}" id="rpm2" />% RPM
                <input type="checkbox" name="randomize[]" value="2" id="randomize2" {'checked' if train_random_speed[1] else ''}/>
                <label for="randomize2">Randomize</label>
            </p>
            <p>
                Train 3 @ <input type="number" min="-100" max="100" step="5" name="rpmList[]" value="{train_speeds[2]}" id="rpm3" />% RPM
                <input type="checkbox" name="randomize[]" value="3" id="randomize3" {'checked' if train_random_speed[2] else ''}/>
                <label for="randomize3">Randomize</label>
            </p>
            <p>
                Train 4 @ <input type="number" min="-100" max="100" step="5" name="rpmList[]" value="{train_speeds[3]}" id="rpm4" />% RPM
                <input type="checkbox" name="randomize[]" value="4" id="randomize4" {'checked' if train_random_speed[3] else ''}/>
                <label for="randomize4">Randomize</label>
            </p>
            <p>
                Random Update Speed: <input type="number" min="0" max="180" step="0.1" name="randomSpeed" value="{update_speed}" /> secs
            </p>
            <p><button type="submit">Update</button></p>
        </form>
    </body>
</html>
''', 200, { 'Content-Type': 'text/html' }

    @http_server.route('/control', methods=['POST'])
    async def control(request):
        global train_speeds, train_random_speed, update_speed

        new_speeds = request.form.getlist('rpmList[]')
        new_randoms = request.form.getlist('randomize[]')
        new_random_speed = request.form.get('randomSpeed')

        train_speeds[0] = int(new_speeds[0])
        train_speeds[1] = int(new_speeds[1])
        train_speeds[2] = int(new_speeds[2])
        train_speeds[3] = int(new_speeds[3])

        if train_speeds[0] < -100 or train_speeds[0] > 100:
            return 'Invalid speed for train 1!'
        if train_speeds[1] < -100 or train_speeds[1] > 100:
            return 'Invalid speed for train 2!'
        if train_speeds[2] < -100 or train_speeds[2] > 100:
            return 'Invalid speed for train 3!'
        if train_speeds[3] < -100 or train_speeds[3] > 100:
            return 'Invalid speed for train 4!'

        train_random_speed[0] = True if '1' in new_randoms else False
        train_random_speed[1] = True if '2' in new_randoms else False
        train_random_speed[2] = True if '3' in new_randoms else False
        train_random_speed[3] = True if '4' in new_randoms else False

        update_speed = float(new_random_speed)

        return '', 302, { 'Location': '/' }

    http_task = uasyncio.create_task(http_server.start_server(port=80))

    async def update_task():
        global update_speed, train_random_speed, train_speeds, motors, servos

        while True:
            try:
                if train_random_speed[0]:
                    train_speeds[0] = round(random() * 100)
                    train_speeds[0] = train_speeds[0] - train_speeds[0] % 5
                if train_random_speed[1]:
                    train_speeds[1] = round(random() * 100)
                    train_speeds[1] = train_speeds[1] - train_speeds[1] % 5
                if train_random_speed[2]:
                    train_speeds[2] = round(random() * 100)
                    train_speeds[2] = train_speeds[2] - train_speeds[2] % 5
                if train_random_speed[3]:
                    train_speeds[3] = round(random() * 100)
                    train_speeds[3] = train_speeds[3] - train_speeds[3] % 5

                motors.set_speed(1, round((train_speeds[0] / 1e2) * 2048))
                motors.set_speed(2, round((train_speeds[1] / 1e2) * 2048))
                servos.set_speed(3, train_speeds[2])
                servos.set_speed(4, train_speeds[3])
            except Exception as e:
                logger.error(f'[MAIN]{e}')
            await uasyncio.sleep(update_speed)

    await uasyncio.gather(http_task, update_task())


if __name__ == "__main__":
    uasyncio.run(main())
