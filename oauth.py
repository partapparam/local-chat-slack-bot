import code
import os
from slack_bolt import App
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.oauth.installation_store import FileInstallationStore, Installation
from slack_sdk.oauth.state_store import FileOAuthStateStore
from dotenv import load_dotenv
from slack_sdk.web import WebClient, SlackResponse
from typing import Any, List, Dict
load_dotenv()
import yaml
import json
from slack_bolt.oauth.callback_options import CallbackOptions, SuccessArgs, FailureArgs
from slack_bolt.response import BoltResponse
from flask import Flask, request, make_response
import html
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt import (Say, Respond, Ack)
from utils import custom_routes



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

def install_store ():
    breakpoint()
     
    
oauth_settings = OAuthSettings(
    client_id=SLACK_CLIENT_ID,
    client_secret=SLACK_CLIENT_SECRET,
    scopes=config['scopes']['bot'],
    user_scopes=config['scopes']['user'],
    installation_store=FileInstallationStore(base_dir="./data/installations"),
    state_store=FileOAuthStateStore(expiration_seconds=600, base_dir="./data/states"),
    redirect_uri=None,
    install_path="/slack/install",
    redirect_uri_path="/slack/oauth_redirect",
    callback_options=callback_options,
)

app = App(
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
    oauth_settings=oauth_settings
)

@app.event(event='app_mention')
def reply_back(event, body, respond, say, context, client, message, payload, view) -> SlackResponse:
    breakpoint()
    text = event['text'].split('>')[1]
    response = hit_serp(query=text, session='False')
    answer = json.loads(response['response'])['answer']
    thread_ts = event["thread_ts"]
    conversation_replies = app.client.conversations_replies(channel=event["channel"], ts=thread_ts)

    # Get the thread messages
    thread_messages = conversation_replies["messages"]
    return say(text=f'<@{event["user"]}>, {answer}', channel=event['channel'])

@app.command(command='/partap-dev')
def handle_modify_bot(ack: Ack, body: Dict[str, Any], respond: Respond, context, client, payload, command) -> None:
    """
    Handle the /modify-bot command
    This function modifies the Bots scope and access for questions
    """
    ack()
    channel_id = body['channel_id']
    trigger_id = body['trigger_id']
    print(channel_id, trigger_id)
     # Load modify_bot_template.json payload
    with open(f'./src/templates/file_upload_template.json', 'r') as f:
        view = json.load(f)
    respond(f"{command['text']}")
    client.views_open(trigger_id=trigger_id, view=view)
    breakpoint()


# @app.event("app_home_opened") etc.
@app.event(event='app_home_opened')
def update_home_tab(client, event, logger):
  print('\n\n\nclient', client.__dict__, '\n\n', event, '\n', logger, '\n\n\n')
  try:
    # views.publish is the method that your app uses to push a view to the Home tab
    client.views_publish(
      # the user that opened your app's app home
      user_id=event["user"],
      # the view object that appears in the app home
      view={
        "type": "home",
        "callback_id": "home_view",

        # body of the view
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Welcome to your _App's Home tab_* :tada:"
            }
          },
          {
            "type": "divider"
          },
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "This button won't do much for now but you can set up a listener for it using the `actions()` method and passing its unique `action_id`. See an example in the `examples` folder within your Bolt app."
            }
          },
          {
            "type": "actions",
            "elements": [
              {
                "type": "button",
                "text": {
                  "type": "plain_text",
                  "text": "Click me!"
                }
              }
            ]
          }
        ]
      }
    )

  except Exception as e:
    logger.error(f"Error publishing home tab: {e}")

# # Issue and consume state parameter value on the server-side.
# state_store = FileOAuthStateStore(expiration_seconds=300, base_dir="./data")
# # Persist installation data and lookup it by IDs.
# installation_store = FileInstallationStore(base_dir="./data")


# Start flask app for Production App
flask_app = Flask(__name__)
handler = SlackRequestHandler(app=app)
@flask_app.route(rule='/slack/events', methods=['GET', 'POST'])
def slack_events():
    return handler.handle(req=request)

@flask_app.route('/slack/install')
def slack_install():
    print('getting slack install')
    return custom_routes.workspace_install_html


# Issue and consume state parameter value on the server-side.
state_store = FileOAuthStateStore(expiration_seconds=300, base_dir="./data")
# Persist installation data and lookup it by IDs.
installation_store = FileInstallationStore(base_dir="./data")

@flask_app.route('/slack/oauth_redirect')
def slack_oauth():
    # Retrieve the auth code and state from the request params
    if "code" in request.args:
        # Verify the state parameter
        if state_store.consume(request.args["state"]):
            client = WebClient()  # no prepared token needed for this
            # Complete the installation by calling oauth.v2.access API method
            oauth_response = client.oauth_v2_access(
                client_id=SLACK_CLIENT_ID,
                client_secret=SLACK_CLIENT_SECRET,
                redirect_uri="https://worthy-slightly-cod.ngrok-free.app/slack/success",
                code=request.args["code"]
            )
            installed_enterprise = oauth_response.get("enterprise") or {}
            is_enterprise_install = oauth_response.get("is_enterprise_install")
            installed_team = oauth_response.get("team") or {}
            installer = oauth_response.get("authed_user") or {}
            incoming_webhook = oauth_response.get("incoming_webhook") or {}
            bot_token = oauth_response.get("access_token")
            # NOTE: oauth.v2.access doesn't include bot_id in response
            bot_id = None
            enterprise_url = None
            if bot_token is not None:
                auth_test = client.auth_test(token=bot_token)
                bot_id = auth_test["bot_id"]
                if is_enterprise_install is True:
                    enterprise_url = auth_test.get("url")

            installation = Installation(
                app_id=oauth_response.get("app_id"),
                enterprise_id=installed_enterprise.get("id"),
                enterprise_name=installed_enterprise.get("name"),
                enterprise_url=enterprise_url,
                team_id=installed_team.get("id"),
                team_name=installed_team.get("name"),
                bot_token=bot_token,
                bot_id=bot_id,
                bot_user_id=oauth_response.get("bot_user_id"),
                bot_scopes=oauth_response.get("scope"),  # comma-separated string
                user_id=installer.get("id"),
                user_token=installer.get("access_token"),
                user_scopes=installer.get("scope"),  # comma-separated string
                incoming_webhook_url=incoming_webhook.get("url"),
                incoming_webhook_channel=incoming_webhook.get("channel"),
                incoming_webhook_channel_id=incoming_webhook.get("channel_id"),
                incoming_webhook_configuration_url=incoming_webhook.get("configuration_url"),
                is_enterprise_install=is_enterprise_install,
                token_type=oauth_response.get("token_type"),
            )
            print(installation)

            # Store the installation
            installation_store.save(installation)

            return "Thanks for installing this app!"
        else:
            return make_response(f"Try the installation again (the state value is already expired)", 400)

    error = request.args["error"] if "error" in request.args else ""
    return make_response(f"Something is wrong with the installation (error: {html.escape(error)})", 400)