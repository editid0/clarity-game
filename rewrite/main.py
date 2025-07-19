from flask import Flask, render_template, send_from_directory, request, redirect
from flask_socketio import SocketIO, join_room, send
from dotenv import load_dotenv
import os, uuid, random, string

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)
games = []


def find_game(game_id) -> dict:
    game_id = str(game_id)
    gm = next((game for game in games if game["id"] == game_id), None)
    return gm


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start")
def start():
    global games
    # Get cookies
    cookies = dict(request.cookies) or {}
    user = cookies.get("user_id")
    if not user:
        return "Error", 403
    params = dict(request.args) or {}
    rounds = int(params.get("rounds", 3))
    tbr = int(params.get("tbr", 30))
    images = random.sample(range(1, 11), rounds)
    share_code = "".join(random.choices(string.digits, k=6))
    game_obj = {
        "creator": user,
        "players": [
            user,
        ],
        "answers": [],
        "id": str(uuid.uuid4()),
        "images": images,
        "share": share_code,
        "status": 0,
        "step": 0,
        "rounds": rounds,
        "tbr": tbr,
    }
    games.append(game_obj)
    return redirect(f'/game/{game_obj["id"]}')


@app.route("/game/<uuid:code>")
def game_page(code):
    game = find_game(code)
    if not game:
        return "No game", 404
    return render_template("game.html", game=game)


@app.route("/public/<path:file>")
def send_public(file):
    return send_from_directory("public", file)


@socketio.on("join")
def room_joiner(data):
    if data.get("game"):
        join_room(data.get("game"))
        send({"user": data["user"]}, to=data.get("game"))


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=6970, debug=True)
