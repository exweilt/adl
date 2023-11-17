# import youtube_dl
# import eyed3
# from pytube import YouTube, Playlist

from urllib.request import urlopen, urlretrieve
from os.path import exists
from os import mkdir, rename, remove
from colorama import Fore, Back, Style
from time import sleep
import os
import subprocess
import sys
from PIL import Image
from mutagen.mp4 import MP4, MP4Cover
import io
import yt_dlp

# eyed3.log.setLevel("ERROR")

LIST_FILE='.\\list.txt'
MUSIC_DIR='D:\\Music'

COOKIES_FILE = "cookies_last.txt"


def green(str):
    print(Fore.GREEN + str + Style.RESET_ALL)


def red(str):
    print(Fore.RED + str + Style.RESET_ALL)


def info(str):
    print(Fore.CYAN + f"(i) {str}" + Style.RESET_ALL)


def getCoverUrl(playlistId):
    with urlopen(f'https://music.youtube.com/playlist?list={playlistId}') as res:
        body = res.read().decode('utf-8')
        key = '<meta property="og:image" content="'
        body = body[body.index(key)+len(key):]
        body = body[:body.index('">')]
        return body


# def dlPlaylist(line, curArtist, curGenre):
#     albumDir = f'{MUSIC_DIR}\\{line[0]}'
#     if not exists(albumDir):
#         mkdir(albumDir)
#     url = f'https://music.youtube.com/playlist?list={line[1]}'

#     p = Playlist(url)

#     info (f"Downloading {p.title} album")

#     for idx, url in enumerate(p.video_urls):
#         info (url)
#         yt = YouTube(url)
#         # info(yt.streams)
#         stream = yt.streams.get_by_itag(251)
#         stream.download(output_path = albumDir, filename = f"{idx}. {yt.title}.raw")
    

#     # info(f"Fetching {line[0]} album info...")
#     # playlistInfo = youtube_dl.YoutubeDL({
#     #     'cookiefile': COOKIES_FILE,
#     #     'simulate': True,
#     #     'quiet': False,
#     # }).extract_info(url, download=False)

#     # cover = urlopen(getCoverUrl(playlistInfo['id'])).read()

#     # for track in playlistInfo["entries"]:
#     #     options = {
#     #         'quiet': False,
#     #         'extractaudio': True,
#     #         'audioformat': 'webm',
#     #         'format': 'bestaudio/opus',

#     #         # 'postprocessors': [{
#     #         #     'key': 'FFmpegExtractAudio',
#     #         #     'preferredcodec': 'mp3',
#     #         #     'preferredquality': '320'
#     #         # }],
#     #         # 'postprocessor_args': [
#     #         #     '-ar', '16000'
#     #         # ],
#     #         # 'prefer_ffmpeg': True,

#     #         'keepvideo': False,
#     #         'outtmpl': f"{albumDir}/{track['playlist_index']:02d}."+track['track'].replace('/', ';')+".webm",
#     #         'cookiefile': COOKIES_FILE

#     #     }

#     #     filename = f"{albumDir}/{track['playlist_index']:02d}." + \
#     #         track['track'].replace('/', ';')+".mp3"

#     #     if not exists(filename):
#     #         while True:
#     #             try:
#     #                 with youtube_dl.YoutubeDL(options) as ydl:
#     #                     #ydl.cache.remove()
#     #                     ydl.download([track['webpage_url']])
#     #                     break
#     #             except:
#     #                 info('Абасрались')
#     #                 sleep(5)
#     #                 continue
#     #         # with youtube_dl.YoutubeDL(options) as ydl:
#     #         #     ydl.download([track['webpage_url']])

#     #         os.system(
#     #             'ffmpeg -loglevel 8 -i "' + filename[:-4].replace("\"", "\\\"") + "\".webm -vn -ab 320k -ar 48000 -y \"" + filename.replace("\"", "\\\"")+ '\";')
#     #         rename(filename, f'{filename}.tmp')

#     #         f = eyed3.load(f'{filename}.tmp')
#     #         f.tag.album_artist = curArtist
#     #         f.tag.artist = track['artist']
#     #         f.tag.track_num = track['playlist_index']
#     #         f.tag.recording_date = track['release_year']
#     #         f.tag.title = track['track']
#     #         f.tag.album = track['album']
#     #         f.tag.genre = curGenre
#     #         f.tag.images.set(3, cover, "image/jpeg", u"cover")
#     #         f.tag.comment = 'fromyoutubemusic'

#     #         f.tag.save()

#     #         rename(f'{filename}.tmp', filename)
#     #         remove(f"{filename[:-4]}.webm")
#     #         info(
#     #             f"{track['playlist_index']:02d}.{track['track']} has been downloaded.")
#     #     else:
#     #         info(
#     #             f"{track['playlist_index']:02d}.{track['track']} has already been downloaded.")

#     # open(f'{albumDir}/.done', 'w').close()
#     green(f"{line[0]} has been downloaded.")
#     sleep(15)






def process_song(filename, album_id, artist_name, album_name, genre, title, year, track_number, total_tracks):
    cover = urlopen(getCoverUrl(album_id)).read()
    image = Image.open(io.BytesIO(cover))

    with io.BytesIO() as output:
        image.save(output, format="JPEG")
        image_bytes = output.getvalue()

    audio_file = MP4(filename)

    audio_file['covr'] = [
        MP4Cover(image_bytes, imageformat=MP4Cover.FORMAT_JPEG)
    ]

    # Set the artist, album name, and genre
    audio_file['\xa9ART'] = artist_name  # '\xa9ART' is the tag for the artist
    audio_file['\xa9alb'] = album_name  # '\xa9alb' is the tag for the album
    audio_file['\xa9gen'] = genre      # '\xa9gen' is the tag for the genre
    audio_file['\xa9nam'] = title        # '\xa9nam' is the tag for the title
    audio_file['\xa9day'] = year      # '\xa9day' is the tag for the release date
    audio_file['trkn'] = [(track_number, total_tracks)]  # 'trkn' is the tag for the track number

    audio_file.save()

    pass

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
            red(f"Error: {error.strip()}")
            exit(1)


    return process.poll()

def download_song(video_url, folder_path, idx):
    fetch_opts = {
        'quiet': True,  # Suppress console output
        'force_generic_extractor': True,  # Use generic extractor for metadata
        'cookiefile': COOKIES_FILE,
    }

    song_title = "Unknown"
    with yt_dlp.YoutubeDL(fetch_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        song_title = info_dict.get('title')

    info(f"Downloading {idx}. {song_title} - {video_url}")

    ydl_opts = {
        'quiet': True,         # Suppress output
        'cookiefile': COOKIES_FILE,
        'format': '141',
        # 'format': 'bestaudio/best[ext=m4a]',
        'outtmpl': f"{folder_path}/{idx}. {song_title}.m4a",
    }

    # Hotfix - yt-dlp cant download from music.youtube with ydl.download (music.youtube is needed because of 141 format 256kbs)
    command_str = f'yt-dlp -f 141 -o "{folder_path}/{idx}. {song_title}.raw" "{video_url}" --cookies="{COOKIES_FILE}" --quiet'
    execute_command(command_str)

    green(f'{idx}. {song_title} downloaded')

def fetch_playlist_video_urls(playlist_url):
    ydl_opts = {
        'extract_flat': True,  # Flatten the playlist
        'quiet': True,         # Suppress output
        'cookiefile': COOKIES_FILE,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(playlist_url, download=False)
        if 'entries' in result:
            video_urls = [entry['url'] for entry in result['entries']]
            return video_urls
    return []

# name format example In_the_Court_of_the_Crimson_King becomes folder name
def dl_playlist(playlist_url, playlist_name, artist, genre):
    album_path = f'{MUSIC_DIR}\\{playlist_name}'
    if not exists(album_path):
        mkdir(album_path)

    info (f"Fetching {playlist_name} album info...")
    video_urls = fetch_playlist_video_urls(playlist_url)

    info (f"Downloading {playlist_name} [{len(video_urls)} songs]\n")
    if video_urls:
        for idx, url in enumerate(video_urls, start=1):
            url = "https://music.youtube.com/watch?v=" + url.split("watch?v=")[1]
            download_song(url, album_path, idx)
            process_song()
    else:
        red("No videos found in the playlist.")
        return
    with open(f'{album_path}/.done', 'w') as file:
        pass 
    green(f'{playlist_name} has been downloaded.')
    sleep(10)


if __name__ == "__main__":
    process_song(f'{MUSIC_DIR}/TOHO_BOSSA_NOVA_1/1. furifuri ojousama.m4a', album_id="OLAK5uy_l06YRyzdC4euFmkFiE8zujhFvyVv2GZTQ", artist_name="ShibayanRecords", album_name="TOHO BOSSA NOVA 1", genre="Bossa Nova", title="furifuri ojousama", track_number=1, total_tracks=10, year="2012")
    # with open(LIST_FILE, 'r') as reader:
    #     lines = reader.read().split('\n')
    #     cur_artist = "Unknown"
    #     cur_genre = "Unknown"
    #     for linetext in lines:
    #         line = linetext.split(' ')
    #         if line[0] == '' or linetext[0] == '"':
    #             continue
    #         if line[0] == "#":
    #             cur_artist = ' '.join(line[1:])
    #             continue
    #         if line[0] == "@":
    #             cur_genre = ' '.join(line[1:])
    #             continue

    #         if not exists(f'{MUSIC_DIR}/{line[0]}/.done'):
    #             dl_playlist(f'https://www.youtube.com/playlist?list={line[1]}', line[0], cur_artist, cur_genre)
    #         else:
    #             green(f"{line[0]} is already downloaded.")



# driver = webdriver.Firefox()
# d = driver.get('https://music.youtube.com/search?q=TOHO_BOSSA_NOVA_3')
# print(d)
# driver.quit()
# with urlopen(f'https://music.youtube.com/search?q=TOHO_BOSSA_NOVA_3') as res:
#     body = res.read().decode('utf-8')
#     print(body)
    # key = '<meta property="og:image" content="'
    # body = body[body.index(key)+len(key):]
    # body = body[:body.index('">')]

# f = eyed3.load('/home/tuma/Music/TOHO_BOSSA_NOVA_1/01.furifuri ojousama.mp3')
# f.tag.album_artist = 'd'
# f.tag.save()
