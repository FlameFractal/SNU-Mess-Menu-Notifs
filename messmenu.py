import bs4 as bs
import urllib.request
from flask import Flask, request
import json
import os
import datetime
app = Flask(__name__)

############# Some Variables

botToken = '439142723:AAGxI51LsPuv0dgzta0lGgH1aJLZfIuDTvE';
users = dict()
replyMarkup = '&reply_markup={"keyboard":[["/dh1_notifs","/dh2_notifs"],["/dh1_menu","/dh2_menu"]]}'

if os.path.exists('users.json'):
	with open('users.json', 'r') as f:
		users = json.load(f)

print(users)
print("Printed users")

############# Some important functions

def sendMessage(msg, user_id):
	urllib.request.urlopen('https://api.telegram.org/bot'+botToken+'/sendMessage?parse_mode=Markdown&chat_id='+user_id+'&text='+urllib.parse.quote_plus(msg)+replyMarkup)


def sendMenu(user_id, mess_choice):
	menuTable = (bs.BeautifulSoup(urllib.request.urlopen('http://messmenu.snu.in/messMenu.php/').read(),'lxml')).find_all(id='dh2MenuItems')
	details = menuTable[mess_choice].find_all('td')
	
	message = "*Menu for DH 1*\n\n" if mess_choice == 0 else "*Menu for DH 2*\n\n"
	#Get the date of the menu
	message = message + "*"+menuTable[mess_choice].find_all('label')[0].text.strip() + "*\n\n" 
	
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

	sendMessage(message, user_id)
	print("Menu "+str(mess_choice)+" sent successfully to "+user_id)


def sendFullMenu(user_id, mess_choice):
	menuTable = (bs.BeautifulSoup(urllib.request.urlopen('http://messmenu.snu.in/messMenu.php/').read(),'lxml')).find_all(id='dh2MenuItems')
	details = menuTable[mess_choice].find_all('td')
	
	message = "*Menu for DH 1*\n\n" if mess_choice == 0 else "*Menu for DH 2*\n\n"
	#Get the date of the menu
	message = message + "*"+menuTable[mess_choice].find_all('label')[0].text.strip() + "*\n\n" 
	
	message = message + "*Breakfast*\n----------------\n"
	for dish in details[1].find_all('p'):
		#Get each dish
		message = message+dish.text+"\n" 
	message = message + "*\nLunch*\n----------------\n"
	for dish in details[2].find_all('p'):
		#Get each dish
		message = message+dish.text+"\n" 
	message = message + "*\nDinner*\n----------------\n"
	for dish in details[3].find_all('p'):
		#Get each dish
		message = message+dish.text+"\n"  


	sendMessage(message, user_id)
	print("Menu "+str(mess_choice)+" sent successfully to "+user_id)



############# APIs to talk to the bot

@app.route('/botWebhook'+botToken, methods=['POST'])
def webhook_handler():
	response = request.get_json()
	print(response)

	
	if "message" in response:
		user_id = str(response["message"]["chat"]["id"])
		user_msg = str(response["message"]["text"])
	else:
		user_id = str(response["edited_message"]["chat"]["id"])
		user_msg = str(response["edited_message"]["text"])
	
	print(user_msg)


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
	elif user_msg == '/dh1_menu':
		sendFullMenu(user_id, 0)
	elif user_msg == '/dh2_menu':
		sendFullMenu(user_id, 1)
	elif user_msg == '/author':
		sendMessage("Resides here: [https://github.com/flamefractal/](https://github.com/flamefractal/)", user_id)
	else:
		sendMessage("Oops! I don't understand that yet!\nType '/' to see all the commands I do understand.", user_id)
	
	with open('users.json', 'w') as f:
		json.dump(users, f)

	return(str(users))


@app.route('/sendMenuAllUsers'+botToken, methods=['GET'])
def sendMenuAllUsers():
	for user in users:
		sendMenu(user, users[user])
		return("Menu successfully sent.")


@app.route('/')
def root():
    return "<a href='http://t.me/SNUMessBot'>http://t.me/SNUMessBot</a>"

@app.route('/<path:path>')
def catch_all(path):
    return "<a href='http://t.me/SNUMessBot'>http://t.me/SNUMessBot</a>"


############# Start the flask server!

if __name__ == "__main__":
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)