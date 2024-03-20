import os
# Use the package we installed
from slack_bolt import App
from slack_sdk.web import WebClient
from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler
import os
from dotenv import load_dotenv
load_dotenv()
import requests
import json

TOKEN = os.getenv('TOKEN')
AUTH = os.getenv('AUTH')
serpAPI = "http://3.236.218.40:443/iquery"

# Initialize your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)
app.client.retry_handlers.append(RateLimitErrorRetryHandler(max_retry_count=2))


def hit_serp(query, session):
    payload = json.dumps({
 "query": query
})
    print(session)
    serp_headers = {
 'token': TOKEN,
 'Content-Type': 'application/json',
 'proxy':'False',
 'session': 'False',
 'Authorization': AUTH}
    serp_response = requests.request(method="POST", url=serpAPI, headers=serp_headers, data=payload)
    return json.loads(serp_response._content)


@app.event('app_mention')
def reply_back(event, say):
    text = event['text'].split('>')[1]
    response = hit_serp(text, 'False')
    answer = json.loads(response['response'])['answer']
    say(text=f'<@{event["user"]}>, {answer}', channel=event['channel'])



# @app.event("app_home_opened") etc.
@app.event('app_home_opened')
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


# Ready? Start your app!
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
