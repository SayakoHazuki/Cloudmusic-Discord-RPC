from pypresence import Presence
import psutil
import win32process
import win32gui
import time
import ctypes
import re
import json

GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW


def get_process():
    if "cloudmusic.exe" in (process.name() for process in psutil.process_iter()):
        for proc in psutil.process_iter():
            if proc.name() == "cloudmusic.exe":
                return proc
    else:
        return None


def get_hwnds_for_pid(pid):
    def callback(hwnd, hwnds):
        _, found_pid = win32process.GetWindowThreadProcessId(hwnd)

        if found_pid == pid:
            hwnds.append(hwnd)
        return True
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds


regex_pattern = re.compile("^(.*) - (.*)$")


def get_track_by_hwnds(hwnds):
    for hwnd in hwnds:
        length = GetWindowTextLength(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        regex_match = regex_pattern.match(buff.value)
        if (regex_match):
            track_title = regex_match.group(1)
            track_singer = regex_match.group(2)
            break

    return track_title, track_singer


f = open('config.json')
config = json.load(f)
RPC = Presence(config["appId"])

temp_track_title = "Loading Title..."
temp_track_singer = "Loading Vocalist..."
RPC.connect()
print('Connected to Discord!')
while True:
    process = get_process()
    if (process and process.status() == 'running'):
        track = get_track_by_hwnds(get_hwnds_for_pid(process.pid))
        if(temp_track_title == track[0]):
            pass
        else:
            temp_track_title = track[0]
            temp_track_singer = track[1]
            RPC.update(details=temp_track_title, state=temp_track_singer,
                       large_image="cloudmusic", large_text="cloudmusic",
                       start=int(time.time()))
            print('Track updated - {} // {}'.format(temp_track_title,temp_track_singer))
            time.sleep(15)
        time.sleep(0.2)
