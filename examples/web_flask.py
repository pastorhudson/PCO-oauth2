#!/usr/bin/env python3
# Install dependencies with:
# pip install -r requirements.txt
# You need to put your Client ID and Secret in environment variables PCO_CLIENT_ID & PCO_CLIENT_SECRET respectively
# You also need to add http://localhost:5000/auth/callback as your callback uri
import os
import logging
import requests
from requests_oauth2.services import PlanningCenterClient

from requests_oauth2 import OAuth2BearerToken
from flask import Flask, request, redirect, session, jsonify


app = Flask(__name__)
# You need to put your Client ID and Secret in environment variables PCO_CLIENT_ID & PCO_CLIENT_SECRET respectively
app.client_id = os.environ["PCO_CLIENT_ID"]
app.secret_key = os.environ["PCO_CLIENT_SECRET"]

pco_auth = PlanningCenterClient(
    client_id=app.client_id,
    client_secret=app.secret_key,
    redirect_uri='http://localhost:5000/auth/callback'
)


@app.route("/")
def index():
    return redirect("/pco/")


@app.route("/pco/")
def pco_index():
    info = ""
    if not session.get("access_token"):
        return redirect("/auth/callback")
    with requests.Session() as s:
        s.auth = OAuth2BearerToken(session["access_token"])
        r = s.get("https://api.planningcenteronline.com/people/v2/people")
    r.raise_for_status()
    data = r.json()
    return jsonify(data)


@app.route("/auth/callback")
def pco_oauth2callback():
    code = request.args.get("code")
    error = request.args.get("error")
    if error:
        return "error :( {!r}".format(error)
    if not code:
        return redirect(pco_auth.authorize_url(
            scope=["people", "services", "check_ins", "resources"],
            response_type="code",
        ))
    data = pco_auth.get_token(
        code=code,
        grant_type="authorization_code",
    )
    session["access_token"] = data.get("access_token")
    return redirect("/")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True)
