"""
Flask app: use WITHOUT login (guest) or WITH Google login.

- Guest  -> data kept only in the browser session (lost when session ends)
- Logged in -> data saved in the database, available whenever the user returns
- Logout -> clears the session

Install:   pip install flask authlib flask-sqlalchemy requests
Env vars:  GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, SECRET_KEY
Google console redirect URI:  http://127.0.0.1:5000/auth/callback
"""
import os
from flask import (Flask, redirect, url_for, session, request,
                   jsonify, render_template_string)
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
db = SQLAlchemy(app)

oauth = OAuth(app)
oauth.register(
    name="google",
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


# ---------- Database models ----------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255))


class Item(db.Model):
    """Replace this with whatever data your website needs to save."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)


with app.app_context():
    db.create_all()


def current_user():
    uid = session.get("user_id")
    return db.session.get(User, uid) if uid else None


# ---------- Auth routes ----------
@app.route("/login")
def login():
    return oauth.google.authorize_redirect(url_for("auth_callback", _external=True))


@app.route("/auth/callback")
def auth_callback():
    token = oauth.google.authorize_access_token()
    info = token["userinfo"]
    user = User.query.filter_by(email=info["email"]).first()
    if not user:
        user = User(email=info["email"], name=info.get("name"))
        db.session.add(user)
        db.session.commit()

    # Move anything the person did as a guest into their account
    for text in session.pop("guest_items", []):
        db.session.add(Item(user_id=user.id, content=text))
    db.session.commit()

    session["user_id"] = user.id
    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ---------- Data API (works for guest AND logged-in) ----------
@app.route("/api/items", methods=["GET", "POST"])
def items():
    user = current_user()

    if request.method == "POST":
        text = (request.json or {}).get("content", "").strip()
        if not text:
            return jsonify(error="empty"), 400
        if user:                                   # saved in database
            db.session.add(Item(user_id=user.id, content=text))
            db.session.commit()
        else:                                      # guest: session only
            session["guest_items"] = session.get("guest_items", []) + [text]

    if user:
        data = [i.content for i in Item.query.filter_by(user_id=user.id)]
    else:
        data = session.get("guest_items", [])
    return jsonify(items=data, logged_in=bool(user))


# ---------- Page ----------
PAGE = """
<!doctype html>
<title>My Website</title>
<body style="font-family:sans-serif;max-width:600px;margin:40px auto">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <h2>My Website</h2>
    <div>
      {% if user %}
        Hi, {{ user.name or user.email }}
        <a href="/logout">Logout</a>
      {% else %}
        Guest mode &nbsp; <a href="/login">Login with Google</a>
      {% endif %}
    </div>
  </div>

  {% if not user %}
    <p style="color:#a60">You are not logged in. Your data will not be saved
    permanently. Log in with Gmail to keep it.</p>
  {% endif %}

  <input id="box" placeholder="Type something" style="width:70%">
  <button onclick="add()">Save</button>
  <ul id="list"></ul>

<script>
async function load(){
  const r = await fetch('/api/items'); const d = await r.json();
  list.innerHTML = d.items.map(i => '<li>'+i.replace(/</g,'&lt;')+'</li>').join('');
}
async function add(){
  await fetch('/api/items',{method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({content:box.value})});
  box.value=''; load();
}
load();
</script>
</body>
"""


@app.route("/")
def home():
    return render_template_string(PAGE, user=current_user())


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
    