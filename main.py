import os
import logging
logging.basicConfig(level=logging.DEBUG)

# Use the package we installed
from slack_bolt import App
from slack_bolt import (Say, Respond, Ack)
from slack_bolt.adapter.flask import SlackRequestHandler
from typing import (Dict, Any)
from slack_sdk.web import WebClient, SlackResponse
from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler
from dotenv import load_dotenv
load_dotenv()
import requests
import json
import asyncio
from flask import Flask, request 


TOKEN = os.getenv('TOKEN')
AUTH = os.getenv('AUTH')
URL = os.getenv(key='URL')
SLACK_BOT_TOKEN = os.getenv(key='SLACK_BOT_TOKEN')
SLACK_SIGNING_SECRET=os.getenv(key='SLACK_SIGNING_SECRET')

# Initialize your app with your bot token and signing secret
app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
    raise_error_for_unhandled_request=True
)

@app.middleware  # or app.use(log_request)
def log_request(logger, body, next):
    logger.debug(body)
    print('middleware')
    return next()

app.client.retry_handlers.append(RateLimitErrorRetryHandler(max_retry_count=2))
def here(error, body, logger):
    logger.exception(f"Error: {error}")
    logger.info(f"Request body: {body}")
    # breakpoint()
    print('here')

app.error(func=here)

def hit_serp(query, session):
    payload = json.dumps({
 "query": query
})
    serp_headers = {
 'token': TOKEN,
 'Content-Type': 'application/json',
 'proxy':'False',
 'session': 'False',
 'Authorization': AUTH}
    serp_response = requests.request(method="POST", url=URL, headers=serp_headers, data=payload)
    return json.loads(serp_response._content)


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

# get files
# files = client.files_list
# file_list = files.data['files']
file_id = 'F06QD203VNJ'


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

# # Ready? Start your app!
# if __name__ == "__main__":
#     app.start(port=int(os.environ.get("PORT", 3000)))

# Load bot in async mode
async def start():
    await app.start(port=int(os.environ.get("PORT", 3000)))

# if __name__ == "__main__":
#     logger = app.logger
#     try:
#         asyncio.run(start())
#         logger.info('App started.')
#     except KeyboardInterrupt:
#         logger.info('App stopped by user.')
#     except Exception as e:
#         logger.info('App stopped due to error.')
#         logger.error(str(e))
#     finally:
#         logger.info('App stopped.')

# Start flask app for Production App
flask_app = Flask(__name__)
handler = SlackRequestHandler(app=app)
@flask_app.route(rule='/slack/events', methods=['GET', 'POST'])
def slack_events():
    return handler.handle(req=request)
