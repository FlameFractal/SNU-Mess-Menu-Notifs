import bs4 as bs
import urllib.request
from flask import Flask, request
import json


botToken = '439142723:AAGxI51LsPuv0dgzta0lGgH1aJLZfIuDTvE';

users = [
	{"user_id": '206914582', "mess_choice": 1},
]



def sendMessage(msg, user_id):
	urllib.request.urlopen('https://api.telegram.org/bot'+botToken+'/sendMessage?parse_mode=Markdown&chat_id='+user_id+'&text='+urllib.parse.quote_plus(msg))



app = Flask(__name__)
@app.route('/', methods=['POST'])
def result():
	#response = json.loads(urllib.request.urlopen('https://api.telegram.org/bot439142723:AAGxI51LsPuv0dgzta0lGgH1aJLZfIuDTvE/getupdates').read().decode('utf-8'))
	response = request.get_json()
	print(response)

	new_user={}
	new_user["user_id"] = str(response["result"][0]["message"]["chat"]["id"])
	new_user["mess_choice"] = 1 #response["result"][0]["message"]["text"]
	if not new_user in users:
		users.append(new_user)
	sendMessage("Your request for notifications has been registered.\nDefault Mess DH-2 selected.\nThank you!", str(response["result"][0]["message"]["chat"]["id"]))

	return("Success.")



def sendMenu():
	menuTable = (bs.BeautifulSoup(urllib.request.urlopen('http://messmenu.snu.in/messMenu.php/').read(),'lxml')).find_all(id='dh2MenuItems')

	for user in users:
	    message = "*Menu for DH 1*\n\n" if user['mess_choice'] == 0 else "*Menu for DH 2*\n\n"
	    #Get the date of the menu
	    message = message + "*"+menuTable[user['mess_choice']].find_all('label')[0].text.strip() + "*\n" 
	    for time in menuTable[user['mess_choice']].find_all('td'): 
	        for dish in time.find_all('p'):
	            #Get each dish
	            message = message+dish.text+"\n" 
	        #Seperate breakfast, lunch, dinner
	        message = message+"----------------\n" 

	    sendMessage(message, user['user_id'])



sendMenu()