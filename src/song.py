from render import render_audio_video
from os_nav import SongPathFinder
from PIL import Image
from utils import resize
import io, os

class Song:
    title = "Untitled"
    album = "Untitled"
    artist = "Unknown"
    album_artist = None
    track = "00"
    year = "0000"
    image = None # Should always be a PIL image
    length = 0

    def __init__(self, audio_properties) -> None:
        def populate_tags(self, audio_properties):
            self.title = audio_properties.get_tag("title")
            self.album = audio_properties.get_tag("album")
            self.artist = audio_properties.get_tag("artist")
            self.year = audio_properties.get_tag("date")
            self.track = audio_properties.get_tag("tracknumber")
            try:
                self.album_artist = audio_properties.get_tag('album artist')
            except:
                pass
            try:
                self.image = audio_properties.get_tag("picture")
                self.image = Image.open(io.BytesIO(self.image.data))
            except:
                pass
            self.length = audio_properties.length()
        
        populate_tags(self, audio_properties)
        self.audio_path = audio_properties.path


    # min width/height = 0 means it won't be resized
    def render(self, output, thumbnail=None, min_width=0, min_height=0):
        # Thumbnail
        if thumbnail is not None:
            self.image = Image.open(thumbnail)

        self.image = resize(self.image, min_width, min_height)
        self.image.save("cover.png")
        out_nail = os.path.join(os.getcwd(), "cover.png")

        # Output Location
        song_path_finder = SongPathFinder(self)
        out_path = song_path_finder.output_path(out_folder=output)

        # Render with FFmpeg
        print("Rendering", self.title, "-", self.album + "...")
        self.mp4 = render_audio_video(self.audio_path, out_nail, out_path)

    def folder_name(self):
        artist_used = self.artist
        if self.album_artist is not None:
            artist_used = self.album_artist
        return f"{self.album} - {artist_used} [{self.year}]"
    
    def file_name(self):
        return f"{self.track} - {self.title} - {self.artist}"