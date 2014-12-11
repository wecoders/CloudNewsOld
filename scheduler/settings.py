import os
import yaml
#database_uri = 'sqlite:///./main.db'
PROJDIR = os.path.abspath(os.path.dirname(__file__))
ROOTDIR = os.path.split(PROJDIR)[0]

database = "mysql://root:admin@localhost/wecoders_com?charset=utf8"
redis_host='localhost'
redis_port=6379


class Settings(dict):
    def __getattr__(self, key):
        if key in self:
            return self[key]
        return None

    def __setattr__(self, key, value):
        self[key] = value

def convert_list(lst):
    new_list = []
    for v in lst:
        new_v = v
        if isinstance(v, dict):
            new_v = convert_dict(v)
        elif isinstance(v, list):
            new_v = convert_list(v)
        new_list.append(new_v)
    return new_list

def convert_dict(d):
    new_dict = Settings()
    for k,v in d.items():
        new_v = v
        if isinstance(v, dict):
            new_v = convert_dict(v)
        elif isinstance(v, list):
            new_v = convert_list(v)
        new_dict[k] = new_v
    return new_dict

def load_config(filename, default_config=None):
    if default_config is None:
        default_config = {}
    stream = file(os.path.join(PROJDIR,filename))
    config = yaml.load(stream)
    default_config.update(config)
    #print config
    settings = Settings(default_config)
    settings = convert_dict(settings)

    return settings

