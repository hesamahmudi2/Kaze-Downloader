import os
import threading
import platform
import traceback

import yt_dlp

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle


class KazeDownloader(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=dp(18),
            padding=[dp(25), dp(30), dp(25), dp(25)],
            **kwargs
        )


        with self.canvas.before:
            Color(0.055, 0.065, 0.09, 1)
            self.background = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(18)]
            )

        self.bind(
            pos=self._update_background,
            size=self._update_background
        )


        title = Label(
            text="KAZE",
            font_size=dp(34),
            bold=True,
            color=(0.3, 0.75, 1, 1),
            size_hint_y=None,
            height=dp(50),
        )

        subtitle = Label(
            text="Downloader",
            font_size=dp(18),
            color=(0.75, 0.78, 0.85, 1),
            size_hint_y=None,
            height=dp(30),
        )

        self.add_widget(title)
        self.add_widget(subtitle)


        self.url_input = TextInput(
            hint_text="Tempel link video di sini...",
            multiline=False,
            size_hint_y=None,
            height=dp(55),
            padding=[dp(15), dp(15)],
            font_size=dp(15),
            foreground_color=(1, 1, 1, 1),
            background_color=(0.11, 0.13, 0.18, 1),
            cursor_color=(0.3, 0.75, 1, 1),
        )

        self.add_widget(self.url_input)


        self.download_button = Button(
            text="DOWNLOAD MEDIA",
            size_hint_y=None,
            height=dp(55),
            font_size=dp(16),
            bold=True,
            background_normal="",
            background_color=(0.12, 0.55, 0.95, 1),
            color=(1, 1, 1, 1),
        )

        self.download_button.bind(
            on_press=self.start_download
        )

        self.add_widget(self.download_button)


        self.progress = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=dp(12),
        )

        self.add_widget(self.progress)

        self.percent = Label(
            text="0%",
            font_size=dp(15),
            color=(0.7, 0.85, 1, 1),
            size_hint_y=None,
            height=dp(30),
        )

        self.add_widget(self.percent)


        self.status = Label(
            text="Siap untuk mendownload",
            font_size=dp(14),
            color=(0.65, 0.68, 0.75, 1),
            size_hint_y=None,
            height=dp(40),
            halign="center",
            valign="middle",
        )

        self.status.bind(
            size=self._update_status_text
        )

        self.add_widget(self.status)


    def _update_background(self, *args):
        self.background.pos = self.pos
        self.background.size = self.size

    def _update_status_text(self, instance, size):
        instance.text_size = size

    def set_status(self, text):
        self.status.text = text


    def start_download(self, instance):

        url = self.url_input.text.strip()

        if not url:
            self.set_status(
                "⚠ Masukkan link terlebih dahulu."
            )
            return

        self.progress.value = 0
        self.percent.text = "0%"

        self.set_status(
            "🔎 Memeriksa link..."
        )

        self.download_button.disabled = True
        self.url_input.disabled = True

        thread = threading.Thread(
            target=self.download_media,
            args=(url,),
            daemon=True
        )

        thread.start()


    def get_download_folder(self):

        if platform.system() == "Android":

            folder = os.path.join(
                "/storage/emulated/0",
                "Download",
                "KazeDownloader"
            )

        else:

            folder = os.path.join(
                os.path.expanduser("~"),
                "Downloads",
                "KazeDownloader"
            )

        os.makedirs(
            folder,
            exist_ok=True
        )

        return folder


    def download_media(self, url):

        try:

            folder = self.get_download_folder()

            print(
                "Download folder:",
                folder
            )

            print(
                "URL:",
                url
            )


            def progress_hook(data):

                status = data.get("status")

                if status == "downloading":

                    downloaded = data.get(
                        "downloaded_bytes",
                        0
                    )

                    total = (
                        data.get("total_bytes")
                        or data.get(
                            "total_bytes_estimate",
                            0
                        )
                    )

                    if total:

                        percent = (
                            downloaded /
                            total *
                            100
                        )

                        percent = min(
                            max(percent, 0),
                            100
                        )

                        Clock.schedule_once(
                            lambda dt, p=percent:
                            self.update_progress(p)
                        )

                        Clock.schedule_once(
                            lambda dt, p=percent:
                            self.set_status(
                                f"🔄 Mengunduh... {p:.1f}%"
                            )
                        )

                elif status == "finished":

                    Clock.schedule_once(
                        lambda dt:
                        self.update_progress(100)
                    )

                    Clock.schedule_once(
                        lambda dt:
                        self.set_status(
                            "⚙ Menyelesaikan download..."
                        )
                    )

            # -------------------------
            # YT-DLP OPTIONS
            # -------------------------

            options = {

                "outtmpl": os.path.join(
                    folder,
                    "%(title)s.%(ext)s"
                ),

                # Prioritaskan MP4 satu file.
                # Kalau tidak tersedia,
                # fallback ke format terbaik.
                "format": (
                    "best[ext=mp4]/"
                    "best"
                ),

                "noplaylist": True,

                "progress_hooks": [
                    progress_hook
                ],

                # Jangan tampilkan output
                # yt-dlp ke console/UI.
                "quiet": True,

                "no_warnings": True,

                # Hindari metadata tambahan.
                "writethumbnail": False,
                "writeinfojson": False,
                "writesubtitles": False,

                # Jangan mencoba merge audio/video.
                # Ini penting karena kita belum
                # membawa FFmpeg.
                "merge_output_format": None,

                "http_headers": {
                    "User-Agent": (
                        "Mozilla/5.0 "
                        "(Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 "
                        "(KHTML, like Gecko) "
                        "Chrome/120.0 Safari/537.36"
                    )
                },
            }


            with yt_dlp.YoutubeDL(
                options
            ) as ydl:

                result = ydl.download(
                    [url]
                )

            print(
                "yt-dlp result:",
                result
            )

            Clock.schedule_once(
                lambda dt:
                self.download_success()
            )

        except Exception as error:

            error_message = str(error)

            print(
                "\n========== DOWNLOAD ERROR =========="
            )

            print(
                error_message
            )

            traceback.print_exc()

            print(
                "====================================\n"
            )

            Clock.schedule_once(
                lambda dt, msg=error_message:
                self.download_failed(msg)
            )


    def update_progress(self, value):

        value = max(
            0,
            min(value, 100)
        )

        self.progress.value = value

        self.percent.text = (
            f"{value:.1f}%"
        )


    def download_success(self):

        self.progress.value = 100

        self.percent.text = "100%"

        self.set_status(
            "✓ Download berhasil!"
        )

        self.url_input.text = ""

        self.download_button.disabled = False
        self.url_input.disabled = False


    def download_failed(self, error):

        self.progress.value = 0

        self.percent.text = "Error"

        self.set_status(
            "✕ Download gagal."
        )

        print(
            "DOWNLOAD ERROR:",
            error
        )

        self.download_button.disabled = False
        self.url_input.disabled = False


class KazeApp(App):

    def build(self):

        self.title = "Kaze Downloader"

        return KazeDownloader()


if __name__ == "__main__":
    KazeApp().run()