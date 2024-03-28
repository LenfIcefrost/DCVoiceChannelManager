# DCVoiceChannelManager

Help member create voice channel and manage channel themself

### Requirement
python>=3.8
python3-virtualenv

## Installation

```shell
pip install discord.py
```

## activative the python virtual environment
```shell
$ python3 -m venv <virtual environment name> # If not created, creating virtualenv

$ source ./<virtual environment name>/bin/activate # Activating virtualenv (for bash)

(<virtual environment name>)$ pip3 install -r ./requirements.txt # Activating virtualenv

(<virtual environment name>)$ deactivate # When you want to leave virtual environment
```

## Setting before use
1. find static_data.py 
2. set bot_token at Line 5



## How to use
```shell
python main.py
```

### 加入伺服器
https://discord.com/api/oauth2/authorize?client_id=1114240368033144943&permissions=8&scope=bot%20applications.commands
