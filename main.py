# module:    main.py
# author:    Carlos Rodriguez
# Date:      November 10, 2022
# Purpose:   Discord bot with the purpose of playing music
#            uses spotify api to search song names can also search spotify playlists
#            uses pytube to stream/download songs found


import asyncio
import datetime
import sys
import time
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
video_length = 0
bot_playlist = []
count = 0
counter = 0
playlist_total = 0
msg = ""
song_name = ""
skip_song = False
playlist_response = ''
SPOTIFY_USERNAME='31nqczrdhhi2y4o2pnyv53ihfncq'
SPOTIPY_CLIENT_ID='3c7d7773da494e2db73293f7361348b3'
SPOTIPY_CLIENT_SECRET='3b72a8bf993642869c4caf9b6af3fb11'
SPOTIPY_REDIRECT_URI='https://github.com/TEAMPOQ/DiscordBotG'
restart_time = (time.time() + 3300)                # used as a timer to restart script
playlist_ID = ''
track_id = ''

scope = 'playlist-modify-public'

token = spotipy.SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI ,scope=scope, username=SPOTIFY_USERNAME)
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
        spotifyObject.set_auth(self.spotify_token)
        playlist_res = spotifyObject.current_user_playlists(limit=25, offset=0)
        print(playlist_res)
        while str(playlist_res).find("'name': ") != -1:
            num = str(playlist_res).find("'name': ")
            secondHAlf = str(playlist_res)[num:]
            bot_playlist.append(secondHAlf[9:secondHAlf.find("',")])

            str_msg_list += '\n' + str(list_num) + '. ' + secondHAlf[9:secondHAlf.find("',")]
            playlist_res = str(playlist_res)[num+9:]
            list_num += 1


    ############ GET PLAYLIST SONGS ############
    ############################################
    def get_playlists_songs(self):
        global str_msg_list, playlist_response, bot_playlist, playlist_ID, songs, artists

        str_msg_list = "SONGS: "
        list_num = 0
        #spotifyObject.set_auth(self.spotify_token)
        playlist_songs  = spotifyObject.playlist_items(playlist_id=playlist_ID, limit=25, offset=0, market=None)
        num_tracks      = spotifyObject.playlist_items(playlist_id=playlist_ID, limit=25, offset=0, market=None, fields='total')
        song_names      = spotifyObject.playlist_items(playlist_id=playlist_ID, limit=25, offset=0, market=None, fields="items(track(name))")
        #artists_names   = spotifyObject.playlist_items(playlist_id=playlist_ID, limit=25, offset=0, market=None, fields="items(track(artists(name)))")
        temp_str_songs = str(song_names)
        #temp_str_artists = str(artists_names)
        append_str = ""
        trackss = str(num_tracks)[10: -1]
        #print(playlist_songs)
        for x in range(int(trackss)-1):
            artists_names = spotifyObject.playlist_items(playlist_id=playlist_ID, limit=1, offset=int(x),
                                                         market=None, fields="items(track(artists(name)))")
            temp_str_artists = str(artists_names)
            try:
                print(playlist_songs['items'][int(list_num)]['track']['name'])
                str_msg_list += str(int(x+1)) + ". " + playlist_songs['items'][int(list_num)]['track']['name'] + " | "
                # save song names
                temp_str_songs = temp_str_songs[temp_str_songs.find("'name': '")+9:]
                songs.append(temp_str_songs[:temp_str_songs.find("'")])
                # save artists names
                print(temp_str_artists)
                temp_str_artists = temp_str_artists[temp_str_artists.find("'name': '") + 9:]
                print(temp_str_artists)
                while True:
                    append_str += temp_str_artists[0:temp_str_artists.find("'")] + " "              # string with all artists in a song
                    if temp_str_artists.find("'name': '") == -1:                                    # break condition
                        break
                    temp_str_artists = temp_str_artists[temp_str_artists.find("'name': '") + 9:]    # updating value

                print("song #"+str(int(x)) + " " + append_str)                                      # debugging purpose
                artists.append(append_str)                                                          # append artists
                append_str = ""                                                                     # clear temp string
                list_num += 1
            except:
                pass


        #print(songs)
        print(songs)
        print(artists)

    ############# SEARCH PLAYLIST ##############
    ############################################
    def search_playlist(self):
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
        print(bot_playlist)
        index = 0                                                                                                   # KEEP TRACK OF PLAYLIST INDEX
        print(name)
        for x in bot_playlist:
            if str(x).find(str(name)) != -1:                                                                        # FIND IF PLAYLIST EXISTS
                break
            index += 1
        playlist_ID = spotifyObject.user_playlists(user=SPOTIFY_USERNAME, offset=0)['items'][index]['id']           # GRAB PLAYLIST ID

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
        global message_play, track_name, track_id, artists, songs, token

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
        message_play = "https://www.youtube.com/results?search_query={}".format(msg.replace(" ", "+").replace("&", "and"))
        print(message_play)

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
    global playlist_total, counter, msg, skip_song, video_length, str_msg_list, restart_time, songs, artists, token, \
        refresh_token, access_token, spotifyObject, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope, SPOTIFY_USERNAME

    # ensures a new token
    if int(time.time()) > int(restart_time):
        Refresh.refresh(ctx)
        token = spotipy.SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,
                                     redirect_uri=SPOTIPY_REDIRECT_URI, scope=scope, username=SPOTIFY_USERNAME)
        spotifyObject = spotipy.Spotify(auth_manager=token)
        restart_time = time.time() + 3300  # update token refresh timer

    if ctx.author == client.user: # checks to see if the message was sent by a bot
        return
    msg = ctx.content
    channel = ctx.author.voice.channel

    ############################ USER COMMANDS #############################
    ########################################################################
    ########################################################################

    ########### FORCE TOKEN REFRESH ############
    ############################################
    if msg.startswith('$refresh'):
        Refresh.refresh(ctx)
        token = spotipy.SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,
                                     redirect_uri=SPOTIPY_REDIRECT_URI, scope=scope, username=SPOTIFY_USERNAME)
        spotifyObject = spotipy.Spotify(auth_manager=token)
        restart_time = time.time() + 3300  # update token refresh timer

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
        songs.clear()
        artists.clear()

        # ensures a new token
        #if int(time.time()) > int(restart_time):
            #Refresh.refresh(ctx)
            #python = sys.executable
            #os.execl(python, os.path.abspath('main.py'), *sys.argv)
        await playlistplay(ctx)



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

    ############## SKIP PLAYLIST ##############
    ###########################################
    if msg.startswith('$p skip'):
        try:
            songs.clear()                               # clear playlist data
            artists.clear()                             # clear playlist data
            await stop(ctx)                             # stop audio stream

        except:
            print("Error skipping playlist")

    ################ PLAY A SONG ##############
    ###########################################
    if msg.startswith('$play'):
        try:
            await play(ctx, msg[6:])
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

    if msg.startswith('$help'):
        await help(ctx)


############################ BOT FUNCTIONS #############################
########################################################################
########################################################################



############# LIST ALL FUNCTIONS    #############
#################################################
async def help(ctx):
    music_channel = client.get_channel(965814271063781396)
    await music_channel.send('$p add [song name] - adds a song top playlist'
                             '\n$connect - connects bot to channel'
                             '\n$p create [name] - creates a playlist'
                             '\n$p list - will list all playlists'
                             '\n$play [song name] - will play a song'
                             '\n$p play - plays a playlist(must select a playlist)'
                             '\n$p select [name of playlist] - selects a playlist'
                             '\n$skip - skips a song'
                             '\n$spam [@user] - spams @\'s a user'
                             '\n$p songs - lists all songs in selected playlist'
                             '\n$p skip - skips all songs in the playlist')

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
    global songs
    global artists

    counter = 0

    if ctx.author == client.user:                                       # checks to see if the message was sent by a bot
        return

    # search playlist function call with spotify api
    a.get_playlists_songs()

    for x in songs:
        try:
            temp = str(songs[int(counter)] + " " + artists[int(counter)])
            print(temp)
            await play(ctx, temp)
            # play song function
        except:
            print('error with play')

        test = asyncio.get_running_loop()                           # wait for song to finish
        end = test.time() + video_length                            # calculate the end of the current song
        counter += 1

        while True:                                                 # while song is playing do
            print(datetime.datetime.now())                          # print time stamp
            if (test.time() + 1.0) >= end or skip_song is True:     # loop break condition
                skip_song = False                                   # reset skip condition
                break
            await asyncio.sleep(1)                                  # timeout

        print("playlist error")                                         # catch any execution errors with playlist
    discord.player.VoiceClient.stop(ctx)                                # force stop voice client


################ DOWNLOAD SONG FUNCTION #############
#####################################################
@client.event
async def download(ctx):
    global watch_link, title, video_length, count, song_name

    music_channel = client.get_channel(965814271063781396)
    channel = ctx.author.voice.channel
    voice = ctx.author.voice
    out_file = None

    print('1')                                                          # debug purposes
    yt = YouTube(str(watch_link))                                       # url input from user

    print('2')
    try:
        # get the audio stream
        audio = yt.streams.get_audio_only()
        print(audio)
        # download the audio stream to a file
        audio.download(output_path='./', filename='song.mp3')
    except:
        pass
    await music_channel.send(song_name + " will begin shortly!") # send in discord chat



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
async def play(ctx, song):
    channel = ctx.author.voice.channel
    voice = ctx.channel.guild.voice_client
    print('1')                                 # debug purposes
    a.search_song(song)
    print('2')
    await getYoutubeUrls()
    print('3')
    print('4')
    try:
        print('5')
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
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()


################ GET VIDEO DURATION #################
#####################################################
async def GetDuration():
    global watch_link, video_length
    info = requests.get(watch_link)
    info = info.text
    info = info[info.find('approxDurationMs":"')+19:]
    info = info[:info.find('"')]
    video_length = (int(info)/1000)
    print(video_length)

############# GET URL FOR SONG FUNCTION #############
#####################################################
@client.event
async def getYoutubeUrls():
    global message_play
    global watch_link
    global video_length
    global song_name
    video_ids = []

    print('1y')
    html = urllib.request.urlopen(anyascii(message_play))
    print('2y')
    response = html.read()
    print('3y')
    video_ids = re.findall(r"watch\?v=(\S{11})", str(response))
    print('4y')
    watch_link = "https://www.youtube.com/watch?v=" + video_ids[0]
    print('5y')
    vid = pytube.YouTube(watch_link)
    song_name = vid.title

    print('6y')
    await GetDuration()
    print(watch_link)

############# RESET VARIABLES FUNCTION ##############
#####################################################
@client.event
async def reset():
    global watch_link, url, title, songs, artists, count, counter, playlist_total, msg, skip_song, playlist_ID, bot_playlist, song_name, playlist_response, track_id, message_play
    url = ["", "", "", "", ""]
    watch_link = []
    title = ""
    songs = []
    artists = []
    count = 0
    counter = 0
    playlist_total = 0
    msg = ""
    playlist_ID = ""
    skip_song = False
    message_play = ""
    url = ["", "", "", "", ""]
    watch_link = []
    title = ""
    songs.clear()
    artists.clear()
    bot_playlist = []
    song_name = ""
    playlist_response = ''
    track_id = ''

a = SaveSongs()
a.call_refresh()
keep_alive()
client.run("")