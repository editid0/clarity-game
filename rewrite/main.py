from flask import (
    Flask,
    render_template,
    send_from_directory,
    request,
    redirect,
    Response,
)
from flask_socketio import SocketIO, join_room, send, emit
from dotenv import load_dotenv
import os, uuid, random, string

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)
games = []
user_map = {}
ANSWERS = {
    "1": "duck",
    "2": "forest",
    "3": "beach",
    "4": "plane",
    "5": "volcano",
    "6": "dog",
    "7": "cat",
    "8": "fox",
    "9": "house",
    "10": "school",
    "11": "castle",
    "12": "taxi",
    "13": "airport",
    "14": "chef",
    "15": "pizza",
    "16": "burger",
    "17": "clock",
}
letter_map = {}
for index, word in ANSWERS.items():
    letter_map[index] = len(word)

URL = os.getenv("URL")


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
    images = random.sample(range(1, len(list(ANSWERS.keys())) + 1), rounds)
    share_code_1 = "".join(random.choices(string.digits[1:], k=1))
    share_code_5 = "".join(random.choices(string.digits, k=5))
    share_code = share_code_1 + share_code_5
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
        "letter_map": letter_map,
    }
    games.append(game_obj)
    return redirect(f'/game/{game_obj["id"]}')


@app.route("/join/<int:share>")
def join_game(share):
    game = next((game for game in games if game["share"] == str(share)), None)
    if not game:
        return "no game", 404
    if game["status"] > 0:
        return "Game started", 403
    cookies = dict(request.cookies) or {}
    res = Response()
    user = cookies.get("user_id")
    set_cookie = False
    if not user:
        user = str(uuid.uuid4())
        set_cookie = True
    index = games.index(game)
    players = games[index]["players"]
    if user not in players:
        games[index]["players"].append(user)
    if set_cookie:
        return render_template("cookiesetter.html")
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
    return render_template("game.html", game=game, URL=URL)


@app.route("/game/<uuid:code>/scores")
def game_scores(code):
    code = str(code)
    game = find_game(code)
    if not game:
        return "No game", 404
    player_count = len(game["players"])
    scores = []
    for k, v in game["scores"].items():
        username = user_map.get(k, "New User")
        scores.append({"name": username, "score": v})
    current_scores = len(scores)
    return render_template(
        "scores.html", scores=scores, player_count=player_count, current=current_scores
    )


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
    round = data.get("round")
    step = data.get("step")
    points = 5 - step
    gm = find_game(game)
    text = text.lower()
    text = text[:15]
    print(step, text, round, gm["images"])
    current_image = gm["images"][round - 1]
    correct_answer = ANSWERS[str(current_image)]
    print(correct_answer)
    if text != correct_answer:
        if step == 3:
            emit(
                "guess_response",
                {
                    "correct": False,
                    "user": user,
                    "start": correct_answer[0],
                    "end": correct_answer[-1],
                    "hint": True,
                },
                to=game,
            )
        else:
            emit(
                "guess_response",
                {
                    "correct": False,
                    "user": user,
                    "hint": False,
                },
                to=game,
            )
        print("bad")
    else:
        emit("guess_response", {"correct": True, "user": user, "hint": False}, to=game)
        index = games.index(gm)
        scores = games[index]["scores"]
        if not scores.get(user):
            scores[user] = points
        else:
            scores[user] += points


@socketio.on("chat")
def on_chat(data):
    print("got chat")
    user = data.get("user")
    text = data.get("text")
    game = data.get("game")
    if not user or not text or not game:
        print("blank")
        return
    if not find_game(game):
        print("no game")
        return
    text = text[:50]
    socketio.emit("chat", {"user": user, "content": text}, to=game)
    print("emitted")


if __name__ == "__main__":
    socketio.run(
        app, host="0.0.0.0", port=6970, debug=False, allow_unsafe_werkzeug=True
    )
