import os
from hue_sdk import Hue
import json

ENV_PATH = "/home/pi/.hue_env"


def write_env(ip, username):
    with open(ENV_PATH, "w") as f:
        f.write("HUE_USERNAME={}\n".format(username))
        f.write("HUE_BRIDGE_IP={}\n".format(ip))

    os.chmod(ENV_PATH, 0o600)


def read_env_file():
    username = None
    ip = None
    with open(ENV_PATH, "r") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            key, value = line.split("=", 1)

            if key == "HUE_BRIDGE_IP":
                ip = value
            elif key == "HUE_USERNAME":
                username = value

    return ip, username


def setup_env():
    ip = None
    username = None

    # check if already existing
    if os.path.exists(ENV_PATH):
        username, ip = read_env_file()
        if username and ip:
            print("Existing ip and username found, skipping env file setup...")
            return username, ip

    # get bridge ip
    ip = Hue.discover()
    if not ip:
        return ip, username

    # sync
    print("Please hit the button on the Hue Bridge, and press ENTER in this terminal.")
    input()

    # register
    username = Hue.register(ip=ip, devicetype="lab_lights#pi")
    if not username:
        return ip, username

    # create env file
    write_env(ip, username)

    return ip, username


def setup_lab_group(ip, username):
    id = None
    if not ip:
        print("Missing bridge IP address, skipping lab group setup")
        return id
    if not username:
        print("Missing username, skipping lab group setup")
        return id

    lab = Hue(username=username, ip=ip)
    id = lab.get_group_id_by_name("Lab")
    if id:
        print("Lab lights group has been setup previously! Ending setup.")
        return id

    print(
        "Please identify which lights to add to the lab group from the options below."
    )
    print(json.dumps(lab.get_lights()))
    lights = list(
        map(int, input("Enter numbers in a comma separated list: ").split(","))
    )
    lights = list(map(str, lights))

    print("Adding lights to new lab group...{}".format(lights))
    r = lab.create_group("Lab", lights=lights)

    id = lab.get_group_id_by_name("Lab")
    return id


def setup():
    ip, username = setup_env()
    id = setup_lab_group(ip, username)

    print("Setup complete!")
    if ip and username:
        print("Bridge IP: {}".format(ip))
        print("Username: {}".format(username))
    else:
        print("FAILED to setup env.")

    if id:
        print("Lab Group Lights ID: {}".format(id))
        print("Service ready to run.")
    else:
        print("FAILED to setup lab group lights")


setup()
