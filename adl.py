from urllib.request import urlopen, urlretrieve
from os.path import exists
from os import mkdir, rename, remove
from time import sleep
import io
import subprocess
import sys
import copy
from dataclasses import dataclass

from colorama import Fore, Back, Style

import yt_dlp
from mutagen.mp4 import MP4, MP4Cover
from PIL import Image


LIST_FILE='./list.txt'
MUSIC_DIR='D:/Music'
COOKIES_FILE = "cookies_last.txt"


class Console:
    @staticmethod
    def green(str):
        print(Fore.GREEN + str + Style.RESET_ALL)

    @staticmethod
    def red(str):
        print(Fore.RED + str + Style.RESET_ALL)

    @staticmethod
    def info(str):
        print(Fore.CYAN + f"(i) {str}" + Style.RESET_ALL)


@dataclass
class SongOptions:
    title:  str         = None
    id: str             = None
    album_foldername: str   = None
    album_name: str     = None
    album_id: str       = None
    artist: str         = None
    genre: str          = None
    year: str           = None
    track_number: int   = None
    total_tracks: int   = None

def replace_unallowed_symbols(filename):
    unallowed_symbols = {
        '<': '(',
        '>': ')',
        ':': '-',
        '"': '\'',
        '/': '_',
        '\\': '_',
        '|': '_',
        '?': ';',
        '*': '\''
    }
    replaced_filename = filename

    for symbol, replacement in unallowed_symbols.items():
        replaced_filename = replaced_filename.replace(symbol, replacement)

    return replaced_filename

def get_cover_url(playlist_id):
    with urlopen(f'https://music.youtube.com/playlist?list={playlist_id}') as res:
        body = res.read().decode('utf-8')
        key = '<meta property="og:image" content="'
        body = body[body.index(key)+len(key):]
        body = body[:body.index('">')]
        return body

# Set song's metadata
def process_song(options: SongOptions):
    cover = urlopen(get_cover_url(options.album_id)).read()
    image = Image.open(io.BytesIO(cover))

    with io.BytesIO() as output:
        image.save(output, format="JPEG")
        image_bytes = output.getvalue()
    
    audio_file = MP4(f"{MUSIC_DIR}/{options.album_foldername}/{options.track_number}. {replace_unallowed_symbols(options.title)}.m4a")

    audio_file['covr'] = [
        MP4Cover(image_bytes, imageformat=MP4Cover.FORMAT_JPEG)
    ]


    # Set the artist, album name, and genre
    if options.title  != "Unknown" and options.title != None:
        audio_file['\xa9nam'] = options.title                                   # '\xa9nam' is the tag for the title

    if options.artist != "Unknown" and options.artist != None:
        audio_file['\xa9ART'] = options.artist                                  # '\xa9ART' is the tag for the artist

    if options.album_name:
        audio_file['\xa9alb'] = options.album_name                              # '\xa9alb' is the tag for the album

    if options.genre != "Unknown" and options.genre != None:
        audio_file['\xa9gen'] = options.genre                                   # '\xa9gen' is the tag for the genre
    
    if options.year:
        audio_file['\xa9day'] = options.year                                    # '\xa9day' is the tag for the release date

    if options.track_number and options.total_tracks:
        audio_file['trkn'] = [(options.track_number, options.total_tracks)]     # 'trkn' is the tag for the track number

    audio_file.save()


# Shell Command
def execute_command(command):
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    while True:
        output = process.stdout.readline()
        error = process.stderr.readline()

        if output == '' and error == '' and process.poll() is not None:
            break

        if output:
            print(f"Output: {output.strip()}")

        if error:
            Console.red(f"Error: {error.strip()}")
            exit(1)


    return process.poll()


# Returns song title
def get_song_title(song: SongOptions):
    fetch_opts = {
        'quiet': True,                      # Suppress console output
        'force_generic_extractor': True,    # Use generic extractor for metadata
        'cookiefile': COOKIES_FILE,
    }

    with yt_dlp.YoutubeDL(fetch_opts) as ydl:
        info_dict = ydl.extract_info(f'https://www.youtube.com/watch?v={song.id}', download=False)
        return info_dict.get('title')
    abort()


def download_song(song: SongOptions):
    Console.info(f"Downloading {song.track_number}. {song.title}")

    # Hotfix - yt-dlp cant download from music.youtube with ydl.download (music.youtube is needed because of 141 format 256kbs)
    command_str = f'yt-dlp -f 141 -o "{MUSIC_DIR}/{song.album_foldername}/{song.track_number}. {replace_unallowed_symbols(song.title)}.m4a" "https://music.youtube.com/watch?v={song.id}" --cookies="{COOKIES_FILE}" --quiet'
    execute_command(command_str)

    

    Console.green(f'{song.track_number}. {song.title} downloaded')


def fetch_playlist_video_urls(playlist_url):
    ydl_opts = {
        'extract_flat': True,       # Flatten the playlist
        'quiet': True,              # Suppress output
        'cookiefile': COOKIES_FILE,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(playlist_url, download=False)
        if 'entries' in result:
            video_urls = [entry['url'] for entry in result['entries']]
            return video_urls
    return []

def get_album_name(song: SongOptions):
    ydl_opts = {
        'extract_flat': True,       # Flatten the playlist
        'quiet': True,              # Suppress output
        'cookiefile': COOKIES_FILE,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f'https://www.youtube.com/playlist?list={song.album_id}', download=False)
        return result.get('title', 'Title not found').split(" - ")[1]


def dl_playlist(options: SongOptions):
    album_path = f'{MUSIC_DIR}/{options.album_foldername}'
    if not exists(album_path):
        mkdir(album_path)

    Console.info(f"Fetching {options.album_foldername} album info...")
    video_urls = fetch_playlist_video_urls(f'https://www.youtube.com/playlist?list={options.album_id}')

    Console.info(f"Downloading {options.album_foldername} [{len(video_urls)} songs]\n")
    if video_urls:
        for idx, song_url in enumerate(video_urls, start=1):
            song = copy.deepcopy(options)

            song.id = song_url.split("/watch?v=")[1]
            song.title = get_song_title(song)
            song.track_number = idx
            song.total_tracks = len(video_urls)
            song.album_name = get_album_name(song)

            download_song(song)
            process_song(song)
    else:
        Console.red("No videos found in the playlist.")
        return
    with open(f'{album_path}/.done', 'w') as file:
        pass 
    Console.green(f'{options.album_foldername} has been downloaded.')
    sleep(10)


# True if already downloaded
def check_playlist_download_state(album_folder):
    return exists(f'{MUSIC_DIR}/{album_folder}/.done')

def interprete_list(lines):
    current_artist = "Unknown"
    current_genre  = "Unknown"
    
    for line in lines:
        line_words = line.split(' ')
        # Ignore
        if line_words[0] == '' or line_words[0] == '"': 
            continue
        # Set Artist
        if line_words[0] == "#":
            current_artist = ' '.join(line_words[1:])
            continue
        # Set Genre
        if line_words[0] == "@":
            current_genre = ' '.join(line_words[1:])
            continue
        # Stop
        if line_words[0] == "STOP":
            return
                
        
        # Otherwise download entry
        if not check_playlist_download_state(line_words[0]):
            options = SongOptions(album_foldername=line_words[0], album_id=line_words[1], artist=current_artist, genre=current_genre)

            # Fetch other options from line
            args = []
            if len(line_words) >= 3:
                args = line_words[2:]
                for opt in args:
                    if "year:" in opt:
                        options.year = opt.split(":")[1]

            dl_playlist(options)
        else:
            Console.green(f"{line_words[0]} is already downloaded.")


if __name__ == "__main__":
    with open(LIST_FILE, 'r') as reader:
        lines = reader.read().split('\n')
        interprete_list(lines)
        Console.green("Downloaded all successfully!")

# process_song(f'{MUSIC_DIR}/TOHO_BOSSA_NOVA_1/1. furifuri ojousama.m4a', album_id="OLAK5uy_l06YRyzdC4euFmkFiE8zujhFvyVv2GZTQ", artist_name="ShibayanRecords", album_name="TOHO BOSSA NOVA 1", genre="Bossa Nova", title="furifuri ojousama", track_number=1, total_tracks=10, year="2012")