"""
EarnApp-Earnings-Watcher - A program to monitor your EarnApp Earnings and send data to a discord webhook
Copyright (C) 2022  SWM Tech Industries

This file is part of EarnApp-Earnings-Watcher.

EarnApp-Earnings-Watcher is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

EarnApp-Earnings-Watcher is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with EarnApp-Earnings-Watcher. If not, see <https://www.gnu.org/licenses/>.
"""

from placeholders import *
from log import *
import requests
import time

def textToEmbed(text: str, cfg: dict, type: str, version: str, state: str, hasBalanceChanged: bool) -> dict:
    embed = {}

    embedSettings = cfg[type + "Settings"]["embedSettings"] if type != "deviceBalanceUpdate" else cfg["balanceUpdateSettings"]["perDeviceEmbedSettings"]

    if embedSettings["colour"] != "":
        embed["color"] = int(embedSettings["colour"], 16) if hasBalanceChanged else int(embedSettings["colourIfNotChanged"], 16)

    embed["author"], embed["thumbnail"], embed["footer"] = {}, {}, {}


    if embedSettings["authorName"] != "":
        embed["author"]["name"] = basicPlaceholderReplace(embedSettings["authorName"], version, state)

    if embedSettings["authorIcon"] != "":
        embed["author"]["icon_url"] = basicPlaceholderReplace(embedSettings["authorIcon"], version, state)
    
    if embedSettings["authorURL"] != "":
        embed["author"]["url"] = basicPlaceholderReplace(embedSettings["authorURL"], version, state)

    if embedSettings["title"] != "":
        embed["title"] = basicPlaceholderReplace(embedSettings["title"], version, state)
    
    if embedSettings["titleURL"] != "":
        embed["url"] = basicPlaceholderReplace(embedSettings["titleURL"], version, state)
        
    if embedSettings["thumbnail"] != "":
        embed["thumbnail"]["url"] = basicPlaceholderReplace(embedSettings["thumbnail"], version, state)

    if embedSettings["description"] != "":
        embed["description"] = basicPlaceholderReplace(embedSettings["description"], version, state) if hasBalanceChanged else basicPlaceholderReplace(embedSettings["descriptionIfNotChanged"], version, state)
        
    if embedSettings["footer"] != "":
        embed["footer"]["text"] = basicPlaceholderReplace(embedSettings["footer"], version, state)

    if embedSettings["footerIcon"] != "":
        embed["footer"]["icon_url"] = basicPlaceholderReplace(embedSettings["footerIcon"], version, state)

    embed["fields"] = []

    # now, take in a string such as "**Account Email**\nexample@example.com\n\n**Account ID**\n123456789\n\n" and turn it into [{"name": "Account Email", "value": "example@example.com"}, {"name": "Account ID", "value": "123456789"}]
    lines = text.split("\n")
    i = -1
    # loop over stripped lines
    for line in lines:
        i += 1
        if line == "":
            continue
        if line[0:2] == "**":
            name = line[2:-2]
            value = lines[i+1]
            embed["fields"].append({"name": name, "value": value, "inline": embedSettings["inline"]})

    
    return embed

def generateAppUpdateText(cfg: dict, oldAppVersions: dict, newAppVersions: dict, version: str, state: str) -> str:
    text = ""

    if cfg["appUpdateSettings"]["shownInfo"]["windows"]["enabled"]:
        text += "**" + cfg["appUpdateSettings"]["shownInfo"]["windows"]["title"] + "**\n" + cfg["appUpdateSettings"]["shownInfo"]["windows"]["text"] + "\n\n"

    if cfg["appUpdateSettings"]["shownInfo"]["mac"]["enabled"]:
        text += "**" + cfg["appUpdateSettings"]["shownInfo"]["mac"]["title"] + "**\n" + cfg["appUpdateSettings"]["shownInfo"]["mac"]["text"] + "\n\n"

    return basicPlaceholderReplace(appUpdatePlaceholderReplace(text, oldAppVersions, newAppVersions), version, state)

def generateRedeemRequestText(cfg: dict, redeemRequest: dict, version: str, state: str) -> str:
    text = ""

    if cfg["redeemRequestSettings"]["shownInfo"]["amount"]["enabled"]:
        text += "**" + cfg["redeemRequestSettings"]["shownInfo"]["amount"]["title"] + "**\n" + cfg["redeemRequestSettings"]["shownInfo"]["amount"]["text"] + "\n\n"

    if cfg["redeemRequestSettings"]["shownInfo"]["promotionsBonus"]["enabled"]:
        text += "**" + cfg["redeemRequestSettings"]["shownInfo"]["promotionsBonus"]["title"] + "**\n" + cfg["redeemRequestSettings"]["shownInfo"]["promotionsBonus"]["text"] + "\n\n"

    if cfg["redeemRequestSettings"]["shownInfo"]["status"]["enabled"]:
        text += "**" + cfg["redeemRequestSettings"]["shownInfo"]["status"]["title"] + "**\n" + cfg["redeemRequestSettings"]["shownInfo"]["status"]["text"] + "\n\n"

    if cfg["redeemRequestSettings"]["shownInfo"]["id"]["enabled"]:
        text += "**" + cfg["redeemRequestSettings"]["shownInfo"]["id"]["title"] + "**\n" + cfg["redeemRequestSettings"]["shownInfo"]["id"]["text"] + "\n\n"

    if cfg["redeemRequestSettings"]["shownInfo"]["createdAt"]["enabled"]:
        text += "**" + cfg["redeemRequestSettings"]["shownInfo"]["createdAt"]["title"] + "**\n" + cfg["redeemRequestSettings"]["shownInfo"]["createdAt"]["text"] + "\n\n"

    if cfg["redeemRequestSettings"]["shownInfo"]["email"]["enabled"]:
        text += "**" + cfg["redeemRequestSettings"]["shownInfo"]["email"]["title"] + "**\n" + cfg["redeemRequestSettings"]["shownInfo"]["email"]["text"] + "\n\n"

    if cfg["redeemRequestSettings"]["shownInfo"]["paymentMethod"]["enabled"]:
        text += "**" + cfg["redeemRequestSettings"]["shownInfo"]["paymentMethod"]["title"] + "**\n" + cfg["redeemRequestSettings"]["shownInfo"]["paymentMethod"]["text"] + "\n\n"

    return basicPlaceholderReplace(redeemRequestPlaceholderReplace(text, redeemRequest), version, state)

def generateNewDeviceText(cfg: dict, newDevice: dict, version: str, state: str) -> str:
    text = ""

    if cfg["newDeviceSettings"]["shownInfo"]["id"]["enabled"]:
        text += "**" + cfg["newDeviceSettings"]["shownInfo"]["id"]["title"] + "**\n" + cfg["newDeviceSettings"]["shownInfo"]["id"]["text"] + "\n\n"

    if cfg["newDeviceSettings"]["shownInfo"]["name"]["enabled"]:
        text += "**" + cfg["newDeviceSettings"]["shownInfo"]["name"]["title"] + "**\n" + cfg["newDeviceSettings"]["shownInfo"]["name"]["text"] + "\n\n"

    if cfg["newDeviceSettings"]["shownInfo"]["bw"]["enabled"]:
        text += "**" + cfg["newDeviceSettings"]["shownInfo"]["bw"]["title"] + "**\n" + cfg["newDeviceSettings"]["shownInfo"]["bw"]["text"] + "\n\n"

    if cfg["newDeviceSettings"]["shownInfo"]["country"]["enabled"]:
        text += "**" + cfg["newDeviceSettings"]["shownInfo"]["country"]["title"] + "**\n" + cfg["newDeviceSettings"]["shownInfo"]["country"]["text"] + "\n\n"

    if cfg["newDeviceSettings"]["shownInfo"]["earned"]["enabled"]:
        text += "**" + cfg["newDeviceSettings"]["shownInfo"]["earned"]["title"] + "**\n" + cfg["newDeviceSettings"]["shownInfo"]["earned"]["text"] + "\n\n"

    if cfg["newDeviceSettings"]["shownInfo"]["totalEarned"]["enabled"]:
        text += "**" + cfg["newDeviceSettings"]["shownInfo"]["totalEarned"]["title"] + "**\n" + cfg["newDeviceSettings"]["shownInfo"]["totalEarned"]["text"] + "\n\n"

    if cfg["newDeviceSettings"]["shownInfo"]["ips"]["enabled"]:
        text += "**" + cfg["newDeviceSettings"]["shownInfo"]["ips"]["title"] + "**\n" + cfg["newDeviceSettings"]["shownInfo"]["ips"]["text"] + "\n\n"

    if cfg["newDeviceSettings"]["shownInfo"]["rate"]["enabled"]:
        text += "**" + cfg["newDeviceSettings"]["shownInfo"]["rate"]["title"] + "**\n" + cfg["newDeviceSettings"]["shownInfo"]["rate"]["text"] + "\n\n"

    if cfg["newDeviceSettings"]["shownInfo"]["totalBw"]["enabled"]:
        text += "**" + cfg["newDeviceSettings"]["shownInfo"]["totalBw"]["title"] + "**\n" + cfg["newDeviceSettings"]["shownInfo"]["totalBw"]["text"] + "\n\n"

    return basicPlaceholderReplace(newDevicePlaceholderReplace(text, newDevice, cfg["newDeviceSettings"]["shownInfo"]["ips"]["separator"]), version, state)

def generateDeviceBalanceUpdateText(cfg: dict, oldDevice: dict, newDevice: dict, version: str, state: str) -> str:
    text = ""

    if cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["deviceID"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["deviceID"]["title"] + "**\n" + cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["deviceID"]["text"] + "\n\n"

    if cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["name"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["name"]["title"] + "**\n" + cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["name"]["text"] + "\n\n"

    if cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["deviceType"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["deviceType"]["title"] + "**\n" + cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["deviceType"]["text"] + "\n\n"

    if cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["bandwidth"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["bandwidth"]["title"] + "**\n" + cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["bandwidth"]["text"] + "\n\n"

    if cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["country"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["country"]["title"] + "**\n" + cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["country"]["text"] + "\n\n"

    if cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["earned"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["earned"]["title"] + "**\n" + cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["earned"]["text"] + "\n\n"

    if cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["totalEarned"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["totalEarned"]["title"] + "**\n" + cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["totalEarned"]["text"] + "\n\n"

    if cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["ips"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["ips"]["title"] + "**\n" + cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["ips"]["text"] + "\n\n"

    if cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["rate"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["rate"]["title"] + "**\n" + cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["rate"]["text"] + "\n\n"

    if cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["totalBw"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["totalBw"]["title"] + "**\n" + cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["totalBw"]["text"] + "\n\n"

    return basicPlaceholderReplace(newDevicePlaceholderReplace(text, newDevice, cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["ips"]["separator"], oldDevice), version, state)

def generateBalanceUpdateText(cfg: dict, oldInfo: dict, newInfo: dict, averageList: list, version: str, state: str) -> str:
    text = ""
    activeDevices = []
    for device in newInfo["devices"]:
        if device["bw"] != 0:
            activeDevices.append(device["uuid"])
        
    linuxDevices = 0
    windowsDevices = 0
    linuxDevicesActive = 0
    windowsDevicesActive = 0
    for device in newInfo["devices"]:
        if device["uuid"].startswith("sdk-win-"):
            windowsDevices += 1
            if device["uuid"] in activeDevices:
                windowsDevicesActive += 1
        elif device["uuid"].startswith("sdk-node-"):
            linuxDevices += 1
            if device["uuid"] in activeDevices:
                linuxDevicesActive += 1

    if cfg["balanceUpdateSettings"]["shownInfo"]["accountEmail"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["shownInfo"]["accountEmail"]["title"] + "**\n" + cfg["balanceUpdateSettings"]["shownInfo"]["accountEmail"]["text"] + "\n\n"

    if cfg["balanceUpdateSettings"]["shownInfo"]["accountName"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["shownInfo"]["accountName"]["title"] + "**\n" + cfg["balanceUpdateSettings"]["shownInfo"]["accountName"]["text"] + "\n\n"

    if cfg["balanceUpdateSettings"]["shownInfo"]["hourEarned"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["shownInfo"]["hourEarned"]["title"] + "**\n" + cfg["balanceUpdateSettings"]["shownInfo"]["hourEarned"]["text"] + "\n\n"

    if cfg["balanceUpdateSettings"]["shownInfo"]["hourEarnedAverage"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["shownInfo"]["hourEarnedAverage"]["title"] + "**\n" + cfg["balanceUpdateSettings"]["shownInfo"]["hourEarnedAverage"]["text"] + "\n\n"

    if cfg["balanceUpdateSettings"]["shownInfo"]["refEarnings"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["shownInfo"]["refEarnings"]["title"] + "**\n" + cfg["balanceUpdateSettings"]["shownInfo"]["refEarnings"]["text"] + "\n\n"

    if cfg["balanceUpdateSettings"]["shownInfo"]["promotionsEarnings"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["shownInfo"]["promotionsEarnings"]["title"] + "**\n" + cfg["balanceUpdateSettings"]["shownInfo"]["promotionsEarnings"]["text"] + "\n\n"

    if cfg["balanceUpdateSettings"]["shownInfo"]["hourTraffic"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["shownInfo"]["hourTraffic"]["title"] + "**\n" + cfg["balanceUpdateSettings"]["shownInfo"]["hourTraffic"]["text"] + "\n\n"

    if cfg["balanceUpdateSettings"]["shownInfo"]["balance"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["shownInfo"]["balance"]["title"] + "**\n" + cfg["balanceUpdateSettings"]["shownInfo"]["balance"]["text"] + "\n\n"

    if cfg["balanceUpdateSettings"]["shownInfo"]["lifetimeBalance"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["shownInfo"]["lifetimeBalance"]["title"] + "**\n" + cfg["balanceUpdateSettings"]["shownInfo"]["lifetimeBalance"]["text"] + "\n\n"

    if cfg["balanceUpdateSettings"]["shownInfo"]["deviceTypeActive"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["shownInfo"]["activeDevices"]["title"] + "**\n" + str(windowsDevicesActive) + " Windows" + cfg["balanceUpdateSettings"]["shownInfo"]["activeDevices"]["separator"] + str(linuxDevicesActive) + " Linux" + "\n\n"
    elif cfg["balanceUpdateSettings"]["shownInfo"]["activeDevices"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["shownInfo"]["activeDevices"]["title"] + "**\n" + str(windowsDevices + linuxDevices) + "\n\n"

    if cfg["balanceUpdateSettings"]["shownInfo"]["deviceTypeInactive"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["shownInfo"]["inactiveDevices"]["title"] + "**\n" + str(windowsDevices - windowsDevicesActive) + " Windows" + cfg["balanceUpdateSettings"]["shownInfo"]["inactiveDevices"]["separator"] + str(linuxDevices - linuxDevicesActive) + " Linux" + "\n\n"
    elif cfg["balanceUpdateSettings"]["shownInfo"]["inactiveDevices"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["shownInfo"]["inactiveDevices"]["title"] + "**\n" + str(windowsDevices - windowsDevicesActive + linuxDevices - linuxDevicesActive) + "\n\n"

    if cfg["balanceUpdateSettings"]["shownInfo"]["deviceTypeTotal"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["shownInfo"]["totalDevices"]["title"] + "**\n" + str(windowsDevices) + " Windows" + cfg["balanceUpdateSettings"]["shownInfo"]["totalDevices"]["separator"] + str(linuxDevices) + " Linux" + "\n\n"
    elif cfg["balanceUpdateSettings"]["shownInfo"]["totalDevices"]["enabled"]:
        text += "**" + cfg["balanceUpdateSettings"]["shownInfo"]["totalDevices"]["title"] + "**\n" + str(windowsDevices + linuxDevices) + "\n\n"
        
    return basicPlaceholderReplace(balanceUpdatePlaceholderReplace(text, oldInfo, newInfo, averageList), version, state)

def sendDeviceBalanceUpdate(cfg: dict, oldDevice: dict, newDevice: dict, webhookURLs: list, version: str, state: str, hasEarningsChanged: bool):
    data = {
        "content": "",
    }

    if cfg["webhookName"] != "":
        data["username"] = cfg["webhookName"]
    if cfg["webhookImage"] != "":
        data["avatar_url"] = cfg["webhookImage"]

    text = generateDeviceBalanceUpdateText(cfg, oldDevice, newDevice, version, state)

    if cfg["balanceUpdateSettings"]["perDeviceEmbedSettings"]["embed"]:
        data["embeds"] = [textToEmbed(text, cfg, "deviceBalanceUpdate", version, state, hasEarningsChanged)]
    else:
        data["content"] = text

    for webhookURL in webhookURLs:
        while True:
            try:
                r = requests.post(webhookURL, json=data)
                if r.status_code == 429:
                    warning("Discord rate limit reached, waiting 5 seconds...")
                    time.sleep(5)
                    continue
                info("Sent balance update message with response code " + str(r.status_code))
                break
            except:
                warning("Something happened, retrying...")


def sendBalanceUpdate(cfg: dict, oldInfo: dict, newInfo: dict, webhookURLs: list, averageList: list, version: str, state: str, hasBalanceChanged: bool):
    data = {
        "content": "",
    }

    if cfg["webhookName"] != "":
        data["username"] = cfg["webhookName"]
    if cfg["webhookImage"] != "":
        data["avatar_url"] = cfg["webhookImage"]

    text = generateBalanceUpdateText(cfg, oldInfo, newInfo, averageList, version, state)

    if cfg["balanceUpdateSettings"]["embedSettings"]["embed"]:
        data["embeds"] = [textToEmbed(text, cfg, "balanceUpdate", version, state, hasBalanceChanged)]
    else:
        data["content"] = text

    for webhookURL in webhookURLs:
        while True:
            try:
                r = requests.post(webhookURL, json=data)
                if r.status_code == 429:
                    warning("Discord rate limit reached, waiting 5 seconds...")
                    time.sleep(5)
                    continue
                info("Sent balance update message with response code " + str(r.status_code))
                break
            except:
                warning("Something happened, retrying...")

def sendAppUpdate(cfg: dict, oldAppVersions: dict, newAppVersions: dict, webhookURLs: list, version: str, state: str) -> None:
    data = {
        "content": "",
    }

    if cfg["webhookName"] != "":
        data["username"] = cfg["webhookName"]
    if cfg["webhookImage"] != "":
        data["avatar_url"] = cfg["webhookImage"]

    text = generateAppUpdateText(cfg, oldAppVersions, newAppVersions, version, state)

    if cfg["appUpdateSettings"]["embedSettings"]["embed"]:
        data["embeds"] = [textToEmbed(text, cfg, "appUpdate", version, state, True)]
    else:
        data["content"] = text

    for webhookURL in webhookURLs:
        while True:
            try:
                r = requests.post(webhookURL, json=data)
                if r.status_code == 429:
                    warning("Discord rate limit reached, waiting 5 seconds...")
                    time.sleep(5)
                    continue
                info("Sent app update message with response code " + str(r.status_code))
                break
            except:
                warning("Something happened, retrying...")

def sendRedeemRequest(cfg: dict, redeemRequest: dict, webhookURLs: list, version: str, state: str) -> None:
    data = {
        "content": "",
    }

    if cfg["webhookName"] != "":
        data["username"] = cfg["webhookName"]
    if cfg["webhookImage"] != "":
        data["avatar_url"] = cfg["webhookImage"]

    text = generateRedeemRequestText(cfg, redeemRequest, version, state)

    if cfg["redeemRequestSettings"]["embedSettings"]["embed"]:
        data["embeds"] = [textToEmbed(text, cfg, "redeemRequest", version, state, True)]
    else:
        data["content"] = text

    for webhookURL in webhookURLs:
        while True:
            try:
                r = requests.post(webhookURL, json=data)
                if r.status_code == 429:
                    warning("Discord rate limit reached, waiting 5 seconds...")
                    time.sleep(5)
                    continue
                info("Sent redeem request message with response code " + str(r.status_code))
                break
            except:
                warning("Something happened, retrying...")

def sendNewDevice(cfg: dict, device: dict, webhookURLs: list, version: str, state: str) -> None:
    data = {
        "content": "",
    }

    if cfg["webhookName"] != "":
        data["username"] = cfg["webhookName"]
    if cfg["webhookImage"] != "":
        data["avatar_url"] = cfg["webhookImage"]

    text = generateNewDeviceText(cfg, device, version, state)

    if cfg["newDeviceSettings"]["embedSettings"]["embed"]:
        data["embeds"] = [textToEmbed(text, cfg, "newDevice", version, state, True)]
    else:
        data["content"] = text

    for webhookURL in webhookURLs:
        while True:
            try:
                r = requests.post(webhookURL, json=data)
                if r.status_code == 429:
                    warning("Discord rate limit reached, waiting 5 seconds...")
                    time.sleep(5)
                    continue
                info("Sent new device message with response code " + str(r.status_code))
                break
            except:
                warning("Something happened, retrying...")
