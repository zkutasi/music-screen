# music-screen

A small TKinter app that uses last.fm and shows currently playing content. It also uses discogs.com to fetch some extra data, mainly better images.

Inspired by https://github.com/hankhank10/music-screen-api: However this project is too tied to Sonos, this one is absolutley without that requirement. The whole point of this project is to give a solution to this problem absolutely without HW requirements. Also that other project is having multiple possible modes, and is very much tailored to one screen and size, so I ended up taking some code from there, but left a bunch of it alone and wrote mine.

# Features

- Poll last.fm's API for currently listening song, pulling in its artist, album and cover
- Cross-searching the same from discogs.com and fetching a higher quality cover from there
- Updating a screen with this "now playing" information

# Getting started

You do not need much, everything is free here:
- Python3 and a small amount of dependencies
- Last.fm account
- Discogs account
- A screen to run it on... I use a Raspberry Pi 4

Be sure to edit settings.py and provide your own accounts and preferences