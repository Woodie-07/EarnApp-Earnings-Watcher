from earnapp import earnapp
import requests, time
from datetime import datetime, timedelta

from log import *
from balanceUpdate import sendBalanceUpdate
from config import *

version = "v0.0.1"
state = "ALPHA"


# use GitHub API to get latest version
def getLatestVersion() -> str:
    url = "https://api.github.com/repos/Woodie-07/EarnApp-Earnings-Watcher/release"
    response = requests.get(url)
    data = response.json()
    return data["tag_name"]

def retrieveData(user: earnapp.User) -> dict:
    retrievedInfo = {}

    doneUserData = False
    doneMoney = False
    doneDevices = False
    doneTransactions = False
    doneAppVersions = False
    while True:
        try:
            if not doneUserData:
                retrievedInfo["userData"] = user.userData()
                doneUserData = True
            if not doneMoney:
                retrievedInfo["money"] = user.money()
                doneMoney = True
            if not doneDevices:
                retrievedInfo["devices"] = user.devices()
                doneDevices = True
            if not doneTransactions:
                retrievedInfo["transactions"] = user.transactions()
                doneTransactions = True
            if not doneAppVersions:
                retrievedInfo["appVersions"] = user.appVersions()
                doneAppVersions = True
            break
        except earnapp.IncorrectTokenException:
            error("Incorrect token: " + token)
        except earnapp.RatelimitedException:
            warning("Ratelimited, waiting " + str(cfg["ratelimitWait"]) + " seconds...")
            time.sleep(cfg["ratelimitWait"])

    return retrievedInfo

cfg = loadConfig()
validation = validateConfig(cfg)
if validation != "Config file is correct.":
    error(validation)

info("Config loaded.")

# check for updates
info("Checking for updates...")
try:
    latestVersion = getLatestVersion()
    if version != latestVersion:
        warning("An update is available, you have " + version + " and the latest is " + latestVersion)
    else:
        info("You have the latest version.")
except:
    warning("Failed to get latest version.")


# create an EarnApp user object for every token
info("Creating EarnApp user objects...")
users = []
for token in cfg["tokens"]:
    user = earnapp.User()
    try:
        user.login(token)
    except earnapp.IncorrectTokenException:
        error("Incorrect token: " + token)

    if len(cfg["webhookURLs"]) == 1:
        webhookURLs = [cfg["webhookURLs"][0]]
    if len(cfg["webhookURLs"]) == len(cfg["tokens"]):
        webhookURLs = [cfg["webhookURLs"][len(users)]]
    else:
        webhookURLs = cfg["webhookURLs"]

    users.append([user,webhookURLs, None, [0.00, 0]]) # earnapp user object, webhook urls, previous info, [average hourly earnings, amount of values in average]
    
info("EarnApp user objects created.")
info("Getting current info...")
for user in users:
    user[2] = retrieveData(user[0])

info("Current info retrieved.")

# start the app
info("Starting earnings watcher...")

# run on the hour
while True:
    # wait until the next hour
    dt = datetime.now() + timedelta(hours=1)
    dt = dt.replace(minute=00, second=00, microsecond=0)
    while datetime.now() < dt:
        time.sleep(1)


    info("It has just become another hour, waiting " + str(cfg["delay"]) + " seconds...")
    time.sleep(cfg["delay"])
    info("It's time to check for new earnings...")

    for user in users:
        oldInfo = user[2]
        info("Getting new info...")
        newInfo = retrieveData(user[0])
        info("New info retrieved.")
    
        if cfg["balanceUpdateSettings"]["enabled"] == True:
            info("Checking balance updates...")
            if oldInfo["money"]["balance"] != newInfo["money"]["balance"]:
                info("Balance has changed!")
                user[3][0] += newInfo["money"]["balance"] - oldInfo["money"]["balance"]
                user[3][1] += 1
                info("Sending balance update...")
                sendBalanceUpdate(cfg, oldInfo, newInfo, user[1], user[3], version, state, True)
                info("Balance update sent.")
            else:
                info("Balance has not changed.")
                user[3][1] += 1
                if cfg["balanceUpdateSettings"]["sendIfNotChanged"] == True:
                    info("Sending balance update...")
                    sendBalanceUpdate(cfg, oldInfo, newInfo, user[1], user[3], version, state, False)
                    info("Balance update sent.")

        user[2] = newInfo