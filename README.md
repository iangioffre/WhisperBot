# WhisperBot for Discord

[![License](https://img.shields.io/npm/l/express.svg)](https://github.com/CalvinKotval/dc_roleselector/blob/master/LICENSE)
[![Donate](https://img.shields.io/badge/Donate-PayPal-blue.svg?style=flat&logo=paypal)](https://www.paypal.com/donate/?hosted_button_id=TYXMT8NWGKPV2&item_name=WhisperBot)


## Functionality
* Create messages and assign roles based on user reactions to message

## Commands
* /ping - sends message back to say it's working
* /roles - prints reaction object
* /clear_roles - clears all role-reaction relationships
* /create_role - creates a message with role-reaction inputs
* /edit_role - edits a given message with role-reaction inputs
* /add_role - adds to given message with role-reaction inputs  

Format for roles input: role1, reaction1, role2, reaction2, ...

## Setting up the bot
* add `.env` to root directory 
* put `BOT_TOKEN="<your token>"` into `.env`

## Running the bot (requires python3 and pip3)
* Linux/Mac: ./prod.sh
* Windows: .\prod.bat (or double click prod.bat)
  * pip install -r requirements.txt
  * python bot/bot.py

## Running the bot with watch changes (requires python3, pip3, nodejs, and npm)
* Linux/Mac: ./dev.sh
* Windows: .\dev.bat
  * pip install -r requirements.txt
  * npm install (may have to run `npm install -g nodemon` manually)
