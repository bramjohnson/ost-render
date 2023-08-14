import mutagen.flac as FLAC
import mutagen.mp3 as MP3
from mutagen.id3 import ID3
import os

FLAC_EXAMPLE = "E:\\itzst\\FLAC Backups\\1989 - Jang Pil-Soon 1\\1.07. 내 마음 언제까지나.flac"
MP3_EXAMPLE = "E:\\itzst\\Music\\Alternative\\peppermint lounge\\1998 - peppermint lounge\\06 - attributes.mp3"

### --- Decode ---

# dictionary of tags
def decode_mp3(song_path):
    audio = MP3.MP3(song_path)
    return audio

def decode_flac(song_path):
    audio = FLAC.FLAC(song_path)
    return audio

class DecodedFLAC:
    def __init__(self, song_path) -> None:
        self.path = song_path
        self.audio = FLAC.FLAC(song_path)

    def get_tag(self, tagname):
        if tagname not in self.audio.keys():
            raise Exception("Tag does not exist in keys")

        return self.audio[tagname][0]
    
    def length(self):
        return self.audio.info.length

class DecodedMP3:
    def __init__(self, song_path) -> None:
        self.path = song_path
        self.audio = MP3.MP3(song_path)

    def get_tag(self, tagname):
        if tagname not in self.audio.keys():
            raise Exception("Tag does not exist in keys")
        
        if tagname == 'APIC:':
            return self.audio[tagname]

        return self.audio[tagname].text[0]
    
    def length(self):
        return self.audio.info.length

class DecodeAudio:
    decoders = {
        '.mp3':DecodedMP3,
        '.flac':DecodedFLAC,
    }

    # Returns a dict wrapped in the fileformat
    def decode(self, path):
        path_extension = os.path.splitext(path)[1]
        audio = self.decoders[path_extension](path)
        return audio
    
    def supports_file(self, path):
        path_extension = os.path.splitext(path)[1]
        return path_extension in self.decoders.keys()
    
### --- Translators ---

class TranslateAudio:
    translations = {
        'TDRC':'date',
        'TRCK':'tracknumber',
        'APIC:':'picture',
        'TCOM':'comment',
        'TXXX:replaygain_track_gain':'replaygain_track_gain',
        'TXXX:replaygain_track_peak':'replaygain_track_peak',
        'TIT2':'title',
        'TALB':'album',
        'TCON':'genre',
        'TPE1':'artist',
        'TPE2':'album artist'
    }

    def translate(self, decoded_audio):
        tags = {}
        for key in decoded_audio.audio.keys():
            new_key = key
            if key in self.translations.keys():
                new_key = self.translations[key]

            tags[new_key] = decoded_audio.get_tag(key)
        return tags


### --- AudioProperties --- 

class AudioProperties:
    def __init__(self, path, decoder=DecodeAudio(), translator=TranslateAudio()) -> None:
        self.path = path
        self.tags = dict()
        self.decoder = decoder
        self.translator = translator

        self.decoded_audio = self.decoder.decode(path)
        self.translated_tags = self.translator.translate(self.decoded_audio)

    def get_tags(self):
        return self.translated_tags.keys()
    
    def get_tag(self, tagname):
        try:
            return self.translated_tags[tagname]
        except:
            raise Exception(f"{tagname} not in tags")
        
    def length(self):
        return self.decoded_audio.length()

# print(AudioProperties(FLAC_EXAMPLE).get_tag('comment'))
# print(AudioProperties(MP3_EXAMPLE).get_tag('comment'))