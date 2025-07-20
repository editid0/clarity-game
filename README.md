# clarity-game
A game where you have to try guess the content of a picture that starts blurred, and gets less blurry as the game goes on.

# How to play
There is a guide for how to play on the homepage.

# How to host
This was made to run on python 3.12, but it should run on any version that supports function type hinting.
## Prerequisites
You need to have python installed.
You need to have pip installed.
Make sure you're in the rewrite folder.
## Install requirements
`pip3 install -r requirements.txt`
## Create `.env` file
The following content is needed in a .env file in the rewrite folder:
```env
SECRET_KEY=YourSecretKey
URL=http://localhost:6070
```
The secret key is used for socketio, and the url is used for the share link on the create game page.
## Running
To run the app, run the following command:
### Linux/Mac
```
python3 main.py
```
### Windows
```
py -3 main.py
```