import alldebrid as ad
import pprint as pp
import json

def get_config():
    config = json.load(open('config.json'))
    return config["user"], config["password"], config["dl_folder"]

user, pw, fol = get_config()
handle = ad.alldebrid(user, pw, dl_folder=fol)
handle.connect()
handle.sync()


