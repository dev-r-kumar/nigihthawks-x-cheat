import json
import os


class InitData:
    def __init__(self):
         # load configs from json file
        self.configuration_file = os.path.join(os.path.dirname(__file__), "static", "configuration.json")
        with open(self.configuration_file, 'r') as config_file:
            self.data = json.load(config_file)

    def write_data(self, data):
        with open(self.configuration_file, 'w') as config_file:
            json.dump(data, config_file, indent=2)


    def load_defaults(self):
        return self.data


class NighthawhsServerConfig:
    def __init__(self, server_status=None):
        data = InitData().load_defaults()
        # init server configs
        self.server_status = server_status or data['server_config']['server_status']


    def update(self):
        init = InitData()
        data = init.load_defaults()
        data['server_config']['server_status'] = self.server_status 
        init.write_data(data)


class NighthawksPanelConfig:
    def __init__(self, scan_pattern = None, write_offset = None, head_offset = None, left_ear_offset = None, right_ear_offset = None, left_shoulder_offset = None, right_shoulder_offset = None):
        # load defaults
        data = InitData().load_defaults()

        # init panel configs
        self.scan_pattern = scan_pattern or data['apps'][0]['configs'][0]['scan_pattern']
        self.write_offset = write_offset or data['apps'][0]['configs'][0]['write_offset']
        self.head_offset = head_offset  or data['apps'][0]['configs'][0]['head_offset']
        self.left_ear_offset = left_ear_offset or data['apps'][0]['configs'][0]['left_ear_offset']
        self.right_ear_offset = right_ear_offset or data['apps'][0]['configs'][0]['right_ear_offset']
        self.left_shoulder_offset = left_shoulder_offset or data['apps'][0]['configs'][0]['left_shoulder_offset']
        self.right_shoulder_offset = right_shoulder_offset or data['apps'][0]['configs'][0]['right_shoulder_offset']


    def update(self):
        init = InitData()
        data = init.load_defaults()
        data['apps'][0]['configs'][0]['scan_pattern'] = self.scan_pattern 
        data['apps'][0]['configs'][0]['write_offset'] = self.write_offset 
        data['apps'][0]['configs'][0]['head_offset'] = self.head_offset 
        data['apps'][0]['configs'][0]['left_ear_offset'] = self.left_ear_offset 
        data['apps'][0]['configs'][0]['right_ear_offset'] = self.right_shoulder_offset 
        data['apps'][0]['configs'][0]['left_shoulder_offset'] = self.left_shoulder_offset
        data['apps'][0]['configs'][0]['right_shoulder_offset'] = self.right_shoulder_offset
        init.write_data(data)



class NighthawksUIDBypass:
    def __init__(self, access_password = None):
        data = InitData().load_defaults()
        # init uid bypass configs
        self.access_password = access_password or data['apps'][1]['configs'][0]['access_password']

    def update(self):
        init = InitData()
        data = init.load_defaults()
        data['apps'][1]['configs'][0]['access_password'] = self.access_password
        init.write_data(data)


class NighthawksDisocrdBot:
    def __init__(self, token = None):
        data = InitData().load_defaults()

        # init discord config
        self.token = token or data['apps'][2]['configs'][0]['token']

    def update(self):
        init = InitData()
        data = init.load_defaults()
        data['apps'][2]['configs'][0]['token'] = self.token
        init.write_data(data)


class NhkSniperConfig:
    def __init__(self, scan_pattern = None, replace_pattern = None):
        data = InitData().load_defaults()

        self.scan_pattern = scan_pattern or data['apps'][0]['configs'][0]['sniper_fov_scan']
        self.replace_pattern = replace_pattern or data['apps'][0]['configs'][0]['sniper_fov_replace']


    def update(self):
        init = InitData()
        data = init.load_defaults()

        data['apps'][0]['configs'][0]['sniper_fov_scan'] = self.scan_pattern
        data['apps'][0]['configs'][0]['sniper_fov_replace'] = self.replace_pattern
        init.write_data(data)

        