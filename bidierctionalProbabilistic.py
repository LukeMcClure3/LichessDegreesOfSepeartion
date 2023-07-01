import requests, json, time, math , random

apiCalls = 0
gamesAnylized = 0
class node:
    def __init__(self, name, rank, games = []) -> None:
        self.name = name
        self.rank = rank
        self.games = games
    def __repr__(self) -> str:
        return "" + self.name + " " + str(self.rank) + " " + str(self.games)
def getRank1(): 
    perfType = "blitz"
    responseTopPlayer = requests.get(f"https://lichess.org/api/player/top/1/{perfType}")
    global apiCalls
    apiCalls += 1
    #print(responseTopPlayer)
    if responseTopPlayer.status_code == 429:
        quit()
    topPlayerJSON = responseTopPlayer.json()
    topPlayer = topPlayerJSON['users'][0]["username"]
    rank = topPlayerJSON['users'][0]["perfs"][perfType]["rating"]
    return (topPlayer,rank)

def getStartingPlayer():
    return input("player?")

def getGamesPlayer(player, numGames = 200):
    global apiCalls , gamesAnylized
    r = requests.get(
        f"https://lichess.org/api/games/user/{player}",
        params={ "rated" :"true" , "max" :numGames},
        headers={"Accept": "application/x-ndjson"}
    )
    if r.status_code == 429:
        print(r.status_code , "rate limited, waiting 60 seconds")
        time.sleep(60)
        print(player)
        r = requests.get(
            f"https://lichess.org/api/games/user/{player}",
            params={ "rated" :"true" , "max" :numGames},
            headers={"Accept": "application/x-ndjson"}
        )
        apiCalls += 1
        print(apiCalls)
    if r.status_code >= 400:
        return ("error" , [])
    
   

    r_text = r.content.decode("utf-8")
    games = [json.loads(s) for s in r_text.split("\n")[:-1]]

    gamesAnylized+= len(games)
    apiCalls += 1
    print(apiCalls , "requests for information and" , gamesAnylized , "games analyzed")

    return games

#exapnds individual nodes returning a list of their children
def getChildrenNodes(n , foo,checklst):
    #low list - looking for node to beat poi - we want poi to lose - oposite of winner color - swap balck - white 
    #foo = lambda x : ("black" if x == "white" else "white") if type == "low" else x
    # checklst is 
    rtn = []
    #API CALLS
    games  = getGamesPlayer(n.name, 200)
    # print(games[3])
    # # \apicalls
    # print(len(games))
    # countinggames = 0 
    for game in games:
        # countinggames+=1
        # print(countinggames)
        # if game == games[3]:
        #     print("pass")
        skipgame = False
        try: 
            game["winner"] #no winner 
            game["players"][foo(game["winner"])]["user"] #user is bot or something
        except:
            skipgame = True
        if not skipgame:
            #no winner #user is bot or something
            
            #print(game)
            #print(game["winner"])
            playerOfInterest = game["players"][foo(game["winner"])]["user"]["name"]
            #print(n.name , playerOfInterest , n.name == playerOfInterest)
            if playerOfInterest != n.name:
                for x in checklst:
                    if x.name == playerOfInterest:
                        #create solution lst.
                        x.games.reverse()
                        sol = n.games + [game["id"]] + x.games
                        #print(sol)
                        return ("solution" , sol)
            # for x in checklstrepeats:
            #     if x.name == playerOfInterest:
            #         break
            # else:
            #     break

            #get stattistics
            rating = game["players"][foo(game["winner"])]["rating"]
            newGames = n.games.copy()
            newGames.append(game["id"])
            rtn.append(node(playerOfInterest, rating, newGames))
    #print("retur" , rtn)
    return ("continue" , rtn)
            
def p(twodarray):
    #pick node based on p(d) formula
    probs = []
    for x in range (len(twodarray)):
        alpha = -1
        numerator = math.e**(alpha * x)
        denominator = 0
        for y in range(len(twodarray)):
            denominator += math.e ** (alpha * y)
        probs.append(numerator/denominator)
    #print(probs)
    choices = [x for x in range(len(probs))]
    random_number = random.choices(choices, probs)[0]
    if len(twodarray[random_number]) == 0:
        del twodarray[random_number]
        return p(twodarray)
    else:
        ChosenNode = twodarray[random_number][0]
    del twodarray[random_number][0]
    #print(ChosenNode , random_number)
    return (ChosenNode , twodarray, random_number)

#setup the highlist or lowlist for expansion
def getPath(lowLst , highLst):
    lowVisited = [] 
    highVisited = [] 
    while True:
        key = lambda n : n.rank
        for l in range(len(lowLst)):
            lowLst[l].sort(key = key , reverse = True) 
        for l in range(len(highLst)):
            highLst[l].sort(key = key) 
        
        pickedVal,lowLst,picked_depth= p(lowLst)
        if pickedVal.name not in [x.name for x in lowVisited]:
            foo = lambda x : ("black" if x == "white" else "white") 
            status , package = getChildrenNodes(pickedVal, foo, highVisited ) 
            # if len(package) == 0:
            #     print(pickedVal,lowLst,picked_depth)
            #     print(lowVisited)
            lowVisited.append(pickedVal)
            if status == "solution":
                return package
            else:
                if len(lowLst) == picked_depth+1:
                    lowLst.append([])
                lowLst[picked_depth+1] += package

        pickedVal,highLst,picked_depth= p(highLst)
        if pickedVal.name not in [x.name for x in highVisited]:
            foo = lambda x : x
            status , package = getChildrenNodes(pickedVal, foo, lowVisited) 
            #if len(package) == 0:
                #print(pickedVal,lowLst,picked_depth)
                #print(lowVisited)
            highVisited.append(pickedVal)
            if status == "solution":
                return package
            else:
                if len(highLst) == picked_depth+1:
                    highLst.append([])
                highLst[picked_depth+1] += package


def main():
    t1 = time.time()
    #aerodaktil
    #Cant_Stop18
    name , rank = getRank1()
    goal = node(name,rank)
    sp = getStartingPlayer()
    random.seed(sp)
    start = node(sp , 0)
    path = getPath([[start]] , [[goal]])
    t2 = time.time()
    print("solution found!" , "path length:", len(path) , "time elapsed:" , f"{t2-t1:.2f}" , "seconds")
    for x in path:
        print("https://lichess.org/" + x)
main()

# foo = lambda x : ("black" if x == "white" else "white")
# foo = lambda x : x
# print("\n\n")
# print (getChildrenNodes(node("SaySomething12", 0) , foo , []))