# deriving the latest base image
FROM python:alpine

# end user must pass in bot token (may not be needed)
ENV BOT_TOKEN="" 
# ENV UID=1000 GID=1000

# set the working directory
WORKDIR /usr/src/app

# copy python requirements
COPY requirements.txt ./

# install python requirements
RUN pip install -r requirements.txt

# copy bot files into container
COPY . .
# Now the structure looks like this: '/usr/src/app/bot'
# Mount /usr/src/app/files to persist "db"

# run bot 
CMD [ "python", "bot/bot.py"]