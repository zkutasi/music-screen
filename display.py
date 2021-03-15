from io import BytesIO
import logging
import os
from PIL import Image, ImageFile, ImageTk
import signal
import tkinter as tk
from tkinter import font as tkFont
import Xlib.display as XDisplay
from Xlib.ext import dpms

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
        _LOGGER.info('Initializing Display...')
        self.data = None
        self.xdisplay = XDisplay.Display()
        self.screen_saver_settings = self.xdisplay.get_screen_saver()
        self.xdisplay.set_screen_saver(
            timeout=0,
            interval=0,
            allow_exposures=True,
            prefer_blank=False)
        self.xdisplay.force_screen_saver(mode=XDisplay.X.ScreenSaverReset)
        self.dmps_timeouts = self.xdisplay.dpms_get_timeouts()
        self.xdisplay.dpms_set_timeouts(
            standby_timeout=0,
            suspend_timeout=0,
            off_timeout=0)
        self.xdisplay.dpms_force_level(dpms.DPMSModeOn)
        self.xdisplay.sync()

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
        self.root.bind("<Double-Button-1>", self.double_click_event)

        self.detail_frame = tk.Frame(self.root, bg="black", width=SCREEN_W, height=SCREEN_H)
        self.detail_frame.grid(row=0, column=0, sticky="news")

        self.curtain_frame = tk.Frame(self.root, bg="black", width=SCREEN_W, height=SCREEN_H)
        self.curtain_frame.grid(row=0, column=0, sticky="news")

        self.track_name = tk.StringVar()
        self.artist_album = tk.StringVar()
        
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
            textvariable=self.artist_album,
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
        self.root.config(cursor="none")
        self.root.update()

    def double_click_event(self, event):
        _LOGGER.info('Exiting...')
        os.kill(os.getpid(), signal.SIGQUIT)

    async def redraw(self, httpclient, data):
        if data == self.data:
            return

        await self._redraw_image(data, httpclient)

        artist_album_text = "?"
        trackname_text = "?"
        if data.nowplaying:
            trackname_text = data.trackname
            
            detail_prefix = None
            detail_suffix = data.album or None

            if data.artist != trackname_text:
                detail_prefix = data.artist

            artist_album_text = " • ".join(filter(None, [detail_prefix, detail_suffix]))
            if data.label:
                artist_album_text += ' • {label}'.format(label=data.label)

            self.curtain_frame.lower()
            _LOGGER.info('Listening to [{trackname}] from [{artist_album}]'.format(
                trackname=trackname_text,
                artist_album=artist_album_text))
            self.detail_frame.lift()
            self.is_showing = True
        else:
            _LOGGER.info('Not listening to anything at the moment...')
            self.curtain_frame.lift()
            self.is_showing = False

        self.track_name.set(trackname_text)
        self.artist_album.set(artist_album_text)
        self.data = data
        self.update()

    def update(self):
        self.root.update_idletasks()
        self.root.update()

    async def _redraw_image(self, data, httpclient):
        image = None

        def resize_image(image, length):
            image = image.resize((length, length), ImageTk.Image.LANCZOS)
            return ImageTk.PhotoImage(image)
        
        if data.nowplaying:
            image_data = await httpclient.get_image_data(data.image_url)
            if image_data:
                image = Image.open(BytesIO(image_data))
        
            if image:
                image = resize_image(image, THUMB_W)
            else:
                _LOGGER.warning("Image not available")

        self.album_image = image
        self.label_albumart_detail.configure(image=image)

    def cleanup(self):
        _LOGGER.info('Reset display settings...')
        self.xdisplay.set_screen_saver(
            timeout=self.screen_saver_settings.timeout,
            interval=self.screen_saver_settings.interval,
            allow_exposures=self.screen_saver_settings.allow_exposures,
            prefer_blank=self.screen_saver_settings.prefer_blanking)
        self.xdisplay.dpms_set_timeouts(
            standby_timeout=self.dmps_timeouts.standby_timeout,
            suspend_timeout=self.dmps_timeouts.suspend_timeout,
            off_timeout=self.dmps_timeouts.off_timeout)
        self.xdisplay.dpms_force_level(dpms.DPMSModeOn)
        self.xdisplay.force_screen_saver(mode=XDisplay.X.ScreenSaverReset)
        self.xdisplay.sync()