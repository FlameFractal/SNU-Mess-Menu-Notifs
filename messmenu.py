import bs4 as bs
import urllib.request
from flask import Flask, request
import json
import os

app = Flask(__name__)


botToken = '439142723:AAGxI51LsPuv0dgzta0lGgH1aJLZfIuDTvE';
users = [
	{"user_id": '206914582', "mess_choice": 1},
]


def sendMessage(msg, user_id):
	urllib.request.urlopen('https://api.telegram.org/bot'+botToken+'/sendMessage?parse_mode=Markdown&chat_id='+user_id+'&text='+urllib.parse.quote_plus(msg))


@app.route('/registerNotifications'+botToken, methods=['POST'])
def webhook_handler():
	#response = json.loads(urllib.request.urlopen('https://api.telegram.org/bot439142723:AAGxI51LsPuv0dgzta0lGgH1aJLZfIuDTvE/getupdates').read().decode('utf-8'))
	response = request.get_json()
	print(response)

	new_user={}
	if "message" in response:
		new_user["user_id"] = str(response["message"]["chat"]["id"])
	else:
		new_user["user_id"] = str(response["edited_message"]["chat"]["id"])
	
	new_user["mess_choice"] = 1 #response["message"]["text"]
	
	if not new_user in users:
		users.append(new_user)
	
	sendMessage("Your request for notifications has been registered.\nDefault Mess DH-2 selected.\nThank you!", new_user["user_id"])
	return(str(users))


@app.route('/sendMenu'+botToken, methods=['GET'])
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
	    return("Menu successfully sent.")

	    

@app.route('/')
def root():
    return "<a href='http://t.me/SNUMessBot'>http://t.me/SNUMessBot</a>"

@app.route('/<path:path>')
def catch_all(path):
    return "<a href='http://t.me/SNUMessBot'>http://t.me/SNUMessBot</a>"



if __name__ == "__main__":
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)