from io import BytesIO
import logging
import os
from PIL import Image, ImageFile, ImageTk
import tkinter as tk
from tkinter import font as tkFont

import settings



SCREEN_W = settings.GlobalConfig.SCREEN_W
SCREEN_H = settings.GlobalConfig.SCREEN_H
THUMB_W = settings.GlobalConfig.THUMB_W
THUMB_H = settings.GlobalConfig.THUMB_H
_LOGGER = logging.getLogger(__name__)



class DisplaySetupError(Exception):
    pass


class DisplayController:
    def __init__(self, loop):
        self.loop = loop
        
        self.album_image = None
        self.is_showing = False

        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.root = None

        if not self.root:
            os.environ["DISPLAY"] = ":0"
            try:
                self.root = tk.Tk()
            except tk.TclError as error:
                _LOGGER.error("Cannot access display: %s", error)
                raise DisplaySetupError

        self.root.geometry(f"{SCREEN_W}x{SCREEN_H}")

        self.detail_frame = tk.Frame(self.root, bg="black", width=SCREEN_W, height=SCREEN_H)
        self.detail_frame.grid(row=0, column=0, sticky="news")

        self.curtain_frame = tk.Frame(self.root, bg="black", width=SCREEN_W, height=SCREEN_H)
        self.curtain_frame.grid(row=0, column=0, sticky="news")

        self.track_name = tk.StringVar()
        self.artist_album_text = tk.StringVar()
        
        track_font = tkFont.Font(family="Helvetica", size=30)
        detail_font = tkFont.Font(family="Helvetica", size=15)

        self.label_albumart_detail = tk.Label(
            self.detail_frame,
            image=None,
            borderwidth=0,
            highlightthickness=0,
            fg="white",
            bg="black",
        )
        label_track = tk.Label(
            self.detail_frame,
            textvariable=self.track_name,
            font=track_font,
            fg="white",
            bg="black",
            wraplength=SCREEN_W,
            justify="center",
        )
        label_artist_album = tk.Label(
            self.detail_frame,
            textvariable=self.artist_album_text,
            font=detail_font,
            fg="white",
            bg="black",
            wraplength=SCREEN_W,
            justify="center",
        )
        self.label_albumart_detail.place(relx=0.5, y=THUMB_H / 2, anchor=tk.CENTER)
        label_track.place(relx=0.5, y=THUMB_H + 10, anchor=tk.N)
        label_artist_album.place(relx=0.5, y=SCREEN_H - 10, anchor=tk.S)

        self.detail_frame.grid_propagate(False)

        self.root.attributes("-fullscreen", True)
        self.root.update()

    async def redraw(self, httpclient, data):
        pil_image = None
        
        if data['discogs'] and data['discogs'].data:
            url = data['discogs'].data.image_url
            image_data = await httpclient.get_image_data(url)
            if image_data:
                pil_image = Image.open(BytesIO(image_data))
        
        if pil_image is None:
            _LOGGER.warning("Image not available")

        self._update(pil_image, data)

    def _show_album(self):
        self.curtain_frame.lower()
        self.detail_frame.lift()
        self.is_showing = True
        self.root.update()

    def _hide_album(self):
        self.curtain_frame.lift()
        self.is_showing = False
        self.root.update()

    def _update(self, image, data):
        lastfm_data = data['lastfm'].data
        discogs_data = data['discogs'].data

        def resize_image(image, length):
            image = image.resize((length, length), ImageTk.Image.LANCZOS)
            return ImageTk.PhotoImage(image)

        if image:
            self.album_image = resize_image(image, THUMB_W)
            self.label_albumart_detail.configure(image=self.album_image)

        artist_album_text = ""
        display_trackname = lastfm_data.trackname

        detail_prefix = None
        detail_suffix = lastfm_data.album or None

        if lastfm_data.artist != display_trackname:
            detail_prefix = lastfm_data.artist

        artist_album_text = " • ".join(filter(None, [detail_prefix, detail_suffix]))
        if discogs_data and discogs_data.label:
            artist_album_text += ' • {label}'.format(label=discogs_data.label)

        self.track_name.set(display_trackname)
        self.artist_album_text.set(artist_album_text)
        self.root.update_idletasks()
        self._show_album()

    def cleanup(self):
        pass