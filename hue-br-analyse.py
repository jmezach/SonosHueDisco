import urllib
from urllib import request
from random import randint 
import base64,requests,json,time,datetime

"""
Hue Sonos Analyser by Harry Plant 2015

This program changes the hue, brightness and tempo of Philips Hue lights depending on the energy and danceability of the track,
as reported by Echonest.

Requirements:

*Philips Hue bridge and at least one Hue Light (http://www2.meethue.com/en-gb/)
*At least one Sonos player (http://www.sonos.com/)
*Python 3 (I have it installed on my Raspberry Pi)
*Echonest api key (obtainable at https://developer.echonest.com/ - click 'Get an API Key')
*node-sonos-http-api (https://github.com/jishi/node-sonos-http-api)

change the following variables to match your setup:

zone is the name of the sonos player you will be listening to
my_list is an array of the hue lights you want to control
sonosinfo is the address of the node-sonos-http-api server
hue_bridge is the address and KEY that you use to control the hue
echonest_apikey is the key you obtained from echonest

I have used this program with success (great parties) on multiple occasions but do not accept 
responsibility for any loss or damage caused by using this code.

"""

zone = 'Woonkamer'
my_list = ['2', '3', '4']
sonosinfo = 'http://localhost:5005/'
hue_bridge = 'http://192.168.1.73/api/oy5fxii4S2OzWkhS6g86Hs-UHh6Zn175vRQv80RG/'
spotify_clientid = 'a4a437a7dba94c4eb8b3b5b6bea53dd9'
spotify_clientsecret = '2d5b9d2f23e0436190c156348a3e16d7'

"""
MAIN PROGRAM BELOW, YOU DON'T NEED TO CHANGE ANYTHING FROM HERE
"""

currenttrack = 'No track'
min_bri = 100
max_bri = 100
off_chance = 0
secs_waited = 0
secs_to_wait = 10
sat = 100
tt = 10
trackfound = 1
std_assumptions = 0
bearer_token = 'unknown'

for r in range(1,999999):
    
    secs_waited = secs_waited + 0.5
    try:
        req = request.urlopen(sonosinfo + zone + '/state')
    except:
        req = {    "volume": 0,    "zonePlayMode": {        "crossfade": false,        "repeat": false,        "shuffle": false    },    "zoneState": "PLAYING",    "mute": false,    "currentTrack": {        "album": "(What's The Story) Morning Glory? (Remastered) [Deluxe Version]",        "radioShowMetaData": "",        "title": "Roll With It - Remastered",        "artist": "Oasis",        "uri": "x-sonos-spotify:spotify%3atrack%3a4lB8SqU4KfzB0QjfEIAssb?sid=9&flags=8224&sn=4",      "streamInfo": "",        "albumArtURI": "/getaa?s=1&u=x-sonos-spotify%3aspotify%253atrack%253a4lB8SqU4KfzB0QjfEIAssb%3fsid%3d9%26flags%3d8224%26sn%3d4",        "duration": 240,        "type": "track",        "absoluteAlbumArtURI": "http://192.168.1.76:1400/getaa?s=1&u=x-sonos-spotify%3aspotify%253atrack%253a4lB8SqU4KfzB0QjfEIAssb%3fsid%3d9%26flags%3d8224%26sn%3d4"    },    "elapsedTime": 170,    "nextTrack": {        "album": "Greatest Hits",        "absoluteAlbumArtURI": "http://192.168.1.76:1400/getaa?s=1&u=x-sonos-spotify%3aspotify%253atrack%253a4P7UhffUpi9UnRM7fLNBe0%3fsid%3d9%26flags%3d8224%26sn%3d4",        "artist": "The Cure",        "title": "Just Like Heaven",        "uri": "x-sonos-spotify:spotify%3atrack%3a4P7UhffUpi9UnRM7fLNBe0?sid=9&flags=8224&sn=4",        "albumArtURI": "/getaa?s=1&u=x-sonos-spotify%3aspotify%253atrack%253a4P7UhffUpi9UnRM7fLNBe0%3fsid%3d9%26flags%3d8224%26sn%3d4"    },    "trackNo": 6,    "playerState": "PLAYING",    "elapsedTimeFormatted": "02:50"}
        print("An error was trapped.")
    finally:

        encoding = req.headers.get_content_charset()
        obj = json.loads(req.read().decode(encoding))
        
        """
        print(json.dumps(obj,indent=4))
        """
        
        if obj['playbackState'] == 'PAUSED_PLAYBACK' or obj['playbackState'] == 'STOPPED':
            print('Player has stopped playing.  Returning lights to white and exiting program.')
            my_list_len = len(my_list)
            for i in range(0,my_list_len):
                hue = 10000
                bri = 200
                sat = 50
                tt = 50
                payload = '{"on":true,"sat":' + str(sat) + ',"bri":' +  str(bri) + ',"hue":' + str(hue) + ',"transitiontime":' +str(tt) + '}'
                """
                print(payload)
                """
                r = requests.put(hue_bridge + "lights/" + my_list[i] + "/state",data=payload)
            exit()

        track = obj['currentTrack']['title']
        artist = obj['currentTrack']['artist'] 	
        elapsedtime = obj['elapsedTime']

        if track == currenttrack:
            """
            print('Waited ' + str(secs_waited) + ' out of ' + str(secs_to_wait))
            """
        if track != currenttrack:
            std_assumptions = 0
            print('This is a new track!')
            print('Now playing : ' + track + ' by '+ artist + ".")
            requeststring = 'https://api.spotify.com/v1/search?q=artist:' + urllib.parse.quote(artist) + '%20title:' + urllib.parse.quote(track) + '&type=track'
            """
            print(requeststring)
            """
            req = request.urlopen(requeststring)
            encoding = req.headers.get_content_charset()
            obj = json.loads(req.read().decode(encoding))
            """
            print(obj)
            """
            if not obj['tracks']['items']:
                std_assumptions = 1            
                print('Song not in database - using standard assumptions')
            
            if std_assumptions == 0:
                songid = obj['tracks']['items'][0]['id']

                """
                print(songid)
                """

                requeststring = 'https://api.spotify.com/v1/audio-features/' + songid
                """
                print(requeststring)
                """
                req = request.Request(requeststring)
                req.add_header('Authorization', 'Bearer ' + bearer_token)
                
                try:
                    res = request.urlopen(req)
                except urllib.error.HTTPError as e:
                    if (e.code == 401):
                        print('Unauthorized. Retrieving new token...')
                        authreq = request.Request('https://accounts.spotify.com/api/token')
                        authbasic = spotify_clientid + ':' + spotify_clientsecret
                        authreq.add_header('Authorization', 'Basic ' + base64.b64encode(authbasic.encode()).decode())
                        body = { 'grant_type': 'client_credentials' }
                        body = bytes( urllib.parse.urlencode(body).encode())
                        authres = request.urlopen(authreq, body)
                        encoding = authres.headers.get_content_charset()
                        print('Got encoding: ' + encoding)
                        token = json.loads(authres.read().decode(encoding))
                        bearer_token = token['access_token']
                        req = request.Request(requeststring)
                        req.add_header('Authorization', 'Bearer ' + bearer_token)
                        res = request.urlopen(req)
                        print('Got new token, continuing...')
                
                encoding = res.headers.get_content_charset()
                obj = json.loads(res.read().decode(encoding))
                if not obj['danceability']:
                    print('Although song was in database, there is no energy and danceability data.  Using standard assumptions for this track.')
                    std_assumptions = 1
    
                if std_assumptions == 0:

                    print(obj)
        
                    dancepercent = int((obj['danceability'])*100)
                    energypercent = int((obj['energy'])*100)
                    pulserate = obj['tempo']
                    print('Danceability is '+str(dancepercent) + '% and energy is ' + str(energypercent) + '% with a tempo of '+str(pulserate) +'bpm.')
                    currenttrack = track

            if std_assumptions == 1:
        
                dancepercent = 50
                energypercent = 50
                pulserate = 100
                print('Danceability is '+str(dancepercent) + '% and energy is ' + str(energypercent) + '% with a tempo of '+str(pulserate) +'bpm.')
                currenttrack = track

            if pulserate < 100:
                secs_to_wait = 10
                tt = 10
 
            if pulserate > 99 and pulserate < 120:
                secs_to_wait = 5
                tt = 7
 
            if pulserate > 119 and pulserate < 160:
                secs_to_wait = 2
                tt = 3

            if pulserate > 159:
                secs_to_wait = 0.5
                tt = 0
            """
        
            secs_to_wait = int((pulserate/60)*2)
            """
            if energypercent < 20:
                sat = 50
 
            if energypercent > 19 and energypercent < 40:
                sat = 100

            if energypercent > 39 and energypercent < 60:
                sat = 120

            if energypercent > 59 and energypercent < 80:
                sat = 170     

            if energypercent > 59 and energypercent < 80:
                sat = 200
        
            if energypercent > 79:
                sat = 255

            if dancepercent < 20:
                max_bri = 60
                min_bri = 40
                off_chance = 100
 
            if dancepercent > 19 and dancepercent < 40:
                max_bri = 100
                min_bri = 80
                off_chance = 1000

            if dancepercent > 39 and dancepercent < 60:
                max_bri = 150
                min_bri = 90
                off_chance = 900

            if dancepercent > 59 and dancepercent < 80:
                max_bri = 200
                min_bri = 100   
                off_chance = 800

            if dancepercent > 59 and dancepercent < 80:
                max_bri = 255
                min_bri = 150
                off_chance = 800

            if dancepercent > 79:
                max_bri = 255
                min_bri = 200
                off_chance = 600

            my_list_len = len(my_list)
            for i in range(0,my_list_len):
                hue = randint(0,65000)
                bri = randint(min_bri,max_bri)
                offnow = randint(0,1000)
                if offnow > off_chance:
                    payload = '{"on":false}'
                if offnow <= off_chance:
                    payload = '{"on":true,"sat":' + str(sat) + ',"bri":' +  str(bri) + ',"hue":' + str(hue) + ',"transitiontime":' +str(tt) + '}'
                """
                print(payload)
                """
                r = requests.put(hue_bridge + "lights/" + my_list[i] + "/state",data=payload)
            secs_waited = 0
         
        if secs_waited >= secs_to_wait:
            my_list_len = len(my_list)
            for i in range(0,my_list_len):
                hue = randint(0,65000)
                bri = randint(min_bri,max_bri)
                offnow = randint(0,1000)
                if offnow > off_chance:
                    payload = '{"on":false}'
                if offnow <= off_chance:
                    payload = '{"on":true,"sat":' + str(sat) + ',"bri":' +  str(bri) + ',"hue":' + str(hue) + ',"transitiontime":' +str(tt) + '}'
                """
                print(payload)
                """
                r = requests.put(hue_bridge + "lights/" + my_list[i] + "/state",data=payload)
            secs_waited = 0

        time.sleep(0.5)
    


