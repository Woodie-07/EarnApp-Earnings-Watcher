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
from random import choice

from log import *
from mysqlUtils import addUserData
from sendUpdate import *
from config import *

version = "v0.0.4"
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
            if len(cfg["proxies"]) > 0:  # if proxies are configured, use them
                warning("Ratelimited, switching proxy...")
                user.proxy = {"https": choice(cfg["proxies"])}
            else:
                warning("Ratelimited, waiting " + str(cfg["ratelimitWait"]) + " seconds...")
                time.sleep(cfg["ratelimitWait"])
        except Exception as e:
            warning("Something happened, retrying...")
            #print(e)

def retrieveUserData(user: earnapp.User, oldData: dict = None) -> dict:
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
            if not oldData:
                error("Incorrect token: " + token)
            else:
                warning("Incorrect token, resorting to magic. Data may not be as accurate.")

                # magic
                retrievedInfo["userData"] = oldData["userData"]
                retrievedInfo["money"] = oldData["money"]
                retrievedInfo["devices"] = oldData["devices"]
                retrievedInfo["transactions"] = oldData["transactions"]

                hasRedeemed = False
                redeemTotal = 0.00

                balance = 0.00

                i = 0
                for device in retrievedInfo["devices"]:
                    deviceID = device["uuid"]
                    try:
                        version = device["version"]
                    except KeyError:
                        version = "1.317.779"
                    client = earnapp.Client(deviceID, version, "x64", device["appid"], user.proxy)
                    
                    while True:
                        try:
                            appConfigWin = client.appConfigWin()
                            break
                        except earnapp.RatelimitedException:
                            if len(cfg["proxies"]) > 0:  # if proxies are configured, use them
                                warning("Ratelimited, switching proxy...")
                                user.proxy = {"https": choice(cfg["proxies"])}
                            else:
                                warning("Ratelimited, waiting " + str(cfg["ratelimitWait"]) + " seconds...")
                                time.sleep(cfg["ratelimitWait"])
                        except requests.ConnectTimeout:
                            warning("Connection timeout, likely ratelimited. Waiting " + str(cfg["ratelimitWait"]) + " seconds...")
                            time.sleep(cfg["ratelimitWait"])
                    
                    totalBW = appConfigWin["server_bw_total"]
                    redeemBW = appConfigWin["redeem_bw_total"]
                    bw = totalBW - redeemBW

                    if not hasRedeemed:
                        if redeemBW > retrievedInfo["devices"][i]["redeem_bw"]:
                            hasRedeemed = True
                            redeemTotal += retrievedInfo["devices"][i]["earned"]

                    earnedTotal = appConfigWin["earnings_total"]
                    earnedSinceRefresh = earnedTotal - retrievedInfo["devices"][i]["earned_total"]
                    earned = retrievedInfo["devices"][i]["earned"] + earnedSinceRefresh if not hasRedeemed else 0.00

                    balance += earned

                    retrievedInfo["devices"][i]["total_bw"] = totalBW
                    retrievedInfo["devices"][i]["redeem_bw"] = redeemBW
                    retrievedInfo["devices"][i]["bw"] = bw
                    
                    retrievedInfo["devices"][i]["version"] = appConfigWin["version"]

                    i += 1

                if not hasRedeemed:
                    balance += retrievedInfo["money"]["ref_bonuses"]

                if hasRedeemed:
                    retrievedInfo["transactions"].insert(0,
                        {
                            "date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                            "email": "Unknown, in magic mode",
                            "money_amount": redeemTotal,
                            "payment_date": None,
                            "payment_method": "Unknown, in magic mode",
                            "promo_bonuses_amount": 0.00,
                            "ref_bonuses_amount": 0.00,
                            "ref_bvpn_amount": 0.00,
                            "status": "pending",
                            "uuid": "Unknown, in magic mode",
                        }
                    )

                retrievedInfo["money"]["balance"] = balance
                if hasRedeemed:
                    retrievedInfo["money"]["ref_bonuses"] = 0

                transactionsTotal = 0.00
                for transaction in retrievedInfo["transactions"]:
                    transactionsTotal += transaction["money_amount"]

                retrievedInfo["money"]["earnings_total"] = transactionsTotal + balance

        except earnapp.RatelimitedException:
            if len(cfg["proxies"]) > 0:  # if proxies are configured, use them
                warning("Ratelimited, switching proxy...")
                user.proxy = {"https": choice(cfg["proxies"])}
            else:
                warning("Ratelimited, waiting " + str(cfg["ratelimitWait"]) + " seconds...")
                time.sleep(cfg["ratelimitWait"])
        except Exception as e:
            warning("Something happened, retrying...")
            #print(e)

    return retrievedInfo

cfg = loadConfig()  # read config file
validation = validateConfig(cfg)  # check if all options are present and of correct type
if validation != "Config file is correct.":
    error(validation)  # if not, print error and exit

info("Config loaded.")

# check for updates
info("Checking for updates...")
try:
    latestVersion = getLatestVersion()  # get latest release version from GitHub
    if version != latestVersion:  # if current version differs to latest, warn user
        warning("An update is available, you have " + version + " and the latest is " + latestVersion)
    else:
        info("You have the latest version.")
except:
    warning("Failed to get latest version.")


# create an EarnApp user object for every token
info("Creating EarnApp user objects...")
users = []  # array will store all EarnApp user objects
for token in cfg["tokens"]:  # loop over all tokens in config
    user = earnapp.User()  # initialize user object
    if len(cfg["proxies"]) > 0:  # if proxies are configured, use them
        user.proxy = {"https": choice(cfg["proxies"])}
    try:
        user.login(token)  # attempt to log in with token
    except earnapp.IncorrectTokenException:  # if token is incorrect, print error and exit
        error("Incorrect token: " + token)

    # figure out how data should be sent to webhook(s)
    if len(cfg["webhookURLs"]) == len(cfg["tokens"]):  # if there is one webhook per token, send token data to it
        webhookURLs = [cfg["webhookURLs"][len(users)]]
    else:  # if there is a different amount of tokens than webhooks, send all data to all webhooks
        webhookURLs = [cfg["webhookURLs"][0]]

    users.append({
        "user_object": user,  # earnapp.py user object
        "webhook_urls": webhookURLs,  # webhook urls to send that token's data to
        "previous_info": None,  # previous check's data, will be used to compare with current data
        "average": {
            "total": 0.00,  # total money earnt in each check
            "count": 0  # amount of checks
        }  # this data can be used to calculate an average.
    })
    
info("EarnApp user objects created.")

sql = cfg["mysql"]["enabled"]

if sql:  # set up MySQL if enabled
    info("Setting up MySQL connection...")
    import mysqlUtils
    mysqlUtils.init(cfg)
    info("MySQL connection set up.")


info("Getting current info...")
for user in users:  # loop over each user in users array
    user["previous_info"] = retrieveUserData(user["user_object"])  # set the previous_info so we can compare after next update

oldAppVersions = retrieveAppVersions(users[0]["user_object"])  # use the first user to retrieve app versions

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

    delay = cfg["delay"]  # fetch delay from config

    info("It has just become another hour, waiting " + str(delay) + " seconds...")

    time.sleep(delay)  # wait for delay seconds - needed because EarnApp doesn't update data instantly
    info("It's time to check for new earnings...")

    newAppVersions = retrieveAppVersions(users[0]["user_object"])  # use the first user to retrieve new app versions
    if newAppVersions["win"] != oldAppVersions["win"] or newAppVersions["mac"] != oldAppVersions["mac"]:  # check if app version has changed
        if sql and cfg["appUpdateSettings"]["sqlEnabled"]:  # if SQL is enabled, add to database
            mysqlUtils.addAppUpdate(newAppVersions, cfg)
        if cfg["appUpdateSettings"]["enabled"]:  # if webhook message is enabled, send message
            sendAppUpdate(cfg, oldAppVersions, newAppVersions, cfg["webhookURLs"], version, state)

    oldAppVersions = newAppVersions  # set oldAppVersions to newAppVersions so we can compare next time

    for user in users:  # loop over all users
        oldInfo = user["previous_info"]  # get the previous info
        info("Getting new info...")
        newInfo = retrieveUserData(user["user_object"], oldInfo)  # get the current info
        info("New info retrieved.")
    
        if sql:
            if cfg["userDataSettings"]["sqlEnabled"]:  # if sql enabled and user data sql enabled, add to database
                addUserData(newInfo["userData"], cfg)

            if cfg["balanceUpdateSettings"]["sqlEnabled"]:  # if sql enabled and balance update sql enabled, add to database
                moneyRow = mysqlUtils.addMoneyUpdate(newInfo["money"], cfg)
                if cfg["balanceUpdateSettings"]["sqlPerDevice"]:  # if sql per device also enabled, add devices to database
                    mysqlUtils.addDevices(newInfo["devices"], cfg, moneyRow)

        if cfg["balanceUpdateSettings"]["enabled"] and cfg["balanceUpdateSettings"]["perDevice"]:
            for device in newInfo["devices"]:
                for oldDevice in oldInfo["devices"]:
                    if oldDevice["uuid"] == device["uuid"]:
                        if device["bw"] != oldDevice["bw"]:
                            sendDeviceBalanceUpdate(cfg, oldDevice, device, webhookURLs, version, state, True)
                        elif cfg["balanceUpdateSettings"]["sendIfNotChanged"]:
                            sendDeviceBalanceUpdate(cfg, oldDevice, device, webhookURLs, version, state, False)
                        break

        if oldInfo["money"]["balance"] != newInfo["money"]["balance"]:  # if balance changed
            if cfg["balanceUpdateSettings"]["enabled"]:  # if balance message enabled
                info("Balance has changed!")
                user["average"]["total"] += newInfo["money"]["earnings_total"] - oldInfo["money"]["earnings_total"]  # add to average
                user["average"]["count"] += 1  # increase average count
                info("Sending balance update...")
                sendBalanceUpdate(cfg, oldInfo, newInfo, user["webhook_urls"], [user["average"]["total"], user["average"]["count"]], version, state, True)  # send balance update message
                info("Balance update sent.")
        else:  # if balance not changed
            info("Balance has not changed.")
            user["average"]["count"] += 1  # increase average count
            if cfg["balanceUpdateSettings"]["sendIfNotChanged"]:  # if send if not changed enabled
                info("Sending balance update...")
                sendBalanceUpdate(cfg, oldInfo, newInfo, user["webhook_urls"], [user["average"]["total"], user["average"]["count"]], version, state, False)  # send balance update message
                info("Balance update sent.")


        if len(oldInfo["transactions"]) < len(newInfo["transactions"]):  # if there are new transactions
            # find the new transactions
            oldTransactionIDs = []
            newTransactions = []
            for transaction in oldInfo["transactions"]:
                oldTransactionIDs.append(transaction["uuid"])

            for transaction in newInfo["transactions"]:
                if transaction["uuid"] not in oldTransactionIDs:
                    newTransactions.append(transaction)


            if sql and cfg["redeemRequestSettings"]["sqlEnabled"]:  # if sql enabled and redeem request sql enabled, add to database
                for transaction in newTransactions:
                    mysqlUtils.addTransaction(transaction, cfg)
            if cfg["redeemRequestSettings"]["enabled"] == True:  # if redeem request message enabled
                info("Redeem requests have changed!")
                for transaction in newTransactions:  # loop over all new transactions and send message
                    info("Sending redeem request update...")
                    sendRedeemRequest(cfg, transaction, user["webhook_urls"], version, state)
                    info("Redeem request update sent.")
            else:
                info("Redeem requests have not changed.")

        if len(oldInfo["devices"]) < len(newInfo["devices"]):  # if new devices added
            # find the new devices
            oldDeviceIDs = []
            newDevices = []
            for device in oldInfo["devices"]:
                oldDeviceIDs.append(device["uuid"])

            for device in newInfo["devices"]:
                if device["uuid"] not in oldDeviceIDs:
                    newDevices.append(device)
                    
            if cfg["newDeviceSettings"]["enabled"]:  # if new device message enabled
                info("New devices have changed!")
                for device in newDevices:  # send a message for each device
                    info("Sending new device update...")
                    sendNewDevice(cfg, device, user["webhook_urls"], version, state)
                    info("New device update sent.")
            else:
                info("New devices have not changed.")

        user["previous_info"] = newInfo  # set previous_info to newInfo so we can compare next time