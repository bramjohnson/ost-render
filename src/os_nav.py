import os
from utils import validate_output_folder, seconds_to_timestamp

def collect_songs(input, decoder):
    songs = []
    # Directory of audio files
    if (os.path.isdir(input)):
        for root, dirs, files in os.walk(input):
            for file in [x for x in files if decoder.supports_file(x)]:
                songs.append(os.path.join(root, file))
    # Playlist file
    elif (os.path.isfile(input) and input.endswith(".m3u8")):
        for line in open(input, 'r').readlines():
            if(os.path.isfile(line)):
                songs.append(line)
    if(len(songs) <= 0):
        print("Input does not contain any audio files.")
        return
    return songs

def tracklist(audio_properties):
    time_in_seconds = 0
    timestamps = {}
    for ap in audio_properties:
        timestamps[time_in_seconds] = f"{ap.get_tag('title')} - {ap.get_tag('artist')}"
        time_in_seconds += ap.length()

    f = open("timestamps.txt", "w", encoding="utf-8")
    for time in timestamps:
        f.write(f"{seconds_to_timestamp(time, time_in_seconds)} - {timestamps[time]}\n")
    f.close()

class SongPathFinder:
    def __init__(self, song) -> None:
        self.song = song

    def output_folder(self, out_folder=None):
        if out_folder is None:
            out_folder = os.path.join(os.getcwd(), "out/")

        folder_name = self.song.folder_name()

        return validate_output_folder(os.path.join(out_folder, folder_name))
    
    def output_path(self, out_folder=""):
        folder_path = self.output_folder(out_folder)
        file_name = self.song.file_name() + '.mp4'

        return os.path.join(folder_path, file_name)