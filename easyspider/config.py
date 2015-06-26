# -*- coding: utf-8 -*-
#!/usr/bin/env python

import yaml

class Config(dict):
    def __getattr__(self, key):
        if key in self:
            return self[key]
        return None

    def __setattr__(self, key, value):
        self[key] = value



def import_config(filename, default_config=None):
    if default_config is None:
        default_config = {}
    new_config = {}
    new_config.update(default_config)
    with open(filename) as stream:
        yaml_config = yaml.load(stream)
        print(yaml_config)
        new_config.update(yaml_config)
    #print config
    config = Config(new_config)
    config = convert_config_dict(config)
    
    headers = {}
    if 'headers' in new_config:
        for item in yaml_config['headers']:
            name = item['name']
            value = item['value']
            headers[name] = value
    config.headers = headers
    print(config)
    return config

def convert_config_list(lst):
    new_list = []
    for v in lst:
        new_v = v
        if isinstance(v, dict):
            new_v = convert_config_dict(v)
        elif isinstance(v, list):
            new_v = convert_config_list(v)
        new_list.append(new_v)
    return new_list

def convert_config_dict(d):
    new_dict = Config()
    for k,v in d.items():
        new_v = v
        if isinstance(v, dict):
            new_v = convert_config_dict(v)
        elif isinstance(v, list):
            new_v = convert_config_list(v)
        new_dict[k] = new_v
    return new_dict

