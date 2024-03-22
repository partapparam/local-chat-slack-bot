# Import the async app instead of the regular one
from slack_bolt.async_app import AsyncApp
from dotenv import load_dotenv
load_dotenv()
import os

TOKEN = os.getenv('TOKEN')
AUTH = os.getenv('AUTH')
URL = os.getenv(key='URL')
SLACK_BOT_TOKEN = os.getenv(key='SLACK_BOT_TOKEN')
SLACK_SIGNING_SECRET=os.getenv(key='SLACK_SIGNING_SECRET')

# Initialize your app with your bot token and signing secret
app = AsyncApp(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
    raise_error_for_unhandled_request=True
)
@app.event("app_mention")
async def event_test(body, say, logger):
    logger.info(body)
    await say("What's up?")

@app.command("/partap")
async def command(ack, body, respond):
    await ack()
    await respond(f"Hi <@{body['user_id']}>!")

# @app.error
# def handle_error():
#     breakpoint()

if __name__ == "__main__":
    app.start(3000)