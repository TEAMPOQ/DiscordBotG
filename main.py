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
import spotipy
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
from secrets import spotify_user_id, playlist_id, refresh_token, access_token
import spotipy.util as util

message_play = ""
intents = discord.Intents.all()
intents.members = True
client = discord.Client(intents=intents)
url = ["", "", "", "", ""]
bot = commands.Bot(intents=intents, command_prefix='$')
watch_link = []
title = ""
str_msg_list = "PLAYLISTS: "
songs = []
artists = []
video_length = []
bot_playlist = []
count = 0
counter = 0
playlist_total = 0
msg = ""
skip_song = False
playlist_response = ''
SPOTIFY_USERNAME='31nqczrdhhi2y4o2pnyv53ihfncq'
SPOTIPY_CLIENT_ID='3c7d7773da494e2db73293f7361348b3'
SPOTIPY_CLIENT_SECRET='3b72a8bf993642869c4caf9b6af3fb11'
SPOTIPY_REDIRECT_URI='https://github.com/TEAMPOQ/DiscordBotG'

playlist_ID = ''
track_id = ''

sp = spotipy.Spotify(auth=access_token)
scope = 'playlist-modify-public'

token = spotipy.SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI, scope=scope, username=SPOTIFY_USERNAME)
spotifyObject = spotipy.Spotify(auth_manager=token)

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

    ############### GET PLAYLIST ###############
    ############################################
    def get_playlists(self):
        global str_msg_list
        global bot_playlist
        bot_playlist.clear()
        str_msg_list = "PLAYLISTS: "
        list_num = 1
        sp.set_auth(self.spotify_token)
        playlist_response = sp.current_user_playlists(limit=25, offset=0)

        while str(playlist_response).find("'name': ") != -1:
            num = str(playlist_response).find("'name': ")
            secondHAlf = str(playlist_response)[num:]
            bot_playlist.append(secondHAlf[9:secondHAlf.find("',")])
            str_msg_list += '\n' + str(list_num) + '. ' + secondHAlf[9:secondHAlf.find("',")]
            playlist_response = str(playlist_response)[num+9:]
            list_num += 1

    ############ GET PLAYLIST SONGS ############
    ############################################
    def get_playlists_songs(self):
        global str_msg_list, playlist_response, bot_playlist, playlist_ID
        song_list = []
        str_msg_list = "SONGS: "
        list_num = 0
        sp.set_auth(self.spotify_token)
        playlist_songs = spotifyObject.playlist_items(playlist_ID, limit=25, offset=0, market=None)

        num_tracks = spotifyObject.playlist_items(playlist_ID, limit=25, offset=0, market=None, fields='total')
        trackss = str(num_tracks)[10: -1]
        #print(playlist_songs)
        for x in range(int(trackss)):
            print(playlist_songs['items'][int(list_num)]['track']['name'])
            str_msg_list += str(int(x+1)) + ". " + playlist_songs['items'][int(list_num)]['track']['name'] + " | "
            list_num += 1

    ############# SEARCH PLAYLIST ##############
    ############################################
    def search_playlist(self, id):
        global songs
        global artists
        global playlist_total
        global playlist_ID

        # query search
        query = "https://api.spotify.com/v1/playlists/{}?limit=25".format(playlist_ID).replace(" ", "")
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

    ############# Create Playlist ##############
    ############################################
    def create_playlist(self, name):
        #create a new playlist
        today = date.today()
        todayFormatted = today.strftime("%d/%n/%Y")

        #sp.set_auth(access_token)
        spotifyObject.user_playlist_create(user=str(SPOTIFY_USERNAME), name=str(name), public=True, collaborative=False, description=todayFormatted)


    ############# Select Playlist ##############
    ############################################
    def select_playlist(self, name):
        global bot_playlist
        global playlist_ID
        a.get_playlists()                                                                                           # INITIALIZE bot_playlist
        index = 0                                                                                                   # KEEP TRACK OF PLAYLIST INDEX
        for x in bot_playlist:
            if str(x).find(str(name)) != -1:                                                                        # FIND IF PLAYLIST EXISTS
                break
            index += 1
        playlist_ID = spotifyObject.user_playlists(user=SPOTIFY_USERNAME, offset=index)['items'][index]['id']       # GRAB PLAYLIST ID

    ############# ADD TO PLAYLIST ##############
    ############################################
    def add_playlist(self, name):
        global playlist_ID
        global track_id
        a.search_song(name)
        print(track_id)
        spotifyObject.playlist_add_items(playlist_id=playlist_ID, items=[track_id], position=0)


    ############### SEARCH SONG ################
    ############################################
    def search_song(self,msg):
        global message_play
        global track_name
        global track_id

        self.song_to_search = msg  # song_to_search
        query = "http://api.spotify.com/v1/search/?type=track&q={}&include_external=audio&limit=4&market=US&limit=1".format(self.song_to_search)

        track_name = ["","","","",""]
        artist_name = ["","","","",""]

        response = requests.get(query, headers={"Content-Type": "application/json", "Authorization":"Bearer {}".format(self.spotify_token)})
        response_json = response.json()

        if response_json["tracks"]["total"] <= 0:                                               # check for zero songs in list
            print("Playlist is to short")

        track_id = response_json["tracks"]["items"][0]["id"]                                    # song id
        track_name[0] = response_json["tracks"]["items"][0]["name"]                             # song name
        artist_name[0] = response_json["tracks"]["items"][0]["album"]["artists"][0]["name"]     # artist Name

        #set the urls
        message_play = "https://www.youtube.com/results?search_query={}+by+{}".format(track_name[0].replace(" ", "+"), artist_name[0].replace(" ", "+"))

    ########## REFRESH SPOTIFY TOKEN ###########
    ############################################
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
    global str_msg_list

    if ctx.author == client.user: # checks to see if the message was sent by a bot
        return
    msg = ctx.content
    channel = ctx.author.voice.channel

    ############################ USER COMMANDS #############################
    ########################################################################
    ########################################################################

    ############ LIST ALL PLAYLIST #############
    ############################################
    if msg.startswith('$p list'):
        a.get_playlists()
        await sendMsg(ctx, str_msg_list)

    ######## LIST ALL SONG IN PLAYLIST #########
    ############################################
    if msg.startswith('$p songs'):
        a.get_playlists_songs()
        await sendMsg(ctx, str_msg_list)

    ########### CREATE A  PLAYLIST #############
    ############################################
    if msg.startswith('$p create'):
        a.create_playlist(msg[10:])                #send command to create a new playlist

    ########### SELECT A  PLAYLIST #############
    ############################################
    if msg.startswith('$p select'):
        a.select_playlist(msg[10:])                #send command to create a new playlist

    ############## ADD A PLAYLIST ##############
    ############################################
    if msg.startswith('$p add'):
        if len(playlist_ID) < 1:
            await sendMsg('SELECT A PLAYLIST BEFORE ADDING A SONG-__-')
        else:
            a.add_playlist(msg[7:])

    ############# PLAY A  PLAYLIST #############
    ############################################
    if msg.startswith('$p play'):
        await playlistplay(ctx)
        await reset()                                          # call to reset variable


    ################ SKIP SONG ################
    ###########################################
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

    ################ PLAY A SONG ##############
    ###########################################
    if msg.startswith('$play'):
        try:
            await play(ctx)
        except:
            print("error playing song")

        await reset()  # call to reset variable

    ################ SPAM A USER ##############
    ###########################################
    if msg.startswith('$spam'):
        #try:
        username_spam = msg[6:]     # username were going to spam
        await spamUser(ctx, username_spam)

    ################ CONNECT BOT TO CHANNEL #############
    #####################################################
    if msg.startswith('$connect'):
        await connect(ctx)


############################ BOT FUNCTIONS #############################
########################################################################
########################################################################



############### SEND A MSG FUNCTION #############
#################################################
async def sendMsg(ctx, str_msg):
    music_channel = client.get_channel(965814271063781396)
    await music_channel.send(str_msg)

################ SPAM USER FUNCTION #############
#################################################
@client.event
async def spamUser(ctx, username):
    channel = ctx.author.voice.channel
    text_channels = ctx.channel.guild.text_channels
    text_channel = text_channels[0]

    mentions = discord.AllowedMentions(everyone=True, users=True, roles=True, replied_user=True)
    for x in range(1000):
        await asyncio.sleep(2)
        await channel.send(username, allowed_mentions=mentions)
        x += 1

################ PLAY PLAYLIST FUNCTION #############
#####################################################
@client.event
async def playlistplay(ctx):
    global playlist_total
    global playlist_ID
    global counter
    global msg
    global skip_song
    global video_length

    if ctx.author == client.user:                                       # checks to see if the message was sent by a bot
        return
    channel = ctx.author.voice.channel
    voice = ctx.channel.guild.voice_client
    video_length.clear()
    # search playlist function call with spotify api
    a.search_playlist(msg[9:32].replace(" ", ""))
    for counter in range(playlist_total):
        a.search_song(songs[counter] + " " + artists[counter])      # search for song

        await getYoutubeUrls()                                      # generate youtube url
        try:
            await download(ctx)
            # play song function
        except:
            print('error with download')
        try:
            if voice is None:
                voice = await channel.connect()
            elif voice.channel != channel:
                voice.move_to(channel)

            source = FFmpegPCMAudio("song.mp3")
            player = voice.play(source)
        except:
            print("error playing song")

        test = asyncio.get_running_loop()                           # wait for song to finish
        end = test.time() + video_length                            # calculate the end of the current song

        while True:                                                 # while song is playing do
            print(datetime.datetime.now())                          # print time stamp
            if (test.time() + 1.0) >= end or skip_song is True:     # loop break condition
                skip_song = False                                   # reset skip condition
                break
            await asyncio.sleep(1)                                  # timeout

        print("playlist error")                                         # catch any execution errors with playlist
    counter = 0                                                         # reset counter
    discord.player.VoiceClient.stop(ctx)                                # force stop voice client


################ DOWNLOAD SONG FUNCTION #############
#####################################################
@client.event
async def download(ctx):
    global watch_link
    global title
    global video_length
    global count

    music_channel = client.get_channel(965814271063781396)
    channel = ctx.author.voice.channel
    voice = ctx.author.voice
    song_name = ''
    out_file = None

    print('1')
    yt = YouTube(str(watch_link))                                       # url input from user

    print('2')
    try:
        out_file = yt.streams.get_audio_only().download()               # download the file
    except:
        pass
    print('3.5')

    song_name = os.path.basename(out_file)[:os.path.basename(out_file).find(".mp4")]

    print('3')
    if os.path.exists('song.mp3'):                                      # if song.mp3 already exists delete
        os.remove('song.mp3')
    print('4')
    os.rename(out_file, 'song.mp3')                                     # rename song file
    print('5')
    await music_channel.send(song_name + " will begin shortly!") # send in discord chat
    print(os.path.basename(out_file) + " has been successfully downloaded.")              # result of success


################ CONNECT BOT TO CHANNEL #############
#####################################################
async def connect(ctx):
    voice = ctx.author.voice
    channel = ctx.author.voice.channel
    try:
        await channel.connect()
    except:
        pass

    print("connected{0.user}".format(client))


################ PLAY SONG FUNCTION #################
#####################################################
@client.event
async def play(ctx):
    channel = ctx.author.voice.channel
    voice = ctx.channel.guild.voice_client

    a.search_song(msg[6:28])
    await getYoutubeUrls()
    video_length.clear()
    try:
        await download(ctx)
        # play song function
    except:
        print('error with download')
    try:
        if voice is None:
            voice = await channel.connect()
        elif voice.channel != channel:
            voice.move_to(channel)

        source = FFmpegPCMAudio("song.mp3")
        player = voice.play(source)
    except:
        print("error playing song")





############### DISCONNECT BOT FUNCTION #############
#####################################################
@client.event
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnected()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


################ PAUSE SONG FUNCTION ################
#####################################################
@client.event
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Currently no audio is playing.")


################ RESUME SONG FUNCTION ###############
#####################################################
@client.event
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("The audio is not paused.")

################# STOP SONG FUNCTION ################
#####################################################
@client.event
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()

############# GET URL FOR SONG FUNCTION #############
#####################################################
@client.event
async def getYoutubeUrls():
    global message_play
    global watch_link
    global video_length
    video_ids = []

    #html = urllib.request.urlopen(message_play)
    html = urllib.request.urlopen(anyascii(message_play))
    response = html.read()
    video_ids = re.findall(r"watch\?v=(\S{11})", str(response))

    watch_link = "https://www.youtube.com/watch?v=" + video_ids[0]
    vid = pytube.YouTube(watch_link)
    video_length = vid.length
    print(watch_link)

############# RESET VARIABLES FUNCTION ##############
#####################################################
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