from decode import DecodeAudio, AudioProperties, TranslateAudio
from os_nav import collect_songs, tracklist, SongPathFinder
from song import Song
from render import combine
import argparse, shutil, os


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
decoder = DecodeAudio()
translator = TranslateAudio()

# Collect valid paths
song_paths = collect_songs(args.input, decoder)

# Collect & transform ID3 tags
audio_properties = [AudioProperties(path, decoder=decoder, translator=translator) for path in song_paths]

# Convert to song object; prepared for rendering
songs = [Song(ap) for ap in audio_properties]

# Render songs individually (will delete later if individual is false)
[song.render(args.output, args.thumbnail, args.min_width, args.min_height) for song in songs]

# Render songs for longplay
if args.longplay:
    longplay = combine(songs, args.thumbnail, args.output)

    # Print tracklist for longplay
    tracklist(audio_properties)

    # Move to out_folder
    shutil.move("timestamps.txt", os.path.join(SongPathFinder(songs[0]).output_folder(), "timestamps.txt"))

print(song_paths)