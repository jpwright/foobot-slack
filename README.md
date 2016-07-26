foobot-slack
============

Slack integration for [Foobot](http://foobot.io/).

You can use this script to customize Slack alerts when conditions exceed a certain threshold:

![Example Foobot alert](docs/alert_example.png)

You can also set this up as a bot to enable on-demand air quality graphs:

![Example Foobot query](docs/query_example.png)

Setup
-----

foobot-slack has the following dependencies: [requests](http://docs.python-requests.org/en/master/), [slackbot](https://github.com/lins05/slackbot), [pyfoobot](https://github.com/philipbl/pyfoobot>), [matplotlib](http://matplotlib.org/), [imgurpython](https://github.com/Imgur/imgurpython>). They can all be installed using pip:

```
$ pip install requests slackbot pyfoobot matplotlib imgurpython
```

You'll need to rename `config.example.txt` to `config.txt` and `slackbot_settings.example.py` to `slackbot_settings.py`. The API parameters for slack, foobot, and imgur are needed for full functionality. All other parameters can be omitted to use default settings.

To set up Slack integration, create an [incoming webhook](https://api.slack.com/incoming-webhooks) and/or create a [bot user](https://api.slack.com/bot-users).

The "SLACK_WEBHOOK" parameter should be the part of your webhook URL that comes AFTER (not including) "https://hooks.slack.com/services/".

You will also need to [register for a Foobot API key](https://api.foobot.io/apidoc/index.html) and [register for an imgur API application](https://api.imgur.com/#registerapp). imgur is used to host the graph images. Eventually this will be replaced by uploading directly to Slack.

Usage
-----

To check for alerts, run `python foobot_grapher.py`. I have this set up as a cron job, but keep in mind that Foobot has an API limit of 200 requests per day.

To run as a bot, run `python bot.py`. Invite the bot to a channel, and it will respond to any message directed at it containing the string "air quality".
