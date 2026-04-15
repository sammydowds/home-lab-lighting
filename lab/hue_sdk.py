import requests
import json


class Hue:
    def __init__(self, username, ip):
        self.username = username
        self.bridge_ip = ip

    @staticmethod
    def discover():
        r = requests.get("http://discovery.meethue.com")

        if r.ok:
            data = r.json()

            # discovery returns a LIST, not a dict
            if isinstance(data, list) and len(data) > 0:
                ip = data[0].get("internalipaddress")
                if ip:
                    print("Bridge IP address: {}".format(ip))
                    return ip

        return None

    @staticmethod
    def register(ip, devicetype):
        payload = json.dumps({"devicetype": devicetype})
        headers = {"Content-Type": "application/json"}

        r = requests.post("http://{}/api".format(ip), data=payload, headers=headers)

        if r.ok:
            data = r.json()

            if isinstance(data, list) and len(data) > 0:
                if "success" in data[0] and "username" in data[0]["success"]:
                    username = data[0]["success"]["username"]
                    print(
                        "Registration successful. Please store this username for future use: {}".format(
                            username
                        )
                    )
                    return username

        return None

    def put(self, uri, data):
        headers = {"Content-Type": "application/json"}
        r = requests.put(
            "http://{}/api/{}{}".format(self.bridge_ip, self.username, uri),
            data=data,
            headers=headers,
        )
        return r.json()

    def post(self, data, uri):
        headers = {"Content-Type": "application/json"}
        r = requests.post(
            "http://{}/api/{}{}".format(self.bridge_ip, self.username, uri),
            data=data,
            headers=headers,
        )
        return r.json()

    def get(self, uri):
        r = requests.get(
            "http://{}/api/{}{}".format(self.bridge_ip, self.username, uri)
        )
        return r.json()

    def get_lights(self):
        return self.get("/lights")

    def get_groups(self):
        return self.get("/groups")

    def create_group(self, name, type="Room", groupClass="Office", lights=None):
        if lights is None:
            lights = []

        payload = json.dumps(
            {"name": name, "type": type, "class": groupClass, "lights": lights}
        )

        return self.post(uri="/groups", data=payload)

    def get_group_id_by_name(self, name):
        groups = self.get_groups()

        if not groups:
            return None

        for group_id, group in groups.items():
            if group.get("name", "").lower() == name.lower():
                return group_id

        print("Warning: group name ({}) not found!".format(name))
        return None

    def group_action(self, name, action=None):
        if action is None:
            action = {"on": True}

        group_number = self.get_group_id_by_name(name=name)
        if not group_number:
            print("Failed to complete action.")
            return None

        payload = json.dumps(action)
        return self.put(uri="/groups/{}/action".format(group_number), data=payload)
