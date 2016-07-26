from slackbot.bot import Bot
from slackbot.bot import respond_to
import re
import foobot_grapher

def main():
	bot = Bot()
	bot.run()

@respond_to('air quality', re.IGNORECASE)
def air_quality(message):
    attachments = [
    {
        'fallback': 'Air quality graph',
	'image_url': foobot_grapher.getSensorReadings(False)
    }]
    message.send_webapi('', json.dumps(attachments))

if __name__ == "__main__":
    main()
