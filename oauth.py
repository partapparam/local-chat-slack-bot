import os
from slack_bolt import App
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore
from dotenv import load_dotenv
from typing import Any, List
load_dotenv()
import yaml

SLACK_CLIENT_SECRET = os.getenv(key='SLACK_CLIENT_SECRET')
SLACK_CLIENT_ID = os.getenv(key='SLACK_CLIENT_ID')
# Get SLack Scopes from yaml file
# will eb a string
def get_scopes() -> List:
    with open(file='./src/templates/scopes.yaml', mode='r') as file:
        config = yaml.safe_load(file) 
    scopes_list = config['scopes']['user'] + config['scopes']['bot']
    return scopes_list

oauth_settings = OAuthSettings(
    client_id=SLACK_CLIENT_ID,
    client_secret=SLACK_CLIENT_SECRET,
    scopes=get_scopes(),
    installation_store=FileInstallationStore(base_dir="./data/installations"),
    state_store=FileOAuthStateStore(expiration_seconds=600, base_dir="./data/states")
)

app = App(
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
    oauth_settings=oauth_settings
)