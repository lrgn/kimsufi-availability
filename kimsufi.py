#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Find the Kimsufi servers availability, and send a message via Telegram when a server is available.
"""

import sys

import requests
import json
import os

from telegram.ext import Updater, CommandHandler

import config

VERSION = "1.0"

API_URL = "https://ws.ovh.com/dedicated/r2/ws.dispatcher/getAvailability2"
REFERENCES = {
    "1801sk12": "KS-1 France",
    "1804sk12": "KS-1 Canada"
}

ZONES = {'gra': 'Gravelines',
         'sbg': 'Strasbourg',
         'rbx': 'Roubaix',
         'bhs': 'Beauharnois'}

CURRENT_PATH = os.path.dirname(__file__)


def get_zone_name(zone):
    # rbx-hz to rbx
    zone = zone.split('-')[0]
    if zone in ZONES:
        return ZONES[zone]
    else:
        return zone


def get_servers():
    """Get the servers from the OVH API."""

    print("Get servers...")

    r = requests.get(API_URL)
    response = r.json()['answer']['availability']

    search = REFERENCES

    return [k for k in response if any(r == k['reference'] for r in search)]


def get_ref(name):
    """Return the reference based on the server model."""

    return list(REFERENCES.keys())[list(REFERENCES.values()).index(name)]


def sayhi(bot, job):
    kim = get_servers()

    total = 0
    output = ""

    for k in kim:
        output += "\n{}\n".format(REFERENCES[k['reference']])
        output += "{}\n".format("=" * len(REFERENCES[k['reference']]))

        for z in k['zones']:
            invalids = ['unavailable', 'unknown']
            availability = z['availability']
            if not availability in invalids:
                total += 1
            output += '{} : {}\n'.format(get_zone_name(z['zone']), availability)

    output += "\n=======\nRESULT : {0} server{1} {2} available on Kimsufi\n=======\n".format(
        total,
        "s"[total <= 1:],
        ["is", "are"][total > 1]
    )

    if total != 0:
        job.context.message.reply_text(output)


def start(bot, update, job_queue):
    bot.sendMessage(chat_id=update.message.chat_id, text="Hello there! I'll keep an eye on Kimsufi, and send you a message when a server is available.")
    job = job_queue.run_repeating(sayhi, 300, context=update)


if __name__ == '__main__':
    updater = Updater(token=config.API_KEY)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start, pass_job_queue=True)
    dispatcher.add_handler(start_handler)
    updater.start_polling()
    updater.idle()
