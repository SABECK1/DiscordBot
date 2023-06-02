ydl_opts = {
    'format': 'bestaudio/best',
    'ignoreerrors': True,
    'quiet': True,

    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}
add_opts = {
    'format': 'bestaudio/best',
    'outtmpl': './sounds/newsound.mp3',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',

    }],
}

ffmpeg_options = {
    'options': '-vn'
}
