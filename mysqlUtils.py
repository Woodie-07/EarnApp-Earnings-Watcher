"""
EarnApp-Earnings-Watcher - A program to monitor your EarnApp Earnings and send data to a discord webhook
Copyright (C) 2023  Woodie

This file is part of EarnApp-Earnings-Watcher.

EarnApp-Earnings-Watcher is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

EarnApp-Earnings-Watcher is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
    
You should have received a copy of the GNU General Public License along with EarnApp-Earnings-Watcher. If not, see <https://www.gnu.org/licenses/>.
"""

import mysql.connector
from log import *
from datetime import datetime

host = None
user = None
password = None
database = None

conn: mysql.connector.MySQLConnection = None

def init(cfg: dict):
    """
    Initializes the MySQL connection.
    """

    global host, user, password, database

    host = cfg["mysql"]["host"]
    user = cfg["mysql"]["user"]
    password = cfg["mysql"]["password"]
    database = cfg["mysql"]["database"]

    info("Connecting to MySQL database...")
    conn = mysql.connector.connect(
        host=host,
        user=user,
        passwd=password,
    )
    cursor = conn.cursor()

    conn

    info("Connected to MySQL database.")

    info("Setting up database")
    cursor.execute("CREATE DATABASE IF NOT EXISTS " + database)
    cursor.execute("USE " + database)
    # create tables for app updates, user data, money, devices, and transactions
    cursor.execute("CREATE TABLE IF NOT EXISTS appUpdates (id INT AUTO_INCREMENT PRIMARY KEY, winVer VARCHAR(255), macVer VARCHAR(255), date DATETIME)")
    cursor.execute("CREATE TABLE IF NOT EXISTS userData (id INT AUTO_INCREMENT PRIMARY KEY, firstName VARCHAR(255), lastName VARCHAR(255), fullName VARCHAR(255), email VARCHAR(255), locale VARCHAR(6), onboarding DATETIME, pictureURL VARCHAR(255), refCode VARCHAR(255), date DATETIME)")
    cursor.execute("CREATE TABLE IF NOT EXISTS money (id INT AUTO_INCREMENT PRIMARY KEY, balance FLOAT(8,2), totalEarnings FLOAT(8,2), multiplier FLOAT, promoBonuses FLOAT(8,2), promoBonusesTotal FLOAT(8,2), redeemEmail VARCHAR(255), minRedeem FLOAT(8,2), paymentMethod VARCHAR(255), refBonuses FLOAT(8,2), refBonusesTotal FLOAT(8,2), referralPercentage VARCHAR(255), date DATETIME)")
    cursor.execute("CREATE TABLE IF NOT EXISTS transactions (id VARCHAR(24) PRIMARY KEY, email VARCHAR(255), amount FLOAT(8,2), paymentDate DATETIME, paymentMethod VARCHAR(255), promoBonusesAmount FLOAT(8,2), refBonusesAmount FLOAT(8,2), status VARCHAR(255), uuid VARCHAR(255), refCode VARCHAR(255), creationDate DATETIME)")
    cursor.execute("CREATE TABLE IF NOT EXISTS devices (id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, uuid TINYTEXT, appid TINYTEXT, billing TINYTEXT, bw BIGINT UNSIGNED, country TINYTEXT, earned FLOAT(8,2), earnedTotal FLOAT(8,2), ips TEXT, rate FLOAT(8,2), redeem_bw BIGINT UNSIGNED, title TINYTEXT, total_bw BIGINT UNSIGNED, datetime DATETIME, money_id INT, FOREIGN KEY (money_id) REFERENCES money(id))")

    conn.commit()
    cursor.close()
    conn.close()

def addUserData(userData: dict, cfg: dict):
    """
    Adds the user data to the MySQL database.
    """
    info("Connecting to MySQL database...")
    conn = mysql.connector.connect(
        host=host,
        user=user,
        passwd=password,
        database=database
    )
    cursor = conn.cursor()

    info("Connected to MySQL database.")

    firstName, lastName, fullName, email, locale, onboarding, pictureURL, refCode = userData["first_name"], userData["last_name"], userData["name"], userData["email"], userData["locale"], userData["onboarding"], userData["picture"], userData["referral_code"]

    #cursor.execute("SELECT * FROM userData WHERE email = %s ORDER BY id DESC LIMIT 1", (userData["email"],))
    cursor.execute("SELECT * FROM userData WHERE email = %s", (userData["email"],))

    # check if anything has changed
    rowCount = cursor.rowcount
    if rowCount == 1:
        row = cursor.fetchone()
        if row[1] != firstName or row[2] != lastName or row[3] != fullName or row[4] != email or row[5] != locale or row[6] != onboarding or row[7] != pictureURL or row[8] != refCode:
            update = True
            print("User data has changed")
        else:
            print("No changes detected.")
    else:
        update = True
        print("No previous user data found.")

    cursor.fetchall()

    if update:
        info("Adding user data to database")
        cursor.execute("INSERT INTO userData (firstName, lastName, fullName, email, locale, onboarding, pictureURL, refCode, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (
            firstName, 
            lastName, 
            fullName, 
            email, 
            locale, 
            datetime.strptime(onboarding, "%Y-%m-%dT%H:%M:%S.%fZ"), 
            pictureURL, 
            refCode, 
            datetime.now()
        ))
        conn.commit()
        cursor.close()
        conn.close()

def addAppUpdate(appUpdate: dict, cfg: dict):
    """
    Adds the app update to the MySQL database.
    """
    info("Connecting to MySQL database...")
    conn = mysql.connector.connect(
        host=host,
        user=user,
        passwd=password,
        database=database,
    )
    info("Connected to MySQL database.")
    cursor = conn.cursor()

    info("Adding app update to database")
    cursor.execute("INSERT INTO appUpdates (winVer, macVer, date) VALUES (%s, %s, %s)", (appUpdate["win"], appUpdate["mac"], datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()

def addMoneyUpdate(money: dict, cfg: dict) -> int:
    """
    Adds the money info to the MySQL database.
    """
    info("Connecting to MySQL database...")
    conn = mysql.connector.connect(
        host=host,
        user=user,
        passwd=password,
        database=database,
    )
    info("Connected to MySQL database.")
    cursor = conn.cursor()

    info("Adding money info to database")
    cursor.execute("INSERT INTO money (balance, totalEarnings, multiplier, promoBonuses, promoBonusesTotal, redeemEmail, minRedeem, paymentMethod, refBonuses, refBonusesTotal, referralPercentage, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (money["balance"], money["earnings_total"], money["multiplier"], money["promo_bonuses"], money["promo_bonuses_total"], money["redeem_details"]["email"], money["redeem_details"]["min_redeem"], money["redeem_details"]["payment_method"], money["ref_bonuses"], money["ref_bonuses_total"], money["referral_part"], datetime.now()))
    moneyRow = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()

    return moneyRow

def addTransaction(transaction: dict, cfg: dict):
    """
    Adds the transaction to the MySQL database.
    """
    info("Connecting to MySQL database...")
    conn = mysql.connector.connect(
        host=host,
        user=user,
        passwd=password,
        database=database,
    )
    info("Connected to MySQL database.")
    cursor = conn.cursor()

    info("Adding transaction to database")
    cursor.execute("INSERT INTO transactions (email, amount, paymentDate, paymentMethod, promoBonusesAmount, refBonusesAmount, status, uuid, refCode, creationDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (transaction["email"], transaction["amount"], datetime.strptime(transaction["payment_date"], "%Y-%m-%dT%H:%M:%S.%fZ"), transaction["payment_method"], transaction["promo_bonuses_amount"], transaction["ref_bonuses_amount"], transaction["status"], transaction["uuid"], transaction["referral_code"], datetime.strptime(transaction["creation_date"], "%Y-%m-%dT%H:%M:%S.%fZ")))
    conn.commit()
    cursor.close()
    conn.close()

def addDevices(devices: list, cfg: dict, moneyRow: int):
    """
    Adds a list of devices to the MySQL database
    """
    info("Connecting to MySQL database...")
    conn = mysql.connector.connect(
        host=host,
        user=user,
        passwd=password,
        database=database,
    )
    info("Connected to MySQL database.")
    cursor = conn.cursor()

    info("Adding devices to database")
    for device in devices:
        cursor.execute("INSERT INTO devices (uuid, appid, billing, bw, country, earned, earnedTotal, ips, rate, redeem_bw, title, total_bw, money_id, datetime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (device["uuid"], device["appid"], device["billing"], device["bw"], device["country"], device["earned"], device["earned_total"], " ".join(device["ips"]), device["rate"], device["redeem_bw"], device["title"], device["total_bw"], moneyRow, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()