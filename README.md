# DCVoiceChannelManager

Help member create voice channel and manage channel themselves

## Requirements
- python>=3.8
- python3-virtualenv

## activate the python virtual environment
### For Linux
```shell
$ python3 -m venv <virtual environment name> # If not created, creating virtualenv

$ source ./<virtual environment name>/bin/activate # Activating virtualenv (for bash)

(<virtual environment name>)$ pip3 install -r ./requirements.txt # Activating virtualenv

(<virtual environment name>)$ deactivate # When you want to leave virtual environment
```

### For Windows
```shell
$ python -m venv <virtual environment name> # If not created, creating virtualenv

$ ./<virtual environment name>/Scripts/activate # Activating virtualenv (for bash) 

(<virtual environment name>)$ pip3 install -r ./requirements.txt # Activating virtualenv

(<virtual environment name>)$ deactivate # When you want to leave virtual environment
```

## Setting before use
1. find static_data.py 
2. set bot_token at Line 5
3. execute main.py

## Create your own bot
Make sure enable the privileged gateway intents
![image](https://i.imgur.com/hGgeknf.jpeg)

## Invite this bot into your own server
https://discord.com/api/oauth2/authorize?client_id=1114240368033144943&permissions=8&scope=bot%20applications.commands
