from idlelib.iomenu import encoding
from random import random

import uvicorn
from fastapi import FastAPI
from enum import Enum
import json
import ssl
import math
app = FastAPI()
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('C:/Certbot/live/kenjietsu.com/fullchain.pem', keyfile='C:/Certbot/live/kenjietsu.com/privkey.pem')



class PlayerName(str, Enum):
    angeles = "angeles"
    ethan = "ethan"
    kenji = "kenji"

class Locations(str, Enum):
    anoia = "anoia"
    bages = "bages"
    barcelones = "barcelones"
    garraf = "garraf"
    llobregat = "llobregat"
    maresme = "maresme"
    occidental = "occidental"
    oriental = "oriental"
    osona = "osona"
    penedes = "penedes"




@app.get("/api/player/{player_id}")
async def root(player_id: str):
    if player_id not in PlayerName:
        return {"message": "Invalid Player"}
    player = open(f"./players/{player_id}.json", "r")
    data = json.load(player)
    player.close()
    return data




@app.put("/api/coins/{player_id}")
async def root(player_id: str, coins: int):
    if player_id not in PlayerName:
        return {"message": "Invalid Player"}
    await change_coins(player_id, coins)
    return {"message": "Coins added"}

@app.get("/api/locations/{location}")
async def root(location: str):
    if location not in Locations:
        return {"message": "Invalid Location"}
    with open(f"./locations/locations.json") as loc:
        data = json.load(loc)
        return data["locations"][location]

@app.get("/api/locations")
async def root():
    with open(f"./locations/locations.json") as loc:
        data = json.load(loc)
        return data["locations"]

@app.put("/api/init")
async def root():
    with open(f"./locations/locations.json", "r+") as loc:
        data = json.load(loc)
        for location in data["locations"]:
            data["locations"][location]["stake"]["angeles"] = 0
            data["locations"][location]["stake"]["ethan"] = 0
            data["locations"][location]["stake"]["kenji"] = 0

        loc.seek(0)
        json.dump(data, loc, indent=4)
        loc.truncate()
    await initplayers("angeles")
    await initplayers("ethan")
    await initplayers("kenji")

    return {"message": "Initialized"}
async def initplayers(player_id: str):
    with open(f"./players/{player_id}.json", "r+") as player:
        data = json.load(player)
        data["coins"] = 1000
        data["inChallenge"] = False
        player.seek(0)
        json.dump(data, player, indent=4)
        player.truncate()


@app.put("/api/location/stake/{location}")
async def root(location: str, player_id: str, coins: int):
    if location not in Locations:
        return {"message": "Invalid Location"}
    if player_id not in PlayerName:
        return {"message": "Invalid Player"}

    # remove coins from player
    await change_coins(player_id, -coins)
    # add stake to location
    with open(f"./locations/locations.json", "r+") as loc:
        data = json.load(loc)
        data["locations"][location]["stake"][player_id] += coins
        loc.seek(0)
        json.dump(data, loc, indent=4)
        loc.truncate()



    return {"message": "Stake added"}

@app.put("/api/init/challenges")
async def root():
    for location in Locations:
        # open every location file
        with open(f"./locations/challenges/{location.name}.json", "r+") as loc:
            data = json.load(loc)
            for i in range(4):
                # random challenge from 1-63
                randomchallenge = math.ceil(random() * 63)

                # check if challenge already exists
                while randomchallenge in data["challenges"]:
                    randomchallenge = math.ceil(random() * 63)

                # change 21, 23, 25, 26, 27, 38, 39, 48, to have a 1 at a beggining
                if randomchallenge == 21 or randomchallenge == 23 or randomchallenge == 25 or randomchallenge == 26 or randomchallenge == 27 or randomchallenge == 38 or randomchallenge == 39 or randomchallenge == 48:
                    randomchallenge = 100 + randomchallenge

                if randomchallenge == 33 or randomchallenge == 34 or randomchallenge == 35 or randomchallenge == 40:
                    randomchallenge = 200 + randomchallenge

                if randomchallenge == 4:
                    randomchallenge = 63


                data["challenges"][i]["id"] = randomchallenge

                data["challenges"][i]["completed"] = False
                for player in PlayerName:
                    data["challenges"][i]["apuestas"][player] = 0

            loc.seek(0)
            json.dump(data, loc, indent=4)
            loc.truncate()

    return {"message": "Challenges initialized"}

@app.put ("/api/challenge/apuesta/{location}")
async def root(location: str, player_id: str, coins: int, challenge_id: int):
    if location not in Locations:
        return {"message": "Invalid Location"}
    if player_id not in PlayerName:
        return {"message": "Invalid Player"}

    with open(f"./locations/challenges/{location}.json", "r+") as loc:
        data = json.load(loc)
        if data["challenges"][challenge_id]["completed"]:
            return {"message": "Challenge already completed"}
        if data["challenges"][challenge_id]["apuestas"][player_id] != 0:
            return {"message": "Already betted"}
        data["challenges"][challenge_id]["apuestas"][player_id] = coins
        loc.seek(0)
        json.dump(data, loc, indent=4)
        loc.truncate()
    await change_coins(player_id, -coins)

    return {"message": "Bet added"}

async def change_coins(player_id: str, coins: int):
    with open(f"./players/{player_id}.json", "r+") as player:
        data = json.load(player)
        data["coins"] += coins
        player.seek(0)
        json.dump(data, player, indent=4)
        player.truncate()

@app.get("/api/challenge/{location}")
async def root(location: str, challengen: int):
    if location not in Locations:
        return {"message": "Invalid Location"}
    with open(f"./locations/challenges/{location}.json") as loc:
        data = json.load(loc)
        challengeID = data["challenges"][challengen]["id"]
        with open(f"./challenges/{challengeID}.json", encoding="utf-8") as challenge:
            challenge_data = json.load(challenge)
            return challenge_data



@app.put("/api/challenge/complete/{location}")
async def root(location: str, challenge_id: int, player_id: str, success: bool):
    if location not in Locations:
        return {"message": "Invalid Location"}
    if player_id not in PlayerName:
        return {"message": "Invalid Player"}

    with open(f"./locations/challenges/{location}.json", "r+") as loc:
        data = json.load(loc)
        if data["challenges"][challenge_id]["completed"]:
            return {"message": "Challenge already completed"}
        if data["challenges"][challenge_id]["apuestas"][player_id] == 0:
            return {"message": "No bet found"}
        if success:
            with open(f"./challenges/{data['challenges'][challenge_id]['id']}.json", "r") as challenge:
                challenge_data = json.load(challenge)
                multiplier = challenge_data["multiplier"]
                total_coins =  math.ceil(data["challenges"][challenge_id]["apuestas"][player_id] * multiplier)
        else:
            total_coins = 0
        data["challenges"][challenge_id]["completed"] = True

        with open(f"./players/{player_id}.json", "r+") as player_id:
            player_data = json.load(player_id)
            player_data["coins"] += total_coins
            player_id.seek(0)
            json.dump(player_data, player_id, indent=4)
            player_id.truncate()

        loc.seek(0)
        json.dump(data, loc, indent=4)
        loc.truncate()
    return {"message": "Challenge completed"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0",
                port=443, ssl_version=ssl.PROTOCOL_TLS, ssl_certfile="C:/Certbot/live/kenjietsu.com/fullchain.pem", ssl_keyfile="C:/Certbot/live/kenjietsu.com/privkey.pem", reload=True)
