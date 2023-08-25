import os
import subprocess
from subprocess import CREATE_NO_WINDOW, PIPE
from os_nav import SongPathFinder
from utils import generate_concat_file

# Render single mp3 to mp4
def render_audio_video(audio, video, out):
    if (os.path.exists(out)):
        return out
    p = subprocess.Popen(
            ['ffmpeg', '-y', '-loop', '1', '-framerate', '5', '-i', video, '-i', audio, '-c:v', 'libx264',
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

# Combine Song objects using ffmpeg
def combine(songs, thumbnail, out):
    sample_song = songs[0]
    out_file = os.path.join(SongPathFinder(sample_song).output_folder(out),f'{sample_song.folder_name()}.mp4')
    # Need to change validate render path for this
    if (os.path.exists(out_file)):
        return out_file
    
    generate_concat_file([song.mp4 for song in songs])

    p = subprocess.Popen(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', "concat.txt", out_file],
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

# Combine multiple files using ffmpeg
def concat(files, out):
    if (os.path.exists(out)):
        return out
    
    p = subprocess.Popen(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', files, out],
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