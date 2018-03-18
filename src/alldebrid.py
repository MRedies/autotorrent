import requests
import pprint as pp
from subprocess import call
import os.path


class alldebrid:
    username  = ""
    password  = ""
    token     = ""
    connected = False
    dl_folder = ""

    def __init__(self, username, password, dl_folder="./"):
        self.username  = username
        self.password  = password
        self.dl_folder = dl_folder

    def connect(self):
        req_url = "https://api.alldebrid.com/user/login?agent=mySoft&username={}&password={}".format(self.username, self.password)
        r = requests.get(req_url)
        answer = r.json()

        self.connected = answer["success"]
        self.token     = answer["token"]

    def get_torrents(self):
        req_url = "https://api.alldebrid.com/user/torrents?agent=mySoft&token={}".format(self.token)
        r = requests.get(req_url).json()
        if r["success"]:
            return r["torrents"]
        else:
            raise Exception("couldn't get torrents")

        
    def get_largest_idx(self, torrent):
        max_sz   = 0
        max_idx  = -1

        for idx, link in enumerate(torrent["link"]):
            req_url = "https://api.alldebrid.com/link/unlock?agent=mySoft&token={}&link={}".format(self.token, link)
            r = requests.get(req_url).json()
            if r["success"]:
                if(r["infos"]["filesize"] > max_sz):
                    max_sz  = r["infos"]["filesize"]
                    max_idx = idx
            else:
                raise Exception("couldn't get link")
        return max_idx

    def download_largest(self, torrent):
        max_idx = self.get_largest_idx(torrent)
        req_url  = "https://api.alldebrid.com/link/unlock?agent=mySoft&token={}&link={}".format(self.token, torrent["link"][max_idx])
        r        = requests.get(req_url).json()
        link     = r["infos"]["link"]
        filename = r["infos"]["filename"]

        call(['wget', '-O', self.dl_folder + filename, link])

    def largest_filename(self, torrent):
        max_idx = self.get_largest_idx(torrent)

        req_url = "https://api.alldebrid.com/link/unlock?agent=mySoft&token={}&link={}".format(self.token, torrent["link"][max_idx])
        r = requests.get(req_url).json()
        return r["infos"]["filename"]


    def sync(self):
        for torr in self.get_torrents():
            if(torr["statusCode"] == 4):
                filename = self.largest_filename(torr)
                if(not(os.path.exists(self.dl_folder + filename))):
                    self.download_largest(torr)
                else:
                    print("{} already downloaded".format(filename))
        
