# module:    main.py
# author:    Carlos Rodriguez
# Date:      November 10, 2022
# Purpose:   Discord bot with the purpose of playing music
#            uses spotify api to search song names can also search spotify playlists
#            uses pytube to stream/download songs found

import asyncio
import datetime
import json
import os
import re
import urllib.request
from datetime import date

import discord
import pytube
import requests
from anyascii import anyascii
from discord import FFmpegPCMAudio
from discord.ext import commands
from pytube import YouTube

from keep_alive import keep_alive
from refresh import Refresh
from secrets import spotify_user_id, playlist_id

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
            songs.append(response_json["tracks"]["items"][x]["track"]["name"])
            artists.append(response_json["tracks"]["items"][x]["track"]["album"]["artists"][0]["name"])


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
        song_searching = msg[6:]
        a.search_song(msg[6:28])
        await getYoutubeUrls()
        video_length.clear()
        try:
            await download(ctx)
            # play song function
            await play(ctx)
        except:
            print("error playing/downloading song")
            
        await reset()  # call to reset variable

    # spam a user @
    if msg.startswith('$spam'):
        #try:
        username_spam = msg[6:]     # username were going to spam
        await spamUser(ctx, username_spam)

    # connect bot to channel
    if msg.startswith('$connect'):
        await connect(ctx)

@client.event
async def spamUser(ctx, username):
    channel = ctx.author.voice.channel
    text_channels = ctx.channel.guild.text_channels
    text_channel = text_channels[0]

    mentions = discord.AllowedMentions(everyone=True, users=True, roles=True, replied_user=True)
    for x in range(1000):
        await asyncio.sleep(1.5)
        await channel.send(username, allowed_mentions=mentions)
        x += 1

@client.event
async def playlistplay(ctx):
    global playlist_total
    global counter
    global msg
    global skip_song

    if ctx.author == client.user:                                       # checks to see if the message was sent by a bot
        return
    channel = ctx.author.voice.channel

    # search playlist function call with spotify api
    a.search_playlist(msg[9:32].replace(" ", ""))
    try:
        for counter in range(playlist_total):
            a.search_song(songs[counter] + " " + artists[counter])      # search for song
            await getYoutubeUrls()                                      # generate youtube url
            await download(ctx)                                         # download song
            await play(ctx)                                             # call play function
            test = asyncio.get_running_loop()                           # wait for song to finish
            end = test.time() + video_length[int(counter)][0]           # calculate the end of the current song

            while True:                                                 # while song is playing do
                print(datetime.datetime.now())                          # print time stamp
                if (test.time() + 1.0) >= end or skip_song is True:     # loop break condition
                    skip_song = False                                   # reset skip condition
                    break
                await asyncio.sleep(1)                                  # timeout
    except:
        print("playlist error")                                         # catch any execution errors with playlist
    counter = 0                                                         # reset counter
    discord.player.VoiceClient.stop(ctx)                                # force stop voice client



@client.event
async def download(ctx):
    global watch_link
    global title
    global video_length
    global count
    channel = ctx.author.voice.channel
    voice = ctx.author.voice

    yt = YouTube(watch_link)                                            # url input from user
    video = yt.streams.filter(only_audio=True).first()                  # extract only audio
    out_file = video.download()                                         # download the file
    new_file = 'song.mp3'                                               # save the file
    print(yt.title + " has been successfully downloaded.")              # result of success



# connect bot function
async def connect(ctx):
    voice = ctx.author.voice
    channel = ctx.author.voice.channel
    try:
        await channel.connect()
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

    source = FFmpegPCMAudio("song.mp3")
    player = voice.play(source)
    #voice.play(FFmpegPCMAudio("song.mp3"))



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