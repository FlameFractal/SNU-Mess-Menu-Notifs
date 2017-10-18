from flask import Flask, request
import bs4 as bs
import requests
import json
import os
import datetime
app = Flask(__name__)

############# Some Variables

botToken = str(os.environ.get('botToken'))
myjsonId = str(os.environ.get('myjsonId'))
botUsername = str(os.environ.get('botUsername'))
myjsonUrl = 'https://api.myjson.com/bins/'+myjsonId;
messUrl = 'http://messmenu.snu.in/messMenu.php/'
replyMarkup = '&reply_markup={"keyboard":[["/dh1_notifs","/dh2_notifs"],["/both_notifs", "/unregister"],["/dh1_menu","/dh2_menu"]]}'

users = requests.get(myjsonUrl).json()


############# Some important functions

def sendMessage(msg, user_id):
	requests.get('https://api.telegram.org/bot'+botToken+'/sendMessage?parse_mode=Markdown&chat_id='+str(user_id)+'&text='+msg+replyMarkup)

def generateMenu(mess, menuTable):
	details = menuTable[mess].find_all('td')
	message = "*Menu for DH +"+str(mess)+"*\n\n"

	if('No Menu' in details[0].text.strip()):
		message = message + "_No Menu Available!_"
	else:		
		#Get the date of the menu
		message = message + "*"+menuTable[mess].find_all('label')[0].text.strip() + "*\n\n" 	
		t = datetime.datetime.now()
		if t.hour<5:
			message = message + "*Breakfast*\n----------------\n"
			for dish in details[1].find_all('p'):
				#Get each dish
				message = message+dish.text+"\n" 
		elif 5<=t.hour<=12:
			message = message + "*Lunch*\n----------------\n"
			for dish in details[2].find_all('p'):
				#Get each dish
				message = message+dish.text+"\n" 
		else:
			message = message + "*Dinner*\n----------------\n"
			for dish in details[3].find_all('p'):
				#Get each dish
				message = message+dish.text+"\n" 

	return message


def sendMenu(user_id, mess_choice):
	menuTable = (bs.BeautifulSoup(requests.get(messUrl).text,'lxml')).find_all(id='dh2MenuItems')
	message = ""
	if mess_choice in [0, 1]:
		message = generateMenu(mess_choice, menuTable)
	elif mess_choice == 2:
		message = generateMenu(0, menuTable) + "\n\n" + generateMenu(1, menuTable)

	sendMessage(message, user_id)


def sendFullMenu(user_id, mess_choice):
	menuTable = (bs.BeautifulSoup(requests.get(messUrl).text,'lxml')).find_all(id='dh2MenuItems')
	details = menuTable[mess_choice].find_all('td')
	message = generateMenu(mess_choice, menuTable)

	sendMessage(message, user_id)


############# APIs to talk to the bot

@app.route('/botWebhook'+botToken, methods=['POST'])
def webhook_handler():
	response = request.get_json()
	user_msg = ''
	print(response)
	
	if "message" in response:
		user_id = str(response["message"]["chat"]["id"])
		if "text" in response["message"]: 
			user_msg = str(response["message"]["text"])
	else:
		user_id = str(response["edited_message"]["chat"]["id"])
		if "text" in response["message"]:
			user_msg = str(response["edited_message"]["text"])


	if user_msg == '/start':
		sendMessage("Hello there! Welcome!", user_id)
		sendMessage("Your request for notifications has been registered.\nDefault Mess DH-2 selected.\nType '/' to switch mess!", user_id)
		users[user_id] = 1
	elif user_msg == '/dh1_notifs':
		users[user_id] = 0
		sendMessage("Your request for notifications has been registered.\nMess DH-1 selected.\nThank you!", user_id)
	elif user_msg == '/dh2_notifs':
		users[user_id] = 1
		sendMessage("Your request for notifications has been registered.\nMess DH-2 selected.\nThank you!", user_id)
	elif user_msg == '/both_notifs':
		users[user_id] = 2
		sendMessage("Your request for notifications has been registered.\nMess DH-1 and DH-2 selected.\nThank you!", user_id)
	elif user_msg == '/unregister':
		users[user_id] = -1
		sendMessage("Your request for unregistering for notifications has been noted.\nThank you!", user_id)
	elif user_msg == '/dh1_menu':
		sendFullMenu(user_id, 0)
	elif user_msg == '/dh2_menu':
		sendFullMenu(user_id, 1)
	elif user_msg == '/author':
		sendMessage("Resides here: [https://github.com/flamefractal/](https://github.com/flamefractal/)", user_id)
	else:
		sendMessage("Oops! I don't understand that yet!\nType '/' to see all the commands I do understand.", user_id)
	
	requests.put(myjsonUrl, headers={'content-type':'application/json', 'data-type':'json'}, data=json.dumps(users))
	# sendMessage(str(response),os.environ.get('debugId')) -> Inline Keyboard expected, sendMessage by default uses replyMarkup
	requests.get('https://api.telegram.org/bot'+botToken+'/sendMessage?parse_mode=Markdown&chat_id='+str(os.environ.get('debugId'))+'&text='+str(response))

	return(str(users))


@app.route('/sendMenuAllUsers'+botToken, methods=['GET'])
def sendMenuAllUsers():
	for user_id in users:
		# send only if registered
		if users[user_id] >= 0:
			sendMenu(user_id, users[user_id])
		return("Menu successfully sent.")


@app.route('/')
def root():
	return "<a href='http://t.me/"+botUsername+"'>http://t.me/"+botUsername+"</a>"

@app.route('/<path:path>')
def catch_all(path):
	return "<a href='http://t.me/"+botUsername+"'>http://t.me/"+botUsername+"</a>"


############# Start the flask server!

if __name__ == "__main__":
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)