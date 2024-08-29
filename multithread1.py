from threading import Thread
from multiprocessing import Process


def start_read():
    ydl_opts = {}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([values['Link_youtube']])


class Download(Thread):
    def run(self):
        start_download()


if __name__ == '__main__':
    while True:  # Event Loop App
        event, values = window.Read()
        if event is None or event == 'Exit':
            break
        if event == 'Download':
            t = Download()
            t.start()