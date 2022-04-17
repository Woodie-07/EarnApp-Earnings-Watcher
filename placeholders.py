"""
EarnApp-Earnings-Watcher - A program to monitor your EarnApp Earnings and send data to a discord webhook
Copyright (C) 2022  SWM Tech Industries

This file is part of EarnApp-Earnings-Watcher.

EarnApp-Earnings-Watcher is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

EarnApp-Earnings-Watcher is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with EarnApp-Earnings-Watcher. If not, see <https://www.gnu.org/licenses/>.
"""

def basicPlaceholderReplace(text: str, version: str, state: str) -> str:
    return (text.replace("{{version}}", version)
                .replace("{{state}}", state)
            )

def appUpdatePlaceholderReplace(text: str, oldAppVersions: dict, newAppVersions: dict) -> str:
    return (text.replace("{{win_old_version}}", oldAppVersions["win"])
                .replace("{{win_new_version}}", newAppVersions["win"])
                .replace("{{mac_old_version}}", oldAppVersions["mac"])
                .replace("{{mac_new_version}}", newAppVersions["mac"])
    )

def balanceUpdatePlaceholderReplace(text: str, oldData: dict, newData: dict, averageList: list) -> str:
    oldTotalBw = 0
    for device in oldData["devices"]:
        try:
            oldTotalBw += device["total_bw"]
        except KeyError:
            pass

    newTotalBw = 0
    for device in newData["devices"]:
        try:
            newTotalBw += device["total_bw"]
        except KeyError:
            pass


    return (text.replace("{{account_email}}", newData["userData"]["email"])
                .replace("{{account_name}}", newData["userData"]["name"])
                .replace("{{hour_earned}}", "{:.2f}".format(newData["money"]["earnings_total"] - oldData["money"]["earnings_total"], 2))
                .replace("{{hour_earned_average}}", "{:.2f}".format(averageList[0]/averageList[1], 2))
                .replace("{{ref_earned}}", "{:.2f}".format(newData["money"]["ref_bonuses"] - oldData["money"]["ref_bonuses"], 2))
                .replace("{{promo_earned}}", "{:.2f}".format(newData["money"]["promo_bonuses"] - oldData["money"]["promo_bonuses"], 2))
                .replace("{{hour_traffic_gb}}", str(round((newTotalBw - oldTotalBw) / 1024 / 1024 / 1024, 2)))
                .replace("{{hour_traffic_mb}}", str(round((newTotalBw - oldTotalBw) / 1024 / 1024, 2)))
                .replace("{{hour_traffic_kb}}", str(round((newTotalBw - oldTotalBw) / 1024, 2)))
                .replace("{{hour_traffic}}", str(round(newTotalBw - oldTotalBw, 2)))
                .replace("{{balance}}", str(round(newData["money"]["balance"], 2)))
                .replace("{{lifetime_balance}}", str(newData["money"]["earnings_total"]))
    )

def newDevicePlaceholderReplace(text: str, device: dict, IPsSeparator: str) -> str:
    ips = ""
    try:
        for ip in device["ips"]:
            ips += ip + IPsSeparator
    except KeyError:
        pass

    if ips == "":
        ips = "-"
    elif len(ips) > 0:
        ips = ips[:len(IPsSeparator) * -1]
    try:
        device["total_bw"]
    except KeyError:
        device["total_bw"] = 0

    return (text.replace("{{id}}", device["uuid"])
                .replace("{{name}}", device["title"])
                .replace("{{bw_gb}}", str(round(device["total_bw"] / 1024 / 1024 / 1024, 2)))
                .replace("{{bw_mb}}", str(round(device["total_bw"] / 1024 / 1024, 2)))
                .replace("{{bw_kb}}", str(round(device["total_bw"] / 1024, 2)))
                .replace("{{bw}}", str(device["total_bw"]))
                .replace("{{country}}", device["country"].lower() if device["country"] else "Unknown")
                .replace("{{earned}}", "{:.2f}".format(device["earned"]))
                .replace("{{total_earned}}", str(device["earned_total"]))
                .replace("{{ips}}", ips)
                .replace("{{rate}}", str(device["rate"]))
                .replace("{{total_bw_gb}}", str(round(device["total_bw"] / 1024 / 1024 / 1024, 2)))
                .replace("{{total_bw_mb}}", str(round(device["total_bw"] / 1024 / 1024, 2)))
                .replace("{{total_bw_kb}}", str(round(device["total_bw"] / 1024, 2)))
                .replace("{{total_bw}}", str(round(device["total_bw"], 2)))
    )

def redeemRequestPlaceholderReplace(text: str, data: dict) -> str:
    return (text.replace("{{amount}}", "{:.2f}".format(data["money_amount"]))
                .replace("{{referrals_bonus}}", "{:.2f}".format(data["ref_bonuses_amount"]))
                .replace("{{promotions_bonus}}", "{:.2f}".format(data["promo_bonuses_amount"]))
                .replace("{{status}}", data["status"])
                .replace("{{id}}", data["uuid"])
                .replace("{{created_at}}", data["date"])
                .replace("{{email}}", data["email"])
                .replace("{{payment_method}}", data["payment_method"])
    )
