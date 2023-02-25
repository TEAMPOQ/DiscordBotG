#module:    main.py
#author:    Carlos Rodriguez
#Date:      November 10, 2022
#Purpose:   Discord bot that plays music
import asyncio
import datetime
import json
import threading
import time
import async_timeout
import requests
import discord
import os
from pytube import YouTube
from keep_alive import keep_alive
from datetime import date
from secrets import spotify_user_id, playlist_id
from discord import FFmpegPCMAudio
from refresh import Refresh
import urllib.request
import re
from discord.ext import commands,tasks
from anyascii import anyascii

message_play = ""
intents = discord.Intents.all()
intents.members = True
client = discord.Client(intents=intents)
url = ["", "", "", "", ""]
bot = commands.Bot(intents=intents, command_prefix='$')
watch_link = []
title = ""
songs = []
artists = []
video_length = []
count = 0
counter = 0
playlist_total = 0
msg = ""
skip_song = False


class SaveSongs:
    def _init_(self):
        self.user_id = spotify_user_id
        self.spotify_token = " "
        self.playlist_id = playlist_id
        self.playlist_total = 0
        self.tracks = [" "]
        self.song_to_search = " "
        self.alb_uri = [" ", " ", " ", " "]


    def ask_user(self):
        song_to_search = input("Enter Spotify Playlist ID >> ")
        self.song_to_search = "6Rz9QFcQCvqaILMv7y95W2"#song_to_search


    def find_songs(self):
        # Loop through playlist tracks, add them to list
        tracks = [" "]
        print("finding songs in playlist")
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id)
        response = requests.get(query,
                                headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(self.spotify_token), "Host": "api.spotify.com"})


        response_json = response.json()

        print(response)

        for i in response_json["items"]:               #for loop for amount of items in response
            tracks += (i["track"]["uri"] + ",")        #stroes our tracks into a list
        self.tracks = tracks[:-1]                      #gets rid of last comma

    def search_playlist(self, id):
        global songs
        global artists
        global playlist_total

        # query search
        query = "https://api.spotify.com/v1/playlists/{}?limit=25".format(id).replace(" ", "")
        print(query)
        response = requests.get(query,
                                headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(self.spotify_token), "Host": "api.spotify.com"})

        response_json = response.json()
        playlist_total = response_json["tracks"]["total"]
        if playlist_total > 25:
            playlist_total = 25

        #print(response_json)
        for x in range(playlist_total):
            #print(response_json["tracks"]["total"]) # total number of tracks in the playlist
            #print(response_json["tracks"]["total"]) # total number of tracks in the playlist
            #print(response_json["tracks"]["items"][x]["track"]["album"]["artists"][0]["name"]) # name of artist
            #print(response_json["tracks"]["items"][x]["track"])  # name of artist

            songs.append(response_json["tracks"]["items"][x]["track"]["name"])
            artists.append(response_json["tracks"]["items"][x]["track"]["album"]["artists"][0]["name"])


            #a.find_songs()
        print(songs)
        print(artists)



    def create_playlist(self):
        #create a new playlist
        today = date.today()
        todayFormatted = today.strftime("%d/%n/%Y")
        query = "http://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)# the {} inserts the .format(id)

        request_body = json.dumps({"name": todayFormatted + " Playlist", "description": "Playlist updated with timestamp", "PUBLIC": False})

        response = requests.post(query, data=request_body, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(self.spotify_token)})

        response_json = response.json()
        print(response)

    def search_song(self,msg):
        global message_play

        self.song_to_search = msg  # song_to_search
        query = "http://api.spotify.com/v1/search/?type=track&q={}&include_external=audio&limit=4&market=US".format(self.song_to_search)
        print(query)
        #query = "https://api.spotify.com/v1/playlists/{}".format(self.song_to_search)# the {} inserts the .format(id)
        #query = "https://api.spotify.com/v1/search?type=album&include_external=audio/{}".format(self.song_to_search)# the {} inserts the .format(id)

        #song_list = [" "]4ox6mJwE4T4r6j2ic2ZMd0
                        # 37i9dQZF1DXd5gAeNDK56u
        global track_name
        track_name = ["","","","",""]
        artist_name = ["","","","",""]

        response = requests.get(query, headers={"Content-Type": "application/json", "Authorization":"Bearer {}".format(self.spotify_token)})

        response_json = response.json()

        if response_json["tracks"]["total"] <= 0:                                               # check for zero songs in list
            print("Playlist is to short")

        track_name[0] = response_json["tracks"]["items"][0]["name"]                             # song name
        artist_name[0] = response_json["tracks"]["items"][0]["album"]["artists"][0]["name"]     # artist Name

        #set the urls
        message_play = "https://www.youtube.com/results?search_query={}+by+{}".format(track_name[0].replace(" ", "+"), artist_name[0].replace(" ", "+"))
        #message_play[1] = "https://www.youtube.com/results?search_query={}+by+{}".format(track_name[1].replace(" ", "+"), artist_name[1].replace(" ", "+"))
        #message_play[2] = "https://www.youtube.com/results?search_query={}+by+{}".format(track_name[2].replace(" ", "+"), artist_name[2].replace(" ", "+"))
        #message_play[3] = "https://www.youtube.com/results?search_query={}+by+{}".format(track_name[3].replace(" ", "+"), artist_name[3].replace(" ", "+"))
        #message_play[4] = "https://www.youtube.com/results?search_query={}+by+{}".format(track_name[4].replace(" ", "+"), artist_name[4].replace(" ", "+"))

    def get_track(self):
        query = "https://api.spotify.com/v1/me/player/play"

        response = requests.put(query, data={"uris": "{}".format(self.alb_uri[0]),
                                "position_ms":"0"},
                                headers={"Content-Type": "application/json",
                                                "Authorization":"Bearer {}".format(self.spotify_token)},
                                )
        response_json = response.json()
        print(response_json)


    def call_refresh(self):
        print("Refreshing token")

        refreshCaller = Refresh()

        self.spotify_token = refreshCaller.refresh()

        #self.find_songs()



@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(ctx):
    global playlist_total
    global counter
    global msg
    global skip_song
    global video_length

    if ctx.author == client.user: # checks to see if the message was sent by a bot
        return
    msg = ctx.content
    channel = ctx.author.voice.channel

    # take command entry from user
    #
    #
    # Search and play playlist
    if msg.startswith('$playlist'):
        await reset()                                      # call to reset variable
        #msg = ctx.content
        await playlistplay(ctx)

    # play easter egg moe's song
    if msg.startswith('$moe'):
        mchannel = ctx.author.voice.channel
        mvoice = ctx.channel.guild.voice_client
        if mvoice is None:
            mvoice = await mchannel.connect()
        elif mvoice.channel != channel:
            mvoice.move_to(channel)
        print('try to play song')
        source = FFmpegPCMAudio('moe.mp3')
        player = mvoice.play(source)

    # skip current song
    if msg.startswith('$skip'):
        try:
            #await stop(ctx)
            playlist_total -= 1                         # adjust for list total
            counter += 1                                # adjust for index
            await stop(ctx)
            skip_song = True
            print(asyncio.get_event_loop())

        except:
            print("Event loop stopped before Future completed")


    # play a song
    if msg.startswith('$play'):
        await reset()                                      # call to reset variable
        try:
            a.search_song(msg[6:28])
            print("going into getURL")
            await getYoutubeUrls()
            print("going into download")
            video_length.clear()
            print(video_length)
            await download(ctx)
            # play song function
            await play(ctx)
        except:
            print("error playing song")


    # connect bot to channel
    if msg.startswith('$connect'):
        await connect(ctx)


@client.event
async def playlistplay(ctx):
    global playlist_total
    global counter
    global msg
    global skip_song

    if ctx.author == client.user: # checks to see if the message was sent by a bot
        return
    channel = ctx.author.voice.channel

    # search playlist function call with spotify api
    a.search_playlist(msg[9:32].replace(" ", ""))
    try:
        for counter in range(playlist_total):
            print(songs[counter] + " " + artists[counter])
            # search for song
            a.search_song(songs[counter] + " " + artists[counter])
            print("going into getURL")
            # generate youtube url
            await getYoutubeUrls()
            # download song
            await download(ctx)
            # call play function
            await play(ctx)
            # wait for song to finish
            test = asyncio.get_running_loop()
            end = test.time() + video_length[int(counter)][0]

            while True:
                print(datetime.datetime.now())
                if (test.time() + 1.0) >= end:
                    break
                if skip_song == True:
                    break
                await asyncio.sleep(1)
            #asyncio.sleep(video_length[int(counter)][0])
            skip_song = False
    except:
        print("playlist error")
    counter = 0
    discord.player.VoiceClient.stop(ctx)


@client.event
async def download(ctx):
    global watch_link
    global title
    global video_length
    global count
    channel = ctx.author.voice.channel
    voice = ctx.author.voice

    try:
        # passiing link to pafy
        print("attempt download")
        yt = YouTube(watch_link)
        title = yt.title + '.mp3'
        video = YouTube(watch_link).streams.filter(only_audio=True).first()
        video.download(filename='song.mp3')
        #stream = yt.streams.filter(file_extension='mp3')
        video_length.append(YouTube(watch_link).length.real.as_integer_ratio())

    except:
        print("DOWNLOAD UNSUCCESSFUL")
        pass

# connect bot function
async def connect(ctx):
    voice = ctx.author.voice
    channel = ctx.author.voice.channel
    if not voice:
        return await ctx.send("Author is not connected to any voice channel")
    try:
        player = await channel.connect()
    except:
        pass

    print("connected{0.user}".format(client))


@client.event
async def play(ctx):
    channel = ctx.author.voice.channel
    voice = ctx.channel.guild.voice_client
    if voice is None:
        voice = await channel.connect()
    elif voice.channel != channel:
        voice.move_to(channel)
    print('try to play song')
    #voice = await channel.connect()
    source = FFmpegPCMAudio("song.mp3")
    player = voice.play(source)


@client.event
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnected()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@client.event
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Currently no audio is playing.")

@client.event
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("The audio is not paused.")

@client.event
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()

@client.event
async def getYoutubeUrls():
    global message_play
    global watch_link
    video_ids = []

    #html = urllib.request.urlopen(message_play)
    html = urllib.request.urlopen(anyascii(message_play))
    response = html.read()
    video_ids = re.findall(r"watch\?v=(\S{11})", str(response))

    watch_link = "https://www.youtube.com/watch?v=" + video_ids[0]
    print(watch_link)

"""
reset all variables to avoid unwanted errors
"""
@client.event
async def reset():
    global watch_link
    global url
    global title
    global songs
    global artists
    global video_length
    global count
    global counter
    global playlist_total
    global msg
    global skip_song
    watch_link = ["", "", "", "", ""]
    url = ["", "", "", "", ""]
    watch_link = []
    title = ""
    songs = []
    artists = []
    video_length = []
    count = 0
    counter = 0
    playlist_total = 0
    msg = ""
    skip_song = False


a = SaveSongs()
a.call_refresh()
keep_alive()
client.run("")