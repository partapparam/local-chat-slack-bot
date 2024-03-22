import logging

logging.basicConfig(level=logging.DEBUG)

from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from dotenv import load_dotenv
load_dotenv()
import os

TOKEN = os.getenv('TOKEN')
AUTH = os.getenv('AUTH')
URL = os.getenv(key='URL')
SLACK_BOT_TOKEN = os.getenv(key='SLACK_BOT_TOKEN')
SLACK_SIGNING_SECRET=os.getenv(key='SLACK_SIGNING_SECRET')

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


@app.event("app_mention")
def event_test(body, say, logger):
    logger.info(body)
    say("What's up?")


@app.command("/partap-dev")
def handle_message(ack,logger):
    ack()
    print('this is happened')


from flask import Flask, request

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    print('events hit')
    return handler.handle(request)

# @flask_app.route("/slack/command", methods=["POST"])
# def slack_events():
#     print('this is hit')
#     return handler.handle(request)

