#Eli Gotttlieb
#Section A
#Final Project
#This project uses the Spotify API to suggest songs
#SpotifyProject.py
#5/28/20


import requests
import numpy as np

CLIENT_ID="d16f652d5ff84d45baa7543630c521c4"
CLIENT_SECRET="b22a47d97fe942668e69aae58d5dd8db"

data = {
  'grant_type': 'client_credentials'
}

responseToken = requests.post('https://accounts.spotify.com/api/token', data=data, auth=(CLIENT_ID,CLIENT_SECRET))
accessTokenJSON=responseToken.json()
accessToken=accessTokenJSON['access_token']

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+accessToken,
}


#METHODS

#Prints the introduction
#Gets the user's choice about which feature they want to use
#Return: the user's choice
def intro():
    print("Welcome to the Spotify Song Suggester!")
    print("This program works in two ways:")
    print("\t1. Input a song and recieve similar songs given your search criteria")
    print("\t2. Input artists and recieve songs from those artists given your search criteria")
    choice=getValidNumber("How would you like to start (1 or 2)?: ",1,2,"int")
    return choice
    

#Searches for the artist that is entered by the user
#Return: the artist's ID
def getArtist():
    notValid=True
    while (notValid):
        artistName=str(input("Please input the name of an artist: "))
        params = (
            ('q', artistName),
            ('type', 'artist'),
            )
        responseArtist = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)
        artistJSON=responseArtist.json()
        if len(artistJSON['artists']['items'])!=0:
            printArtists(artistJSON['artists']['items'])
            choice=getValidNumber("Please enter the number of the artist: ",1, len(artistJSON['artists']['items']),"int")
            artistID=artistJSON['artists']['items'][choice-1]['id']
            notValid=False
        else:
            print("Could not find artist. Please try again.")
    return artistID

#Prints the related artists to the artist that is passed in
#Parameters: an artist ID
def printRelatedArtists(artistID):
    responseRA=requests.get('https://api.spotify.com/v1/artists/'+artistID+'/related-artists', headers=headers)
    responseRAJSON=responseRA.json()
    printArtists(responseRAJSON['artists'])
    
#Prints a list of artists
#Parameter: a list of artists
def printArtists(listArtists):
    print()
    #I made the choice to only print 5 artists because it looks cleaner on 
    #the screen and the artist the user is looking for is most likely in the 
    #top 5.
    if len(listArtists)>5:
        listArtists=listArtists[:5]
    for x in range(len(listArtists)):
        print(str(x+1)+". "+listArtists[x]['name'])
        

#Gets all the criteria for the search
#This includes each audio feature, as well the bottom and upper bound for the search
#for each audio feature
#Return: a tuple containing a list of the features, a list of the bottom bounds, and a list of the upper bounds
def getInfo():
    #The 2 is so that the correct amount of info is printed to the screen
    printAudioFeatures(2)
    features=np.array([])
    bottom=np.array([])
    top=np.array([])
    keepGoing=True
    x=0
    #There are 6 features to choose from
    while keepGoing and x<6:
        x=x+1
        feature=getValidFeature(x,features)
        features=np.append(features,np.array([feature]))
        bottomTop=getValue(feature)
        bottomV=bottomTop[0]
        topV=bottomTop[1]
        bottom=np.append(bottom,np.array([bottomV]))
        top=np.append(top,np.array([topV]))
        if x<6:
            keepGoing=more("Would you like to add another feature to the search?")
    return (features,bottom,top)

#Prints the audio features that are chosen from to create the search
def printAudioFeatures(ver):
    print()
    print("Here are the audio features to create your search:")
    print("Acousticness")
    print("Danceability")
    print("Energy")
    print("Instrumentalness")
    print("Tempo (BPM)")
    print("Valence (how positive a song sounds)")
    #Only print this section if the user needs to enter a range
    if ver==2:
        print()
        print("All features, except tempo, are measured between 0 and 1, with a larger")
        print("number indicating a higher value of whatever the feature it is")
        print("For example, a 0.8 value for energy would mean it is a high energy song,")
        print("while a 0.3 value for valence would mean the song does not song very positive.")
        print("Tempo is measured in beats per minute. ")

#Prompts the user to enter a feature for their search
#Return: the feature
def getFeature():
    notValid=True
    while (notValid):
        word=str(input("Please choose a feature (enter the feature in all lowercase letters): "))
        if (word=="acousticness" or word=="danceability" or word=="energy" or word=="instrumentalness" or word=="valence" or word=="tempo"):
            notValid=False
        else:
            print("Please enter a valid feature.")
    return word

#Prompts the user to enter the bottom and upper bound for the search
#Parameters: the feature
#Return: a tuple containing the bottom bound and the upper bound for the search
def getValue(feature):
    if feature=="tempo":
        #I kind of randomly chose 299 as it is VERY FAST
        bottom=getValidNumber("Please enter the bottom bound for the search (between 0 and 299 BPM): ",0,299,"float")
        top=getValidNumber("Please enter the upper bound for the search (between bottom bound and 300 BPM): ",bottom,300,"float")
    else:
        bottom=getValidNumber("Please enter the bottom bound for the search (between 0 and 0.9): ",0,0.9,"float")
        top=getValidNumber("Please enter the upper bound for the search (between bottom bound and 1): ",bottom,1,"float")
    return (bottom,top)

#Checks all of the top tracks for one artist to see if a song falls within the search criteria
#Parameters: an artist ID, a list of audio features, a list of bottom bounds, and a list of upper bounds
#Return: a list of the songs that fell within the search criteria
def getSongs(artistID,listFeatures,listBottom,listTop):
    relatedSongs=np.array([])
    params = (
        ('country','US'),
    )
    responseSongs=requests.get('https://api.spotify.com/v1/artists/'+artistID+'/top-tracks', headers=headers,params=params)
    responseSJSON=responseSongs.json()
    possibleSongs=responseSJSON['tracks']
    for x in range(len(possibleSongs)):
        isMatch=checkSong(possibleSongs[x]['id'],listFeatures,listBottom,listTop)
        if isMatch[0]:
            relatedSongs=np.append(relatedSongs,np.array([[possibleSongs[x]['name'],possibleSongs[x]['id'],isMatch[1]]]))
    return relatedSongs

#Checks to see if a song falls with the search criteria
#Parameters: a song ID, a list of audio features, a list of bottom bounds, and a list of upper bounds
#Return: true or false, whether the song falls within the criteria or not
def checkSong(songID,listFeatures,listBottom,listTop):
    responseSong=requests.get('https://api.spotify.com/v1/audio-features/'+songID, headers=headers)
    songJSON=responseSong.json()
    songFeatures = np.array([])
    valid=True
    ii=0
    while (ii<len(listFeatures) and valid):
        valid=checkFeature(songJSON[listFeatures[ii]],listBottom[ii],listTop[ii])
        ii=ii+1
    return (valid, songJSON)

#Checks to see if the actual value of the audio feature falls within the range
#Parameters: the actual value, the bottom bound, and the upper bound        
def checkFeature(actualValue, bottom, top):
    if (actualValue>=bottom and actualValue<=top):
        return True
    else:
        return False

#Prints the songs that fell within the criteria for one artist
#Parameters: an artist ID, a list of songs        
def printFinalSongs(artistID,songs):
    if len(songs)>0:
        responseArtist=requests.get('https://api.spotify.com/v1/artists/'+artistID, headers=headers)
        artistJSON=responseArtist.json()
        print("\nSongs by "+artistJSON['name']+":")
        ii=0
        for ii in range(len(songs)):
            print("\t"+str(ii+1)+". "+songs[ii][0])
  
    


#Prompts the user to enter a song and its artist
#If the song is by more than one artist, the user can choose multiple artists for the 
#search to be centered around
#Return: a tuple containing the song ID and the artist (or artists) ID(s)
def getSong():
    notValid=True
    while (notValid):
        songName=str(input("Please enter the name of a song: "))
        artistName=str(input("Please enter the name of the artist: "))
        params = (
        ('q', 'track:'+songName+' artist:'+artistName),
        ('type', 'track'),
        )
        searchSong=requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)
        ssJSON=searchSong.json()
        if len(ssJSON['tracks']['items'])!=0:
            num=printAllSongs(ssJSON['tracks']['items'])
            choice=getValidNumber("Please enter the number of the song: ",1,num,"int")
            songID=ssJSON['tracks']['items'][choice-1]['id']
            notValid=False
        else:
            print("Could not find any song to match you requests.")
    if len(ssJSON['tracks']['items'][choice-1]['artists'])>1:
        artistIDs=chooseArtists(ssJSON['tracks']['items'][choice-1]['artists'])
    else:
        artistIDs=[ssJSON['tracks']['items'][choice-1]['album']['artists'][0]['id']]
    return (songID,artistIDs)

#Lets the user choose the artists they want the search to be centered around 
#if the song is by multiple artists    
#Parameters: the list of all the artists the song is by
#Return: the list of the artists the user has chosen
def chooseArtists(artistList):
    printArtists(artistList)
    print("This track has multiple artists associated with it.")
    print("Please choose one or more artists for the search to be centered around.")
    artists=[]
    keepGoing=True
    x=0
    while keepGoing and x<len(artistList):
        x=x+1
        notValid=True
        while notValid:
            choice=getValidNumber("Please enter the number of the artist: ",1,len(artistList),"int")
            if x>1 and (artistList[choice-1]['id'] in artists):
                print("Artist already chosen. Try again.")
            else:
                notValid=False
                artists.append(artistList[choice-1]['id'])
                if x<len(artistList):
                    keepGoing=more("Would you like to add another artist to the search?")
    return artists
 

#Prints the songs that are generated by the search call to the Spotify API
#Only prints songs that have a different artist than the first song (this is 
#because usually the same song will come up multiple times just as different versions,
#like a live version, so this is in place try to only print out different songs)
#Parameters: a list of the songs that have been generated by the search
#Return: the number of songs that were printed   
def printAllSongs(listSongs):
    number=1
    print()
    print("1. "+listSongs[0]['name']+" by "+listSongs[0]['artists'][0]['name'])
    for x in range(len(listSongs)-1):
        if (listSongs[x+1]['artists'][0]['name']!=listSongs[0]['artists'][0]['name']):
            number=number+1
            print(str(number)+". "+listSongs[x+1]['name']+" by "+listSongs[x+1]['artists'][0]['name'])
    return number
        

#Creates the list of features, bottom bound, and upper bound for the search
#Gives the user an option to personalize their search (choose the audio features),
#or use the general search (more basic search for related songs because there is a good 
#number of audio features included in the search)
#Parameters: a song ID
#Return: a tuple containing a list of the features, the bottom bounds, and the upper bounds
def createInfo(songID):
    songInfo=requests.get('https://api.spotify.com/v1/audio-features/'+songID, headers=headers)
    songInfoJSON=songInfo.json()
    
    acousticness=songInfoJSON['acousticness']
    danceability=songInfoJSON['danceability']
    energy=songInfoJSON['energy']
    instrumentalness=songInfoJSON['instrumentalness']
    tempo=songInfoJSON['tempo']
    valence=songInfoJSON['valence']
    
    features=np.array([])
    bottom=np.array([])
    top=np.array([])
    print()
    print("Would you like to personalize your search, or do the generic search?")
    print("1. Personalize")
    print("2. Generic")
    choice=getValidNumber("Please enter your choice: ",1,2,"int")
    if choice==1:
        #The 1 is so that the correct amount of information is printed on the screen
        printAudioFeatures(1)
        keepGoing=True
        x=0
        #There are 6 features
        while keepGoing and x<6:
            x=x+1
            feature=getValidFeature(x,features)
            features=np.append(features,np.array([feature]))
            bottom=np.append(bottom,np.array([songInfoJSON[feature]]))
            top=np.append(top,np.array([songInfoJSON[feature]]))
            if x<6:
                keepGoing=more("Would you like to add another feature to the search?")
    else: 
        features=np.array(["tempo","energy","valence","acousticness", "danceability"])
        bottom=np.array([tempo, energy,valence, acousticness, danceability])
        top=np.array([tempo, energy,valence, acousticness, danceability])
    #The idea behind this next section is that for every feature in the search, the search range
    #for each feature gets bigger in order to actually get results. This is because if we were
    #searching with a bunch of features and every search range was really small, there probably 
    #wouldn't be any matches. 
    for ii in range(len(features)):
        bottomTop=widenRange(features,bottom,top)
    bottom=bottomTop[0]
    top=bottomTop[1]
    return (features, bottom, top)

#Widens the search range for each feature in the search
#Parameters: a list of features, a list of bottom bounds, and a list of upper bounds
#Return: a tuple containing the new bottom and upper bounds
def widenRange(features,bottom,top):
    #From testing this program a bunch of times, I have come to these numbers as good
    #numbers to widen the range so that most of the time enough songs are printed out, 
    #yet the songs still are similar to the song entered.
    for x in range(len(features)):
        if features[x]=="tempo":
            bottom[x]=bottom[x]-4
            top[x]=top[x]+4
        else:
            bottom[x]=bottom[x]-0.035
            top[x]=top[x]+0.035
    return (bottom,top)
    
#Gets all of the related artists
#Parameters: an artist ID
#Returns: a list containing the related artist IDs
def getAllRelatedArtists(artistID):
    relatedArtists=requests.get('https://api.spotify.com/v1/artists/'+str(artistID)+'/related-artists', headers=headers)
    rAJSON=relatedArtists.json()
    relatedArtistIDs=np.array([])
    if (len(rAJSON['artists'])==0):
        print("Sorry, there are no related artists to center the search around. Please start over.")
    else:
        for x in range(len(rAJSON['artists'])):
            relatedArtistIDs=np.append(relatedArtistIDs,np.array([rAJSON['artists'][x]['id']]))
    return relatedArtistIDs
    
#Gets a valid audio feature for the search
#Parameters: the number of features in the search and the list of features in the search
#Return: the audio feature
def getValidFeature(x, features):
    notValid=True
    while notValid:
        feature=getFeature()
        if x>1 and feature in features:
            print("Feature already in search.")
        else:
            notValid=False
    return feature
    
#Prompts the user to enter a valid number
#Parameters: a prompt, a minimum number, a maximum number, and the type (int or float)
#Return: the valid number
def getValidNumber(prompt,minNum,maxNum, typeNum):
    notValid=True
    while (notValid):
        try:
            if typeNum=="int":
                toReturn=int(input(prompt))
            else:
                toReturn=float(input(prompt))
            if (toReturn<=maxNum and toReturn>=minNum):
                notValid=False
            else:
                print("Please enter a valid number.")
        except ValueError:
            print("Please enter a valid number.")
    return toReturn

#Used to see if the user wants to add something else to their search
#Parameters: the prompt
#Return: true or false, whether they want to or not
def more(prompt):
    print(prompt)
    num=getValidNumber("1 for yes, 2 for no: ",1,2,"int")
    if num==1:
        return True
    else:
        return False 
        
#Coordinates getting the info for the route that has the user enter a song    
#Return: a tuple containing the info for the search as well as the list of artist IDs
#whose songs are going to be checked
def songBased():
    notValid=True
    while (notValid):
        songArtistIDs=getSong()
        mainArtists=songArtistIDs[1]
        relatedArtistIDs=np.array([])
        for i in range(len(mainArtists)):
            newRelatedArtistIDs=getAllRelatedArtists(mainArtists[i])
            relatedArtistIDs=np.append(relatedArtistIDs,newRelatedArtistIDs)
        if len(relatedArtistIDs)!=0:
            notValid=False
    info=createInfo(songArtistIDs[0])
    return (info,relatedArtistIDs)
 
#Coordinates getting the info for the route that has the user enter artists 
#Return: a tuple containing the info for the search as well as the list of artist IDs
#whose songs are going to be checked  
def artistBased():
    relatedArtistIDs=np.array([])
    keepGoing=True
    ii=0
    newID=""
    while keepGoing:
        ii=ii+1
        if ii>1:
            print("Here are some related artists you might want to add:")
            printRelatedArtists(newID)
        notValid=True
        while notValid:
            newID=getArtist()
            if ii>1 and (newID in relatedArtistIDs):
                print("Artist already added in search.")
            else:
                notValid=False
        relatedArtistIDs=np.append(relatedArtistIDs,np.array([newID]))
        keepGoing=more("Would you like to add another artist to your search?")
    info=getInfo()
    return (info,relatedArtistIDs)

def adjustPreferences(songs,features,bottom,top):
    keepGoing=True
    likedSongs=np.array([])
    while (keepGoing):
        songName=str(input("Enter a song that you liked: "))
        currentlen = len(likedSongs)
        for x in songs:
            if songName==x[0]:
                likedSongs = np.append(likedSongs, np.array([x[2]]))
        if (len(likedSongs)==currentlen):
            print("Sorry - couldn't find anything. Try again.")
        else:
            choice=getValidNumber("Would you like to add another(1 - yes, 2 - no)?: ",1,2,"int")
            if (choice==2):
                keepGoing=False
    
        
                

#MAIN PROGRAM
startingChoice=intro()
if (startingChoice==1):
    allInfo=songBased()
else:
    allInfo=artistBased()
    
info=allInfo[0]
relatedArtistIDs=allInfo[1]   
features=info[0]
bottom=info[1]
top=info[2]
total=0
while total<1:
    for x in range(len(relatedArtistIDs)):
        relatedSongs=getSongs(relatedArtistIDs[x],features,bottom,top)
        printFinalSongs(relatedArtistIDs[x],relatedSongs)
        if len(relatedSongs)!=0:
            total=total+1
    if total==0:
        if startingChoice==1:
            updatedRange=widenRange(features,bottom,top)
            bottom=updatedRange[0]
            top=updatedRange[1]
        else:
            print("Sorry, there were no songs that matched your search criteria.")
            total=2
            
if (startingChoice==1) and (len(features)>2):
    adjustPreferences(relatedSongs,features,bottom,top)
