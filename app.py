from flask import Flask, render_template, redirect, request, jsonify
from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv()
app = Flask(__name__)

# Initialise supabase client
"""
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)
"""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # TODO: Create new user
        return redirect("/login")
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # TODO: Set auth code -- supabase?
        return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    # TODO: Logout code
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
