import math
import os
import time

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

def validate_output(output):
    pass

def validate_output_folder(out_folder = None):
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)
    return out_folder

def seconds_to_timestamp(time_in_seconds, total_in_seconds=0):
    strftime_string = "%S"
    if total_in_seconds > 60:
        strftime_string = "%M:" + strftime_string
    if total_in_seconds > 3600:
        strftime_string = "%H:" + strftime_string

    print(strftime_string)

    return time.strftime(strftime_string, time.gmtime(time_in_seconds))

def generate_concat_file(files):
    entries = []
    for file in files:      
        entry = 'file ' + '\''
        entry += (file).replace("\'", "\'\\\'\'")
        entry += '\'\n'
        entries.append(entry)
    f = open("concat.txt", "w", encoding='utf-8')
    f.writelines(entries)
    f.close()
    return "concat.txt"