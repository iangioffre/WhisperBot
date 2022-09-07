#!/bin/bash
pip3 install -r requirements.txt
npm install
npm install -g nodemon
nodemon --watch bot --exec python3 bot/bot.py
