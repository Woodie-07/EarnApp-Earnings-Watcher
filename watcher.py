"""
EarnApp-Earnings-Watcher - A program to monitor your EarnApp Earnings and send data to a discord webhook
Copyright (C) 2022  SWM Tech Industries

This file is part of EarnApp-Earnings-Watcher.

EarnApp-Earnings-Watcher is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

EarnApp-Earnings-Watcher is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with EarnApp-Earnings-Watcher. If not, see <https://www.gnu.org/licenses/>.
"""

from earnapp import earnapp
import requests, time
from datetime import datetime, timedelta

from log import *
from sendUpdate import *
from config import *

version = "v0.0.3"
state = "ALPHA"


# use GitHub API to get latest version
def getLatestVersion() -> str:
    url = "https://api.github.com/repos/Woodie-07/EarnApp-Earnings-Watcher/releases"
    response = requests.get(url)
    data = response.json()
    return data[0]["tag_name"]

def retrieveAppVersions(user: earnapp.User) -> dict:
    while True:
        try:
            return user.appVersions()
        except earnapp.IncorrectTokenException:
            error("Incorrect token: " + token)
        except earnapp.RatelimitedException:
            warning("Ratelimited, waiting " + str(cfg["ratelimitWait"]) + " seconds...")
            time.sleep(cfg["ratelimitWait"])
        except:
            warning("Something happened, retrying...")

def retrieveUserData(user: earnapp.User) -> dict:
    retrievedInfo = {}

    doneUserData = False
    doneMoney = False
    doneDevices = False
    doneTransactions = False
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
            break
        except earnapp.IncorrectTokenException:
            error("Incorrect token: " + token)
        except earnapp.RatelimitedException:
            warning("Ratelimited, waiting " + str(cfg["ratelimitWait"]) + " seconds...")
            time.sleep(cfg["ratelimitWait"])
        except:
            warning("Something happened, retrying...")

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
    user[2] = retrieveUserData(user[0])

oldAppVersions = retrieveAppVersions(users[0][0])

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

    newAppVersions = retrieveAppVersions(users[0][0])
    if newAppVersions["win"] != oldAppVersions["win"] or newAppVersions["mac"] != oldAppVersions["mac"]:
        sendAppUpdate(cfg, oldAppVersions, newAppVersions, cfg["webhookURLs"], version, state)

    oldAppVersions = newAppVersions

    for user in users:
        oldInfo = user[2]
        info("Getting new info...")
        newInfo = retrieveUserData(user[0])
        info("New info retrieved.")
    
        if cfg["balanceUpdateSettings"]["enabled"] == True:
            info("Checking balance updates...")
            if oldInfo["money"]["balance"] != newInfo["money"]["balance"]:
                info("Balance has changed!")
                user[3][0] += newInfo["money"]["earnings_total"] - oldInfo["money"]["earnings_total"]
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

        if cfg["redeemRequestSettings"]["enabled"] == True:
            info("Checking redeem requests...")
            if len(oldInfo["transactions"]) < len(newInfo["transactions"]):
                oldTransactionIDs = []
                newTransactions = []
                for transaction in oldInfo["transactions"]:
                    oldTransactionIDs.append(transaction["uuid"])

                for transaction in newInfo["transactions"]:
                    if transaction["uuid"] not in oldTransactionIDs:
                        newTransactions.append(transaction)

                info("Redeem requests have changed!")
                for transaction in newTransactions:
                    info("Sending redeem request update...")
                    sendRedeemRequest(cfg, transaction, user[1], version, state)
                    info("Redeem request update sent.")
            else:
                info("Redeem requests have not changed.")

        if cfg["newDeviceSettings"]["enabled"]:
            info("Checking new devices...")
            if len(oldInfo["devices"]) < len(newInfo["devices"]):
                oldDeviceIDs = []
                newDevices = []
                for device in oldInfo["devices"]:
                    oldDeviceIDs.append(device["uuid"])

                for device in newInfo["devices"]:
                    if device["uuid"] not in oldDeviceIDs:
                        newDevices.append(device)

                info("New devices have changed!")
                for device in newDevices:
                    info("Sending new device update...")
                    sendNewDevice(cfg, device, user[1], version, state)
                    info("New device update sent.")
            else:
                info("New devices have not changed.")

        user[2] = newInfo
