import os
from slack_bolt import App
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore
from dotenv import load_dotenv
from typing import Any, List
load_dotenv()
import yaml
from slack_bolt.oauth.callback_options import CallbackOptions, SuccessArgs, FailureArgs
from slack_bolt.response import BoltResponse
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler


def success(args: SuccessArgs) -> BoltResponse:
    assert args.request is not None
    return BoltResponse(
        status=200,  # you can redirect users too
        body="Your own response to end-users here"
    )

def failure(args: FailureArgs) -> BoltResponse:
    assert args.request is not None
    assert args.reason is not None
    return BoltResponse(
        status=args.suggested_status_code,
        body="Your own response to end-users here"
    )

callback_options = CallbackOptions(success=success, failure=failure)


SLACK_CLIENT_SECRET = os.getenv(key='SLACK_CLIENT_SECRET')
SLACK_CLIENT_ID = os.getenv(key='SLACK_CLIENT_ID')
# Get SLack Scopes from yaml file
# will be a string
with open(file='./src/templates/scopes.yaml', mode='r') as file:
        config = yaml.safe_load(file) 
    

oauth_settings = OAuthSettings(
    client_id=SLACK_CLIENT_ID,
    client_secret=SLACK_CLIENT_SECRET,
    scopes=config['scopes']['bot'],
    user_scopes=config['scopes']['user']
    installation_store=FileInstallationStore(base_dir="./data/installations"),
    state_store=FileOAuthStateStore(expiration_seconds=600, base_dir="./data/states")
    redirect_uri=None,
    install_path="/slack/install",
    redirect_uri_path="/slack/oauth_redirect",
    callback_options=callback_options,
)

app = App(
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
    oauth_settings=oauth_settings
)

# Start flask app for Production App
flask_app = Flask(__name__)
handler = SlackRequestHandler(app=app)
@flask_app.route(rule='/slack/events', methods=['GET', 'POST'])
def slack_events():
    return handler.handle(req=request)