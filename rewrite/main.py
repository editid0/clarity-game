from flask import Flask, render_template, send_from_directory, request, redirect
from flask_socketio import SocketIO, join_room, send, emit
from dotenv import load_dotenv
import os, uuid, random, string

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)
games = []
user_map = {}
letter_map = {
    "1": 4,
    "2": 6,
    "3": 5,
    "4": 5,
}


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
    images = random.sample(range(1, 5), rounds)
    share_code = "".join(random.choices(string.digits, k=6))
    game_obj = {
        "creator": user,
        "players": [
            user,
        ],
        "answers": [],
        "scores": {},
        "id": str(uuid.uuid4()),
        "images": images,
        "share": share_code,
        "status": 0,
        "step": 0,
        "rounds": rounds,
        "tbr": tbr,
        "letter_map": letter_map,
    }
    games.append(game_obj)
    return redirect(f'/game/{game_obj["id"]}')


@app.route("/join/<int:share>")
def join_game(share):
    # TODO, GENERATE A COOKIE FOR THE USER ID IF THERE ISN'T ONE
    # Find the game
    game = next((game for game in games if game["share"] == str(share)), None)
    if not game:
        return "no game", 404
    if game["status"] > 0:
        return "Game started", 403
    cookies = dict(request.cookies) or {}
    user = cookies.get("user_id")
    if not user:
        return "Error", 403
    index = games.index(game)
    players = games[index]["players"]
    if user not in players:
        games[index]["players"].append(user)
    return redirect(f"/game/{game['id']}")


@app.route("/game/<uuid:code>")
def game_page(code):
    game = find_game(code)
    if not game:
        return "No game", 404
    cookies = dict(request.cookies) or {}
    user = cookies.get("user_id")
    if not user:
        return "Error", 403
    if user not in game["players"]:
        return "Not in this game", 403
    return render_template("game.html", game=game)


@app.route("/public/<path:file>")
def send_public(file):
    return send_from_directory("public", file)


@socketio.on("join")
def room_joiner(data):
    if data.get("game"):
        join_room(data.get("game"))
        emit("new_user", {"user": data.get("user", "")}, to=data.get("game"))


@socketio.on("whois")
def room_joiner(data):
    if data.get("id"):
        emit(
            "user_name",
            {"display": user_map.get(data.get("id"), "New User"), "id": data.get("id")},
            to=data.get("game"),
        )


@socketio.on("rename")
def renamer(data):
    if data.get("id") and data.get("game") and data.get("name"):
        user_map[data.get("id")] = data.get("name")
        emit(
            "renamed",
            {"id": data.get("id"), "name": data.get("name")},
            to=data.get("game"),
        )


@socketio.on("start_game")
def start_game(data):
    game = data.get("game")
    user = data.get("user")
    game_o = find_game(game)
    if not game_o:
        print("no game")
        return
    if not game_o["creator"] == user:
        print("no creator")
        return
    index = games.index(game_o)
    games[index]["status"] = 1  # This prevents new people joining
    emit("start", games[index], to=game)


@socketio.on("guess")
def user_guess(data):
    text = data.get("text", "")
    user = data.get("user")
    game = data.get("game")
    gm = find_game(game)
    answers = {"1": "duck", "2": "forest", "3": "beach", "4": "plane"}
    text = text.lower()
    text = text[:15]
    print(gm)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=6970, debug=True)
