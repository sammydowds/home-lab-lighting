import os
from hue_sdk import Hue
from gpiozero import MotionSensor
import time

USERNAME = os.getenv("HUE_USERNAME")
IP = os.getenv("HUE_BRIDGE_IP")
TIMEOUT = 1800  # 30 minutes

if not IP and not USERNAME:
    raise Exception(
        "Missing env variables: HUE_USERNAME and HUE_BRIDGE_API. Please run setup_hue_env.py"
    )

pir = MotionSensor(4)

lab = Hue(username=USERNAME, ip=IP)
last_motion = 0
lights_on = False

while True:
    if pir.motion_detected:
        last_motion = time.time()

        if not lights_on:
            lab.group_action(name="Lab", action={"on": True})
            lights_on = True

    if lights_on and (time.time() - last_motion > TIMEOUT):
        lab.group_action(name="Lab", action={"on": False})
        lights_on = False

    time.sleep(1)
