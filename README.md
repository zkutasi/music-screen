# music-screen

A small TKinter app that uses last.fm and shows currently playing content. It also uses discogs.com to fetch some extra data, mainly better images.

Inspired by https://github.com/hankhank10/music-screen-api: However this project is too tied to Sonos, this one is absolutley without that requirement. The whole point of this project is to give a solution to this problem absolutely without HW requirements. Also that other project is having multiple possible modes, and is very much tailored to one screen and size, so I ended up taking some code from there, but left a bunch of it alone and wrote mine.

# Features

- There are parsers: Modules that try to figure out what you play
  - Poll last.fm's API for currently listening song, pulling in its artist, album and cover
  - Poll your Emby local server for what is playing
- There are also enrichers: Modules that enrich the data with extra info or higher quality images for example
  - Cross-searching the same played content on discogs.com and fetching a higher quality cover from there
- Updating a screen with this "now playing" information

# Limitations

- The discogs.com search is taking the very first found match from the list, and sometimes that is not right... not sure if anything can be done about it though: the tool searches for artist-album-title alltogether and sometimes it is not uniquely identifying the release
- LastFM seems to error our frequently during the day without any reasons, after the transient period things go back to normal, but it seems to be quite annoying

# Getting started

You do not need much, everything is free here:
- Python3 and a small amount of dependencies
- Last.fm account (optional)
- Emby local server (optional)
- Discogs account (optional)
- A screen to run it on... I use a Raspberry Pi 4

Be sure to create a settings.py and provide your own accounts and preferences in it (see the example file for syntax)