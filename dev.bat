@echo off
pip install -r requirements.txt
npm install
npm install -g nodemon
nodemon --watch bot --exec python bot/bot.py
