import os
import json
import pkg_resources

root_dir = os.path.dirname(os.path.abspath(__file__))

data_path = pkg_resources.resource_filename('ideas4eo', 'config.json')
with open(data_path) as json_data:
    config_data = json.load(json_data)

nasa_laads_daac_token = config_data['nasa_laads_daac_token']
media_path = config_data['media_path']
