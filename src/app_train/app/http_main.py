# -*-coding:utf-8-*-
#
# The CyberBrick Codebase License, see the file LICENSE for details.
#
# Copyright (c) 2026 ayan4m1 <andrew@bulletlogic.com>
# Portions Copyright (c) 2025 MakerWorld
#

import machine
import time
import ujson
import ulogger
import uasyncio
from gc import collect as garbage_collect
from network import WLAN, STA_IF
from random import random
from sys import path

path.append("/app")
path.append("/bbl")
if '.frozen' in path:
    path.remove('.frozen')
    path.append('.frozen')

from microdot import Microdot
from bbl.leds import LEDController
from bbl.motors import MotorsController
from bbl.servos import ServosController

motors = MotorsController()
servos = ServosController()
leds = LEDController("LED1")

wifi_ssid = 'qux'          # WiFi station ID
wifi_psk = 'changeme'      # WiFi pre-shared key
wifi_hostname = 'motorbox' # Hostname (UI be available at http://motorbox.local)

max_random_delta: int = 100
train_random_speed: list[bool] = [False, False, False, False]
train_reverse: list[bool] = [False, False, False, False]
train_speeds = [0, 0, 0, 0]
update_speed: float = 1
volcano_color: int = 0x000000
volcano_mode: str = 'off'

BLACK_COLOR = 0x000000
BREATHING_EFFECT_SECONDS = 0.02
FIRE_EFFECT_COLOR = 0xf0f000
FIRE_EFFECT_COOLING = 28
FIRE_EFFECT_SECONDS = 0.05
FIRE_EFFECT_SPARK_MAX = 0.65
FIRE_EFFECT_SPARK_MIN = 0.25
FIRE_EFFECT_SPARKING = 32
HTTP_PORT = 80
LED_BITMASK = 0b0001
LED_EFFECT_BREATHE = 2
LED_EFFECT_DURATION = 1000
LED_EFFECT_REPEAT = 255
LED_EFFECT_SOLID = 0
OTHER_EFFECT_SECONDS = 0.5
SPEED_MAX = 100
SPEED_MIN = -100

class Clock(ulogger.BaseClock):
    def __init__(self):
        self.start = time.time()

    def __call__(self) -> str:
        inv = time.time() - self.start
        return '%d' % (inv)

def update_volcano_mode():
    effect = LED_EFFECT_BREATHE if volcano_mode is 'breathing' else LED_EFFECT_SOLID
    color = FIRE_EFFECT_COLOR if volcano_mode in ['breathing', 'solid'] else BLACK_COLOR
    leds.set_led_effect(effect, LED_EFFECT_DURATION, LED_EFFECT_REPEAT, LED_BITMASK, color)

async def main():
    global train_speeds, train_random_speed, train_reverse, update_speed, max_random_delta, volcano_mode

    # get restart cause and initialize logging
    reset_cause = machine.reset_cause()
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
    reset_cause_map = {
        getattr(machine, i): i
        for i in ('PWRON_RESET',
                  'HARD_RESET',
                  'WDT_RESET',
                  'DEEPSLEEP_RESET',
                  'SOFT_RESET')
    }
    reset_cause_string = reset_cause_map.get(reset_cause, str(reset_cause))
    del reset_cause_map
    garbage_collect()

    # log restart cause
    logger.info(f'[MAIN]{reset_cause_string}')

    # load config if one exists
    try:
        with open('train_config', 'r') as f:
            config = ujson.load(f)

            train_speeds = config['speeds']
            train_random_speed = config['random_speed']
            train_reverse = config['reverse']
            update_speed = config['update_speed']
            max_random_delta = config['max_random_delta']
            volcano_mode = config['volcano_mode']
            
            update_volcano_mode()

            del config
            garbage_collect()
    except Exception as e:
        logger.warn(f"[CFG_LOAD]{e}.")

    # connect to WiFi
    wlan = WLAN(STA_IF)
    wlan.active(True)
    while not wlan.isconnected():
        logger.info(f'[WIFI]Connect to {wifi_ssid}...')
        wlan.connect(wifi_ssid, wifi_psk)
        await uasyncio.sleep(5)
    logger.info("[WIFI]Connected!")

    # set up HTTP server
    http_server = Microdot()

    @http_server.route('/')
    async def index(_):
        return f'''
<!DOCTYPE html>
<html>
    <head>
        <title>Motor Box for Mini Train Control</title>
        <script type="text/javascript">
document.addEventListener('DOMContentLoaded', () => {{
    for (let i = 1; i <= 4; i++) {{
        document.querySelector(`#randomize${{i}}`).onclick = () => {{
            document.querySelector(`#speed${{i}}`).readOnly = !document.querySelector(`#speed${{i}}`).readOnly;
            document.querySelector(`#reverse${{i}}`).disabled = !document.querySelector(`#reverse${{i}}`).disabled;
        }};
    }}
}});
        </script>
        <style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');
html {{
    font-family: 'Inter', sans-serif;
    background-color: #3fa7d6;
    color: #fefefe;
}}
body {{
    max-width: 960px;
    margin: 0 auto;
}}
h1 {{
    text-align: center;
    text-shadow: 0 0 4px #fefefe80;
    margin: 8px 0 16px;
}}
button {{
    background-color: #59cd90;
    color: #fefefe;
    border: 1px solid #1b6e8c;
    border-radius: 4px;
    padding: 8px;
}}
        </style>
    </head>
    <body>
        <h1>Motor Box for Mini Train Control</h1>
        <form action="/control" method="POST">
            <p>
                Train 1 @ <input type="number" min="{SPEED_MIN}" max="{SPEED_MAX}" step="5" name="speeds[]" value="{train_speeds[0]}" id="speed1" {'readonly ' if train_random_speed[0] else ''}/>%
                <input type="checkbox" name="randomize[]" value="1" id="randomize1" {'checked ' if train_random_speed[0] else ''}/>
                <label for="randomize1">Randomize</label>
                <input type="checkbox" name="reverse[]" value="1" id="reverse1" {'checked' if train_reverse[0] else ''} {'' if train_random_speed[0] else 'disabled '}/>
                <label for="reverse1">Reverse</label>
            </p>
            <p>
                Train 2 @ <input type="number" min="{SPEED_MIN}" max="{SPEED_MAX}" step="5" name="speeds[]" value="{train_speeds[1]}" id="speed2" {'readonly ' if train_random_speed[1] else ''}/>%
                <input type="checkbox" name="randomize[]" value="2" id="randomize2" {'checked ' if train_random_speed[1] else ''}/>
                <label for="randomize2">Randomize</label>
                <input type="checkbox" name="reverse[]" value="2" id="reverse2" {'checked' if train_reverse[1] else ''} {'' if train_random_speed[1] else 'disabled '}/>
                <label for="reverse2">Reverse</label>
            </p>
            <p>
                Train 3 @ <input type="number" min="{SPEED_MIN}" max="{SPEED_MAX}" step="5" name="speeds[]" value="{train_speeds[2]}" id="speed3" {'readonly ' if train_random_speed[2] else ''}/>%
                <input type="checkbox" name="randomize[]" value="3" id="randomize3" {'checked ' if train_random_speed[2] else ''}/>
                <label for="randomize3">Randomize</label>
                <input type="checkbox" name="reverse[]" value="3" id="reverse3" {'checked' if train_reverse[2] else ''} {'' if train_random_speed[2] else 'disabled '}/>
                <label for="reverse3">Reverse</label>
            </p>
            <p>
                Train 4 @ <input type="number" min="{SPEED_MIN}" max="{SPEED_MAX}" step="5" name="speeds[]" value="{train_speeds[3]}" id="speed4" {'readonly ' if train_random_speed[3] else ''}/>%
                <input type="checkbox" name="randomize[]" value="4" id="randomize4" {'checked ' if train_random_speed[3] else ''}/>
                <label for="randomize4">Randomize</label>
                <input type="checkbox" name="reverse[]" value="4" id="reverse4" {'checked' if train_reverse[3] else ''} {'' if train_random_speed[3] else 'disabled '}/>
                <label for="reverse4">Reverse</label>
            </p>
            <p>
                Volcano Mode:
                <select name="volcanoMode">
                    <option value="off" {'selected ' if volcano_mode is 'off' else ''}>Off</option>
                    <option value="solid" {'selected ' if volcano_mode is 'solid' else ''}>Solid</option>
                    <option value="breathing" {'selected ' if volcano_mode is 'breathing' else ''}>Breathing</option>
                    <option value="erupting" {'selected ' if volcano_mode is 'erupting' else ''}>Erupting</option>
                </select>
            </p>
            <p>
                Random Update Speed: <input type="number" min="0.1" max="3600" step="0.1" name="randomSpeed" value="{update_speed}" /> sec(s)
            </p>
            <p>
                Max Random Delta: <input type="number" min="5" max="100" step="5" name="maxRandomDelta" value="{max_random_delta}" />%
            </p>
            <p><button type="submit">Update</button></p>
        </form>
        <p style="text-align:right;">Model by <a href="https://makerworld.com/en/@BamBamDesign" target="_blank">BamBam Design</a>.</p>
    </body>
</html>
''', 200, { 'Content-Type': 'text/html' }

    @http_server.route('/control', methods=['POST'])
    async def control(request):
        global train_speeds, train_random_speed, update_speed, max_random_delta, volcano_mode

        new_speeds = request.form.getlist('speeds[]')
        new_randoms = request.form.getlist('randomize[]')
        new_reverses = request.form.getlist('reverse[]')
        new_random_speed = request.form.get('randomSpeed')
        new_random_delta = request.form.get('maxRandomDelta')
        new_volcano_mode = request.form.get('volcanoMode')

        for i in range(4):
            train_speeds[i] = min(SPEED_MAX, max(SPEED_MIN, int(new_speeds[i])))
            train_random_speed[i] = True if str(i + 1) in new_randoms else False
            train_reverse[i] = True if str(i + 1) in new_reverses else False

        update_speed = float(new_random_speed)
        max_random_delta = int(new_random_delta)
        volcano_mode = new_volcano_mode

        update_volcano_mode()

        try:
            with open('train_config', 'w') as f:
                config = {
                    'speeds': train_speeds,
                    'random_speed': train_random_speed,
                    'reverse': train_reverse,
                    'update_speed': update_speed,
                    'max_random_delta': max_random_delta,
                    'volcano_mode': volcano_mode
                }
                ujson.dump(config, f)

                del config
                garbage_collect()
        except Exception as e:
            logger.error(f'[CFG_SAVE]{e}')

        return '', 302, { 'Location': '/' }

    async def inner_update():
        global train_speeds

        while True:
            try:
                for i in range(4):
                    # generate random speeds rounded to 5% intervals
                    if train_random_speed[i]:
                        train_speeds[i] = abs(train_speeds[i] + round((random() - 0.5) * 2 * max_random_delta))
                        # if reverse is set, invert speed
                        if train_reverse[i]:
                            train_speeds[i] = train_speeds[i] * -1
                        train_speeds[i] = train_speeds[i] - train_speeds[i] % 5
                    # perform clamping on speed values
                    train_speeds[i] = min(SPEED_MAX, max(SPEED_MIN, train_speeds[i]))

                # set motor and servo speeds
                motors.set_speed(1, round((train_speeds[0] / 1e2) * 2048))
                motors.set_speed(2, round((train_speeds[1] / 1e2) * 2048))
                servos.set_speed(3, train_speeds[2])
                servos.set_speed(4, train_speeds[3])
            except Exception as e:
                logger.error(f'[INLOOP]{e}')
            # wait for the configured interval
            await uasyncio.sleep(update_speed)

    # run update task every {update_speed} seconds
    async def update_task():
        while True:
            try:
                await inner_update()
            except Exception as e:
                logger.error(f'[OUTLOOP]{e}')
                await uasyncio.sleep(1)

    async def led_task():
        global volcano_color

        while True:
            if volcano_mode is 'erupting':
                # cool down first
                volcano_color = volcano_color + int((FIRE_EFFECT_COOLING / 100) * FIRE_EFFECT_COLOR * -1)

                # if sparking, then heat up
                if random() > (FIRE_EFFECT_SPARKING / 100):
                    spark_amount = min(FIRE_EFFECT_SPARK_MAX, random() + FIRE_EFFECT_SPARK_MIN)
                    volcano_color = volcano_color + int(spark_amount * FIRE_EFFECT_COLOR)

                # clamp color from pure fire color to white
                volcano_color = min(FIRE_EFFECT_COLOR, max(0, volcano_color))

                leds.set_led_effect(0, FIRE_EFFECT_SECONDS * 1000, 1, 1, volcano_color)

            # call periodic update function for LED controller
            leds.timing_proc()

            # run LED task as often as needed by selected effect
            if volcano_mode is 'erupting':
                await uasyncio.sleep(FIRE_EFFECT_SECONDS)
            elif volcano_mode is 'breathing':
                await uasyncio.sleep(BREATHING_EFFECT_SECONDS)
            else:
                await uasyncio.sleep(OTHER_EFFECT_SECONDS)

    # start HTTP server
    http_task = uasyncio.create_task(http_server.start_server(port=HTTP_PORT))

    # run HTTP server and update task in parallel
    await uasyncio.gather(http_task, update_task(), led_task())


if __name__ == "__main__":
    uasyncio.run(main())
