
#export GOOGLE_APPLICATION_CREDENTIALS="Natural Language-7b0e42d436f7.json"

import csv
from googleapiclient import discovery
import httplib2
from oauth2client.client import GoogleCredentials

DISCOVERY_URL = ('https://{api}.googleapis.com/'
                '$discovery/rest?version={apiVersion}')

http = httplib2.Http()

credentials = GoogleCredentials.get_application_default().create_scoped(
 ['https://www.googleapis.com/auth/cloud-platform'])

http=httplib2.Http()
credentials.authorize(http)

service = discovery.build('language', 'v1beta1',
                       http=http, discoveryServiceUrl=DISCOVERY_URL)


def parse_csv(file):
	reader = csv.reader(open(file))

	result = {}
	list_keys = []
	for row in reader:
		list_keys.append(row[0])
		key = row[0]
		result[key] = row[1:]
		#1st column = Name of Youtube account
		#2nd column = Time
		#3rd column = Timestamp
		#4th column = Comment snippet
		#5th column = Number of likes
	return list_keys, result


def each_sentiment(comment):
	service_request = service.documents().analyzeSentiment(
	body={
	 'document': {
	    'type': 'PLAIN_TEXT',
	    'content': comment
	 }
	})

	response = service_request.execute()
	polarity = response['documentSentiment']['polarity']
	magnitude = response['documentSentiment']['magnitude']
	score = polarity*magnitude
	return score,polarity, magnitude


def all_sentiment(list_keys,result,limit_comment):
	result_sentiment = {}
	for key in list_keys[1:limit_comment]:
		comment_snippet = result[key][3]
		try: 
			result_sentiment[key] = each_sentiment(comment_snippet)
		except HttpError:
			result_sentiment[key] = (0,0,0)
	return result_sentiment	


def sort_negative(result,result_sentiment,limit):
	sorted_keys = sorted(result_sentiment,key=result_sentiment.get)
	sorted_keys = sorted_keys[0:limit]
	for key in sorted_keys:
		print ("Comment: " + result[key][3] +
			"\n Score: " + str(result_sentiment[key][0]) +
			"\n ID: " + str(key) + "\n"
			)
	return None


def main(file,limit_comment,limit_result):
	list_keys,result = parse_csv(file)
	result_sentiment = all_sentiment(list_keys,result,limit_comment)
	sort_negative(result,result_sentiment,limit_result)
	return None

if __name__=='__main__':
	main("testcsv2.csv",50,10)

