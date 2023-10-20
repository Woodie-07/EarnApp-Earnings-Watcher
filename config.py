"""
EarnApp-Earnings-Watcher - A program to monitor your EarnApp Earnings and send data to a discord webhook
Copyright (C) 2023  Woodie

This file is part of EarnApp-Earnings-Watcher.

EarnApp-Earnings-Watcher is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

EarnApp-Earnings-Watcher is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with EarnApp-Earnings-Watcher. If not, see <https://www.gnu.org/licenses/>.
"""

import yaml

def loadConfig() -> dict:
    with open('config.yml', 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    return cfg

def validateConfig(cfg: dict) -> str:
    try:
        # check that all config variables are of the correct type
        if isinstance(cfg["webhookURLs"], list):
            for item in cfg["webhookURLs"] :
                if not isinstance(item, str):
                    return("webhookURLs must be a list of strings")
        else:
            return("webhookURLs must be a list of strings")

        if isinstance(cfg["tokens"], list):
            for item in cfg["tokens"] :
                if not isinstance(item, str):
                    return("tokens must be a list of strings")
        else:
            return("tokens must be a list of strings")

        if isinstance(cfg["proxies"], list):
            for item in cfg["proxies"] :
                if not isinstance(item, str):
                    return("proxies must be a list of strings")
        else:
            return("proxies must be a list of strings")

        if not all(isinstance(i, str) for i in [
            cfg["webhookName"],
            cfg["webhookImage"],
            cfg["mysql"]["host"],
            cfg["mysql"]["user"],
            cfg["mysql"]["password"],
            cfg["mysql"]["database"],
            cfg["balanceUpdateSettings"]["perDeviceEmbedSettings"]["colour"], 
            cfg["balanceUpdateSettings"]["perDeviceEmbedSettings"]["title"], 
            cfg["balanceUpdateSettings"]["perDeviceEmbedSettings"]["titleURL"], 
            cfg["balanceUpdateSettings"]["perDeviceEmbedSettings"]["description"], 
            cfg["balanceUpdateSettings"]["perDeviceEmbedSettings"]["authorName"], 
            cfg["balanceUpdateSettings"]["perDeviceEmbedSettings"]["authorURL"], 
            cfg["balanceUpdateSettings"]["perDeviceEmbedSettings"]["authorIcon"], 
            cfg["balanceUpdateSettings"]["perDeviceEmbedSettings"]["image"], 
            cfg["balanceUpdateSettings"]["perDeviceEmbedSettings"]["thumbnail"], 
            cfg["balanceUpdateSettings"]["perDeviceEmbedSettings"]["footer"], 
            cfg["balanceUpdateSettings"]["perDeviceEmbedSettings"]["footerIcon"],
            cfg["balanceUpdateSettings"]["embedSettings"]["colour"], 
            cfg["balanceUpdateSettings"]["embedSettings"]["title"], 
            cfg["balanceUpdateSettings"]["embedSettings"]["titleURL"], 
            cfg["balanceUpdateSettings"]["embedSettings"]["description"], 
            cfg["balanceUpdateSettings"]["embedSettings"]["authorName"], 
            cfg["balanceUpdateSettings"]["embedSettings"]["authorURL"], 
            cfg["balanceUpdateSettings"]["embedSettings"]["authorIcon"], 
            cfg["balanceUpdateSettings"]["embedSettings"]["image"], 
            cfg["balanceUpdateSettings"]["embedSettings"]["thumbnail"], 
            cfg["balanceUpdateSettings"]["embedSettings"]["footer"], 
            cfg["balanceUpdateSettings"]["embedSettings"]["footerIcon"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["deviceID"]["title"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["deviceID"]["text"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["deviceType"]["title"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["deviceType"]["text"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["bandwidth"]["title"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["bandwidth"]["text"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["country"]["title"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["country"]["text"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["earned"]["title"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["earned"]["text"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["totalEarned"]["title"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["totalEarned"]["text"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["ips"]["title"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["ips"]["text"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["ips"]["separator"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["rate"]["title"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["rate"]["text"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["name"]["title"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["name"]["text"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["totalBw"]["title"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["totalBw"]["text"],
            cfg["balanceUpdateSettings"]["shownInfo"]["accountEmail"]["title"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["accountEmail"]["text"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["accountName"]["title"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["accountName"]["text"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["hourEarned"]["title"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["hourEarned"]["text"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["hourEarnedAverage"]["title"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["hourEarnedAverage"]["text"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["refEarnings"]["title"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["refEarnings"]["text"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["promotionsEarnings"]["title"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["promotionsEarnings"]["text"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["hourTraffic"]["title"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["hourTraffic"]["text"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["balance"]["title"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["balance"]["text"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["lifetimeBalance"]["title"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["lifetimeBalance"]["text"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["activeDevices"]["title"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["activeDevices"]["separator"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["inactiveDevices"]["title"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["inactiveDevices"]["separator"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["totalDevices"]["title"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["totalDevices"]["separator"], 
            cfg["balanceUpdateSettings"]["embedSettings"]["colourIfNotChanged"],
            cfg["balanceUpdateSettings"]["embedSettings"]["descriptionIfNotChanged"],
            cfg["appUpdateSettings"]["embedSettings"]["colour"], 
            cfg["appUpdateSettings"]["embedSettings"]["title"], 
            cfg["appUpdateSettings"]["embedSettings"]["titleURL"], 
            cfg["appUpdateSettings"]["embedSettings"]["description"],
            cfg["appUpdateSettings"]["embedSettings"]["authorName"],
            cfg["appUpdateSettings"]["embedSettings"]["authorURL"],
            cfg["appUpdateSettings"]["embedSettings"]["authorIcon"],
            cfg["appUpdateSettings"]["embedSettings"]["image"],
            cfg["appUpdateSettings"]["embedSettings"]["thumbnail"],
            cfg["appUpdateSettings"]["embedSettings"]["footer"],
            cfg["appUpdateSettings"]["embedSettings"]["footerIcon"],
            cfg["appUpdateSettings"]["shownInfo"]["windows"]["title"],
            cfg["appUpdateSettings"]["shownInfo"]["windows"]["text"],
            cfg["appUpdateSettings"]["shownInfo"]["mac"]["title"],
            cfg["appUpdateSettings"]["shownInfo"]["mac"]["text"],
            cfg["redeemRequestSettings"]["embedSettings"]["colour"],
            cfg["redeemRequestSettings"]["embedSettings"]["title"],
            cfg["redeemRequestSettings"]["embedSettings"]["titleURL"], 
            cfg["redeemRequestSettings"]["embedSettings"]["description"],
            cfg["redeemRequestSettings"]["embedSettings"]["authorName"],
            cfg["redeemRequestSettings"]["embedSettings"]["authorURL"],
            cfg["redeemRequestSettings"]["embedSettings"]["authorIcon"],
            cfg["redeemRequestSettings"]["embedSettings"]["image"],
            cfg["redeemRequestSettings"]["embedSettings"]["thumbnail"],
            cfg["redeemRequestSettings"]["embedSettings"]["footer"],
            cfg["redeemRequestSettings"]["embedSettings"]["footerIcon"],
            cfg["redeemRequestSettings"]["shownInfo"]["amount"]["title"],
            cfg["redeemRequestSettings"]["shownInfo"]["amount"]["text"],
            cfg["redeemRequestSettings"]["shownInfo"]["referralsBonus"]["title"],
            cfg["redeemRequestSettings"]["shownInfo"]["referralsBonus"]["text"],
            cfg["redeemRequestSettings"]["shownInfo"]["promotionsBonus"]["title"],
            cfg["redeemRequestSettings"]["shownInfo"]["promotionsBonus"]["text"],
            cfg["redeemRequestSettings"]["shownInfo"]["status"]["title"],
            cfg["redeemRequestSettings"]["shownInfo"]["status"]["text"],
            cfg["redeemRequestSettings"]["shownInfo"]["id"]["title"],
            cfg["redeemRequestSettings"]["shownInfo"]["id"]["text"],
            cfg["redeemRequestSettings"]["shownInfo"]["createdAt"]["title"],
            cfg["redeemRequestSettings"]["shownInfo"]["createdAt"]["text"],
            cfg["redeemRequestSettings"]["shownInfo"]["email"]["title"],
            cfg["redeemRequestSettings"]["shownInfo"]["email"]["text"],
            cfg["redeemRequestSettings"]["shownInfo"]["paymentMethod"]["title"],
            cfg["redeemRequestSettings"]["shownInfo"]["paymentMethod"]["text"],
            cfg["newDeviceSettings"]["embedSettings"]["colour"],
            cfg["newDeviceSettings"]["embedSettings"]["title"],
            cfg["newDeviceSettings"]["embedSettings"]["titleURL"], 
            cfg["newDeviceSettings"]["embedSettings"]["description"],
            cfg["newDeviceSettings"]["embedSettings"]["authorName"],
            cfg["newDeviceSettings"]["embedSettings"]["authorURL"],
            cfg["newDeviceSettings"]["embedSettings"]["authorIcon"],
            cfg["newDeviceSettings"]["embedSettings"]["image"],
            cfg["newDeviceSettings"]["embedSettings"]["thumbnail"],
            cfg["newDeviceSettings"]["embedSettings"]["footer"],
            cfg["newDeviceSettings"]["embedSettings"]["footerIcon"],
            cfg["newDeviceSettings"]["shownInfo"]["id"]["title"],
            cfg["newDeviceSettings"]["shownInfo"]["id"]["text"],
            cfg["newDeviceSettings"]["shownInfo"]["name"]["title"],
            cfg["newDeviceSettings"]["shownInfo"]["name"]["text"],
            cfg["newDeviceSettings"]["shownInfo"]["bw"]["title"],
            cfg["newDeviceSettings"]["shownInfo"]["bw"]["text"],
            cfg["newDeviceSettings"]["shownInfo"]["country"]["title"],
            cfg["newDeviceSettings"]["shownInfo"]["country"]["text"],
            cfg["newDeviceSettings"]["shownInfo"]["earned"]["title"],
            cfg["newDeviceSettings"]["shownInfo"]["earned"]["text"],
            cfg["newDeviceSettings"]["shownInfo"]["totalEarned"]["title"],
            cfg["newDeviceSettings"]["shownInfo"]["totalEarned"]["text"],
            cfg["newDeviceSettings"]["shownInfo"]["ips"]["title"],
            cfg["newDeviceSettings"]["shownInfo"]["ips"]["text"],
            cfg["newDeviceSettings"]["shownInfo"]["ips"]["separator"],
            cfg["newDeviceSettings"]["shownInfo"]["rate"]["title"],
            cfg["newDeviceSettings"]["shownInfo"]["rate"]["text"],
            cfg["newDeviceSettings"]["shownInfo"]["totalBw"]["title"],
            cfg["newDeviceSettings"]["shownInfo"]["totalBw"]["text"]
        ]) or not all(isinstance(i, int) for i in [
            cfg["ratelimitWait"], 
            cfg["delay"]
        ]) or not all(isinstance(i, bool) for i in [
            cfg["mysql"]["enabled"],
            cfg["balanceUpdateSettings"]["enabled"],
            cfg["balanceUpdateSettings"]["sqlEnabled"],
            cfg["balanceUpdateSettings"]["shownInfo"]["accountEmail"]["enabled"],
            cfg["balanceUpdateSettings"]["shownInfo"]["accountName"]["enabled"],
            cfg["balanceUpdateSettings"]["perDevice"],
            cfg["balanceUpdateSettings"]["embedSettings"]["embed"],
            cfg["balanceUpdateSettings"]["embedSettings"]["inline"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["deviceID"]["enabled"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["deviceType"]["enabled"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["bandwidth"]["enabled"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["country"]["enabled"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["earned"]["enabled"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["totalEarned"]["enabled"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["ips"]["enabled"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["rate"]["enabled"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["name"]["enabled"],
            cfg["balanceUpdateSettings"]["perDeviceShownInfo"]["totalBw"]["enabled"],
            cfg["balanceUpdateSettings"]["shownInfo"]["hourEarned"]["enabled"], 
            cfg["balanceUpdateSettings"]["shownInfo"]["hourEarnedAverage"]["enabled"],
            cfg["balanceUpdateSettings"]["shownInfo"]["refEarnings"]["enabled"],
            cfg["balanceUpdateSettings"]["shownInfo"]["promotionsEarnings"]["enabled"],
            cfg["balanceUpdateSettings"]["shownInfo"]["hourTraffic"]["enabled"],
            cfg["balanceUpdateSettings"]["shownInfo"]["balance"]["enabled"],
            cfg["balanceUpdateSettings"]["shownInfo"]["lifetimeBalance"]["enabled"],
            cfg["balanceUpdateSettings"]["shownInfo"]["activeDevices"]["enabled"],
            cfg["balanceUpdateSettings"]["shownInfo"]["inactiveDevices"]["enabled"],
            cfg["balanceUpdateSettings"]["shownInfo"]["totalDevices"]["enabled"],
            cfg["balanceUpdateSettings"]["shownInfo"]["promotionsEarnings"]["enabled"],
            cfg["balanceUpdateSettings"]["shownInfo"]["hourTraffic"]["enabled"],
            cfg["balanceUpdateSettings"]["shownInfo"]["balance"]["enabled"],
            cfg["balanceUpdateSettings"]["shownInfo"]["lifetimeBalance"]["enabled"],
            cfg["balanceUpdateSettings"]["shownInfo"]["activeDevices"]["enabled"],
            cfg["balanceUpdateSettings"]["shownInfo"]["deviceTypeActive"]["enabled"],
            cfg["balanceUpdateSettings"]["shownInfo"]["inactiveDevices"]["enabled"],
            cfg["balanceUpdateSettings"]["shownInfo"]["deviceTypeInactive"]["enabled"],
            cfg["balanceUpdateSettings"]["shownInfo"]["totalDevices"]["enabled"],
            cfg["balanceUpdateSettings"]["shownInfo"]["deviceTypeTotal"]["enabled"],
            cfg["balanceUpdateSettings"]["enabled"],
            cfg["balanceUpdateSettings"]["sendIfNotChanged"],
            cfg["appUpdateSettings"]["enabled"],
            cfg["appUpdateSettings"]["sqlEnabled"],
            cfg["appUpdateSettings"]["embedSettings"]["embed"],
            cfg["appUpdateSettings"]["embedSettings"]["inline"],
            cfg["appUpdateSettings"]["shownInfo"]["windows"]["enabled"],
            cfg["appUpdateSettings"]["shownInfo"]["mac"]["enabled"],
            cfg["redeemRequestSettings"]["enabled"],
            cfg["redeemRequestSettings"]["sqlEnabled"],
            cfg["redeemRequestSettings"]["embedSettings"]["embed"],
            cfg["redeemRequestSettings"]["embedSettings"]["inline"],
            cfg["redeemRequestSettings"]["shownInfo"]["amount"]["enabled"],
            cfg["redeemRequestSettings"]["shownInfo"]["referralsBonus"]["enabled"],
            cfg["redeemRequestSettings"]["shownInfo"]["promotionsBonus"]["enabled"],
            cfg["redeemRequestSettings"]["shownInfo"]["status"]["enabled"],
            cfg["redeemRequestSettings"]["shownInfo"]["id"]["enabled"],
            cfg["redeemRequestSettings"]["shownInfo"]["createdAt"]["enabled"],
            cfg["redeemRequestSettings"]["shownInfo"]["email"]["enabled"],
            cfg["redeemRequestSettings"]["shownInfo"]["paymentMethod"]["enabled"],
            cfg["newDeviceSettings"]["enabled"],
            cfg["newDeviceSettings"]["sqlEnabled"],
            cfg["newDeviceSettings"]["embedSettings"]["embed"],
            cfg["newDeviceSettings"]["embedSettings"]["inline"],
            cfg["newDeviceSettings"]["shownInfo"]["id"]["enabled"],
            cfg["newDeviceSettings"]["shownInfo"]["name"]["enabled"],
            cfg["newDeviceSettings"]["shownInfo"]["bw"]["enabled"],
            cfg["newDeviceSettings"]["shownInfo"]["country"]["enabled"],
            cfg["newDeviceSettings"]["shownInfo"]["earned"]["enabled"],
            cfg["newDeviceSettings"]["shownInfo"]["totalEarned"]["enabled"],
            cfg["newDeviceSettings"]["shownInfo"]["ips"]["enabled"],
            cfg["newDeviceSettings"]["shownInfo"]["rate"]["enabled"],
            cfg["newDeviceSettings"]["shownInfo"]["totalBw"]["enabled"],
            cfg["userDataSettings"]["sqlEnabled"],
            cfg["balanceUpdateSettings"]["sqlPerDevice"]
        ]):
            return("Config file is not correct. Please check the config.yml file and make sure all options are of the correct type.")

    except KeyError as e:
        return("Config file is not correct. Please check the config.yml file and make sure all options are there. Option missing: " + str(e))

    return("Config file is correct.")
