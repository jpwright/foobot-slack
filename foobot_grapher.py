#!/usr/bin/env python

from pyfoobot import Foobot
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.dates
import matplotlib.pyplot
import datetime
from imgurpython import ImgurClient
import ConfigParser

def getSensorReadings(notify):

	config = ConfigParser.ConfigParser()
	config.read("config.txt")

	settings = {
		'foobot_api_key': '',
		'foobot_email': '',
		'foobot_password': '',
		'imgur_id': '',
		'imgur_secret': '',
		'slack_webhook': '',
		'averaging_period': 15,
		'periods_to_graph': 12,
		'threshold_pm': 25.0,
		'threshold_temperature': 26.5,
		'threshold_humidity': 60.0,
		'threshold_co2': 30000.0,
		'threshold_tvoc': 500.0
	}

	for settings_key in settings:
		try:
			value_to_set = config.get('default', settings_key)
			settings[settings_key] = value_to_set
		except:
			pass

	imgur_supported = False

	if (len(settings['imgur_id']) > 0 and len(settings['imgur_secret']) > 0):
		imgur_supported = True
		imgur = ImgurClient(settings['imgur_id'], settings['imgur_secret'])

	fb = Foobot(settings['foobot_api_key'], settings['foobot_email'], settings['foobot_password'])
	devices = fb.devices()
	device = devices[0]

	measurement_interval = 60*(int(settings['averaging_period']) * int(settings['periods_to_graph']))

	data = device.data_period(measurement_interval, 0)

	alerts = []
	labels = ["PM2.5", "Temperature", "Humidity", "CO2", "tVOC"]
	units = ["ug/m3", "C", "%", "ppm", "ppb"]
	max_vals = [0, 0, 0, 0, 0]
	sums = [0, 0, 0, 0, 0]
	datapoints = [[], [], [], [], []]
	timeseries = []
	thresholds = [
		float(settings['threshold_pm']),
		float(settings['threshold_temperature']),
		float(settings['threshold_humidity']),
		float(settings['threshold_co2']),
		float(settings['threshold_tvoc'])
	]

	num_averaging_samples = int(len(data['datapoints']) / int(settings['periods_to_graph']))

	for i in range(0, len(data['datapoints'])):
		datapoint = data['datapoints'][i]
		time = datapoint[0]
		pm = datapoint[1]
		tmp = datapoint[2]
		hum = datapoint[3]
		co2 = datapoint[4]
		voc = datapoint[5]
		allpollu = datapoint[6]

		for j in range(0, 5):
			datapoints[j].append(datapoint[j+1])

			if (i >= (len(data['datapoints']) - num_averaging_samples)):
				sums[j] += datapoint[j+1]
				if datapoint[j] > max_vals[j]:
					max_vals[j] = datapoint[j+1]

		timeseries.append(datetime.datetime.fromtimestamp(time))

	hours = matplotlib.dates.HourLocator()
	minutes = matplotlib.dates.MinuteLocator(interval = 10)
	hoursFmt = matplotlib.dates.DateFormatter('%-I:%M')

	if notify:
		for i in range(0, 5):
			sums[i] = sums[i] / num_averaging_samples

			if sums[i] > thresholds[i]:
				print("Sending alert for "+labels[i])
				fig, ax = matplotlib.pyplot.subplots()
				ax.plot(timeseries, datapoints[i])

				ax.xaxis.set_major_locator(hours)
				ax.xaxis.set_major_formatter(hoursFmt)
				ax.grid(True)

				matplotlib.pyplot.xlabel("Time")
				matplotlib.pyplot.ylabel(labels[i] + " ("+units[i]+")")

				fig.autofmt_xdate()

				matplotlib.pyplot.savefig("figure.png")
				if imgur_supported:
					image = imgur.upload_from_path("figure.png", anon=True)
				else:
					image = {"link": "http://imgur.not.supported.com/alter_your_config.txt"}

				payload = '{"text": "Warning: '+labels[i]+' levels at '+"{0:.2f}".format(sums[i])+' '+units[i]+'.", "attachments": [{"fallback": "Graph.", "image_url": "'+image["link"]+'"}]}'
				r = requests.post("https://hooks.slack.com/services/"+settings['slack_webhook'], data={"payload": payload})

	else:
		fig, axarr = matplotlib.pyplot.subplots(1,5)
		for i in range(0, 5):
			ax = axarr[i]
			ax.plot(timeseries, datapoints[i])

			ax.xaxis.set_major_locator(hours)
			ax.xaxis.set_major_formatter(hoursFmt)
			ax.grid(True)

			ax.set_xlabel("Time")
			ax.set_title(labels[i] + " ("+units[i]+")")

			fig.autofmt_xdate()


		fig.set_size_inches(18, 4)
		matplotlib.pyplot.savefig("figure.png", bbox_inches='tight')

		if (imgur_supported):
			image = imgur.upload_from_path("figure.png", anon=True)
		else:
			image = {"link": "http://imgur.not.supported.com/alter_your_config.txt"}

		return image["link"]

if __name__ == "__main__":
	getSensorReadings(True)
