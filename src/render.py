import os
import argparse
import io
from time import sleep
from mutagen.id3 import ID3
import pyautogui
import subprocess
from subprocess import CREATE_NO_WINDOW, PIPE
from PIL import Image
import math

# Final vars
MIN_WIDTH = 1920 #px
MIN_HEIGHT = 1080 #px
INDIVIDUAL = True
LONGPLAY = False

# Initialize parse
parser = argparse.ArgumentParser(description="Upload OST to YouTube.")
parser.add_argument("-t", "--thumbnail", help="Makes the image for the video THUMBNAIL", type=str)
parser.add_argument("-i", "--input", help="Path of directory, playlist, or session file", type=str, required=True)
parser.add_argument("-o", "--output", help="Path of directory to output files to", type=str)
parser.add_argument("--min-width", help=f"Minimum width for the thumbnail ({MIN_WIDTH}px default)", type=int, default=MIN_WIDTH)
parser.add_argument("--min-height", help=f"Minimum height for the thumbnail ({MIN_HEIGHT}px default)", type=int, default=MIN_HEIGHT)
parser.add_argument("--individual", help=f"Renders tracks individually to their own respective mp4 file ({INDIVIDUAL} default)", type=bool, default=INDIVIDUAL)
parser.add_argument("--longplay", help=f"Renders tracks individually to their own respective mp4 file ({LONGPLAY} default)", type=bool, default=LONGPLAY)

# Initailize args
args = parser.parse_args()

class Song:
    title = "Undefined"
    album = "Undefined"
    year = "0000"
    image = None

    def __init__(self, song_path, thumbnail, output) -> None:
        audio = ID3(song_path)
        self.image = thumbnail
        if "TALB" in audio.keys():
            self.album = audio["TALB"].text[0]
        if "TDRC" in audio.keys():
            self.year = audio["TDRC"].text[0]
        if "TIT2" in audio.keys(): 
            self.title = audio["TIT2"].text[0]
        if "APIC:" in audio.keys():
            bytes_image = audio["APIC:"].data
            pil_image = Image.open(io.BytesIO(bytes_image))

            pil_image = resize(pil_image, args.min_width, args.min_height)
            pil_image.save("cover.png")

            self.image = os.path.join(os.getcwd(), "cover.png")
        print("Rendering", self.title, "-", self.album + "...")
        print(self.image)
        self.mp4 = render(song_path, self.image, validate_render_path(song_path, output))

# Returns an image with the required minimum width/height
def resize(image, min_width, min_height):
    # Calculate 720p sizes
    new_width = image.height
    new_height = image.width

    # if less, increase height by same factor
    if new_width < min_width:
        new_height = (min_width / new_width) * new_height # height first to maintain (width vs new_width) diff
        new_width = min_width

    # if still less, increase width by same factor
    if new_height < min_height:
        new_width = (min_height / new_height) * new_width # width first to maintain (height vs new_height) diff
        new_height = min_height
    
    return image.resize((math.ceil(new_width), math.ceil(new_height)))
        
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

# Render single mp3 to mp4
def render(song_path, thumbnail, out):
    if (os.path.exists(out)):
        return out
    p = subprocess.Popen(
            ['ffmpeg', '-y', '-loop', '1', '-framerate', '5', '-i', thumbnail, '-i', song_path, '-c:v', 'libx264',
            '-tune', 'stillimage', '-c:a', 'aac', '-b:v', "4000k", '-b:a', "320k", '-pix_fmt',
            'yuv420p', '-vf', 'crop=trunc(iw/2)*2:trunc(ih/2)*2', '-movflags', '+faststart', '-shortest', '-fflags',
            '+shortest', '-max_interleave_delta', '100M', out], stdout=PIPE, stderr=subprocess.STDOUT, creationflags=CREATE_NO_WINDOW, universal_newlines=True)
    # I don't know why you need to open it like this, it won't work without the utf-8 encoding ):<
    for line in open(p.stdout.name, 'r', encoding='utf-8'):
        string_line = str(line)
        if "time=" in string_line:
            time = string_line[string_line.index("time=") + 6:string_line.index("bitrate=") - 1]
            h, m, s = time.split(':')
            s, ms = s.split('.')
        # print(string_line)
    return out

# Combine multiple files using ffmpeg
def combine(songs, thumbnail, out):
    # Need to change validate render path for this
    # if (os.path.exists(out)):
    #     return out
    entries = []
    for filename in songs:
        print(filename)
        print(songs[filename].mp4)
        
        entry = 'file ' + '\''
        entry += (songs[filename].mp4).replace("\'", "\'\\\'\'")
        entry += '\'\n'
        entries.append(entry)
    f = open("concat.txt", "w", encoding='utf-8')
    f.writelines(entries)
    f.close()
    sample_song = list(songs.values())[0]
    p = subprocess.Popen(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', "concat.txt", os.path.join(validate_output_folder(sample_song),f'{sample_song.year} - {sample_song.album}.mp4')],
                         stdin=subprocess.PIPE, stderr=subprocess.STDOUT, stdout=PIPE, creationflags=CREATE_NO_WINDOW,
                         universal_newlines=True)
    # I don't know why you need to open it like this, it won't work without the utf-8 encoding ):<
    for line in open(p.stdout.name, 'r', encoding='utf-8'):
        string_line = str(line)
        if "time=" in string_line:
            time = string_line[string_line.index("time=") + 6:string_line.index("bitrate=") - 1]
            h, m, s = time.split(':')
            s, ms = s.split('.')
        # print(string_line)
    return out

def validate_output_folder(song, out_folder = None):
    if out_folder is None:
        out_folder = f"{song.year} - {song.album}"
        out_folder = os.path.join(os.getcwd(), "out/", out_folder)
    if not os.path.exists(os.path.join(os.getcwd(), "out/", out_folder)):
        os.mkdir(os.path.join(os.getcwd(), "out/", out_folder))
    return out_folder

def validate_render_path(song_path, out_folder = None):
    output = ""
    if out_folder is None:
        out_folder = os.path.basename(os.path.dirname(song_path))
        out_folder = os.path.join(os.getcwd(), "out/", out_folder)
    output = os.path.join(out_folder, os.path.basename(song_path)[:-4] + '.mp4')
    if not os.path.exists(os.path.join(os.getcwd(), "out/", out_folder)):
        os.mkdir(os.path.join(os.getcwd(), "out/", out_folder))
    print(output)
    return output

songs = add(args.input, args.thumbnail, args.output)
print(songs)
lonplay = combine(songs, args.thumbnail, args.output)