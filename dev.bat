@echo off
call pip install -r requirements.txt
call npm install
call npm install -g nodemon
call nodemon --watch bot --exec python bot/bot.py
