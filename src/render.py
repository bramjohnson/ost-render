import os
import argparse
from time import sleep
from mutagen.id3 import ID3
import pyautogui
import subprocess
from subprocess import CREATE_NO_WINDOW, PIPE

# Initialize parse
parser = argparse.ArgumentParser(description="Upload OST to YouTube.")
parser.add_argument("-t", "--thumbnail", help="Makes the image for the video THUMBNAIL", type=str)
parser.add_argument("-i", "--input", help="Path of directory, playlist, or session file", type=str, required=True)
parser.add_argument("-o", "--output", help="Path of directory to output files to", type=str)

# Initailize args
args = parser.parse_args()

class Song:
    title = "Undefined"
    album = "Undefined"

    def __init__(self, song_path, thumbnail, output) -> None:
        audio = ID3(song_path)
        if "TALB" in audio.keys():
            self.album = audio["TALB"].text[0]
        if "TIT2" in audio.keys(): 
            self.title = audio["TIT2"].text[0]
        print("Rendering", self.title, "-", self.album + "...")
        self.mp4 = render(song_path, thumbnail, validate_render_path(song_path, output))
        
def add(input, thumbnail, output):
    songs = []
    # Directory of audio files
    if (os.path.isdir(input)):
        for root, dirs, files in os.walk(input):
            for file in [x for x in files if x.endswith('.mp3')]:
                songs.append(os.path.join(root, file))
    # Playlist file
    elif (os.path.isfile(input) and input.endswith(".m3u8")):
        for line in open(input, 'r').readlines():
            if(os.path.isfile(line)):
                songs.append(line)
    # OST file (unfinished)
    elif (os.path.isfile(input) and input.endswith(".ost")):
        pass
    if(len(songs) <= 0):
        print("Input does not contain any audio files.")
        return
    db = dict()
    for song in songs:
        db[song] = Song(song, thumbnail, output)
    return db


def render(song_path, thumbnail, out):
    print(out)
    if (os.path.exists(out)):
        return out
    p = subprocess.Popen(
            ['ffmpeg', '-y', '-loop', '1', '-framerate', '5', '-i', thumbnail, '-i', song_path, '-c:v', 'libx264',
            '-tune', 'stillimage', '-c:a', 'aac', '-b:v', "4000k", '-b:a', "320k", '-pix_fmt',
            'yuv420p', '-vf', 'crop=trunc(iw/2)*2:trunc(ih/2)*2', '-movflags', '+faststart', '-shortest', '-fflags',
            '+shortest', '-max_interleave_delta', '100M', out], stdout=PIPE, stderr=subprocess.STDOUT, creationflags=CREATE_NO_WINDOW, universal_newlines=True)
    for line in p.stdout:
        string_line = str(line)
        if "time=" in string_line:
            time = string_line[string_line.index("time=") + 6:string_line.index("bitrate=") - 1]
            h, m, s = time.split(':')
            s, ms = s.split('.')
    return out

def validate_render_path(song_path, out_folder = None):
    output = ""
    if out_folder is None:
        out_folder = os.path.basename(os.path.dirname(song_path))
        output = os.path.join(os.getcwd(), "out/", out_folder)
    output = os.path.join(out_folder, os.path.basename(song_path)[:-4] + '.mp4')
    if not os.path.exists(os.path.join(os.getcwd(), "out/", out_folder)):
        os.mkdir(os.path.join(os.getcwd(), "out/", out_folder))
    return output

songs = add(args.input, args.thumbnail, args.output)