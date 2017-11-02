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
appUrl = str(os.environ.get('appUrl'))
debugId = str(os.environ.get('debugId'))
secretSauce = str(os.environ.get('secretSauce'))
myjsonUrl = 'https://api.myjson.com/bins/'+myjsonId;
messUrl = 'http://messmenu.snu.in/messMenu.php/'
replyMarkup = '{"keyboard":[["/dh1_notifs", "/dh2_notifs"],["/both_notifs", "/deregister"],["/dh1_menu", "/dh2_menu"], ["/dh2_extras", "/help"]]}'

users = requests.get(myjsonUrl).json()
print(users)

############# Some important functions

def sendMessage(user_id, msg):
	requests.get('https://api.telegram.org/bot'+botToken+'/sendMessage?parse_mode=Markdown&chat_id='+str(user_id)+'&text='+msg+'&reply_markup='+replyMarkup+'&disable_web_page_preview=TRUE')

def sendPhoto(user_id, photo, caption=''):
	requests.get('https://api.telegram.org/bot'+botToken+'/sendPhoto?chat_id='+str(user_id)+'&photo='+str(photo)+'&caption='+str(caption)+'&replyMarkup='+replyMarkup)

def generateMenu(mess, menuTable):
	details = menuTable[mess].find_all('td')
	message = "*Menu for DH +"+str(mess+1)+"*\n\n"

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
			message = message + "*\nLunch*\n----------------\n"
			for dish in details[2].find_all('p'):
				#Get each dish
				message = message+dish.text+"\n"
			message = message + "*\nDinner*\n----------------\n"
			for dish in details[3].find_all('p'):
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
	try:
		menuTable = (bs.BeautifulSoup(requests.get(messUrl, timeout=1).text,'lxml')).find_all(id='dh2MenuItems')
		message = ""
		if mess_choice in [0, 1]:
			message = generateMenu(mess_choice, menuTable)
		elif mess_choice == 2:
			message = generateMenu(0, menuTable) + "\n--------------------------\n" + generateMenu(1, menuTable)
		sendMessage(user_id, message)
	except requests.exceptions.RequestException as e:
		sendMessage(user_id, str(e))
		sendMessage(user_id, "Mess website is not responding. Please check at "+messUrl)


def sendFullMenu(user_id, mess_choice):
	try:
		menuTable = (bs.BeautifulSoup(requests.get(messUrl, timeout=1).text,'lxml')).find_all(id='dh2MenuItems')
		details = menuTable[mess_choice].find_all('td')
		message = "*Menu for DH 1*\n\n" if mess_choice == 0 else "*Menu for DH 2*\n\n"

		if('No Menu' in details[0].text.strip()):
			message = message + "_No Menu Available!_"
		else:
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
		sendMessage(user_id, message)
	except requests.exceptions.RequestException as e:
		sendMessage(user_id, str(e))
		sendMessage(user_id, "Mess website is not responding. Please check at "+messUrl)

############# APIs to talk to the bot

@app.route('/botWebhook'+botToken, methods=['POST'])
def webhook_handler():
	response = request.get_json()
	user_msg = ''
	print(response)
	
	if "message" in response:
		user_id = str(response["message"]["chat"]["id"])
		users[user_id][1] = response["message"]["chat"]["first_name"]
		if "last_name" in response["message"]["chat"]:
			users[user_id][1] = users[user_id][1] + " " + response["message"]["chat"]["last_name"]
		if "username" in response["message"]["chat"]:
			users[user_id][2] = response["message"]["chat"]["username"]
		if "text" in response["message"]: 
			user_msg = str(response["message"]["text"])
	else:
		user_id = str(response["edited_message"]["chat"]["id"])
		users[user_id][1] = response["edited_message"]["chat"]["first_name"]
		if "last_name" in response["edited_message"]["chat"]:
			users[user_id][1] = users[user_id][1] + " " + response["message"]["chat"]["last_name"]
		if "username" in response["edited_message"]["chat"]:
			users[user_id][2] = response["message"]["chat"]["username"]
		if "text" in response["edited_message"]:
			user_msg = str(response["edited_message"]["text"])


	if user_msg == '/start':
		sendMessage(user_id, "Hello there! Welcome!")
		sendMessage(user_id, "Your request for notifications has been registered.\nDefault Mess DH-2 selected.\nType '/help' to switch mess!")
		users[user_id][0] = 1
	elif user_msg == '/dh1_notifs':
		users[user_id][0] = 0
		sendMessage(user_id, "Your request for notifications has been registered.\nMess DH-1 selected.\nThank you!")
	elif user_msg == '/dh2_notifs':
		users[user_id][0] = 1
		sendMessage(user_id, "Your request for notifications has been registered.\nMess DH-2 selected.\nThank you!")
	elif user_msg == '/both_notifs':
		users[user_id][0] = 2
		sendMessage(user_id, "Your request for notifications has been registered.\nMess DH-1 and DH-2 selected.\nThank you!")
	elif user_msg == '/deregister':
		users[user_id][0] = -1
		sendMessage(user_id, "Your request for deregistering for notifications has been noted.\nThank you!")
	elif user_msg == '/dh1_menu':
		sendFullMenu(user_id, 0)
	elif user_msg == '/dh2_menu':
		sendFullMenu(user_id, 1)
	elif user_msg == '/dh2_extras':
		sendPhoto(user_id, 'AgADBQAD2qcxG0eK2VfpzkXxLhHWRaQYzDIABHPxFna3WsVEDKgDAAEC', 'DH2 extras menu')
	elif '/adhoc_update'+secretSauce in user_msg:
		new_menu = user_msg.replace('/adhoc_update'+secretSauce,'')
		if '/dh1' in new_menu:
			new_menu = new_menu.replace('/dh1 ','')
			new_menu = "*Menu for DH1*\n\n"+new_menu
			for user in users:
				if users[user][0] == 0 or users[user][0] == 2:
					sendMessage(user, new_menu.strip())
		elif '/dh2' in new_menu:
			new_menu = new_menu.replace('/dh2 ','')
			new_menu = "*Menu for DH2*\n\n"+new_menu
			for user in users:
				if users[user][0] == 1 or users[user][0] == 2:
					sendMessage(user, new_menu.strip())
		else:
			sendMessage(user_id, "Oops. Did not understand that.")
	elif user_msg == '/help':
		sendMessage(user_id, """Hi! I'll send you Mess Menu notifications three times a day, right before your meal timings : 7:30AM, 11:30AM, 7:30PM.\n

You can use these commands to interface with me:\n

/dh1\_notifs - Daily notifications for DH1
/dh2\_notifs - Daily notifications for DH2
/both\_notifs - Daily notifications for BOTH
/deregister - NO daily notifications
/dh1\_menu - Get today's DH1 Menu
/dh2\_menu - Get today's DH2 Menu
/dh2\_extras - DH2's Rollu, Evening, Drinks menu.
/help - Display this help menu

Github repo: https://github.com/flamefractal/\n

To report a bug or suggest improvements, please contact @vishaaaal, thank you.""")
	else:
		sendMessage(user_id, "Oops! I don't understand that yet!\nType '/help' to see all the commands.")
	
	requests.put(myjsonUrl, headers={'content-type':'application/json', 'data-type':'json'}, data=json.dumps(users))
	# sendMessage(os.environ.get('debugId'), str(response)) -> Inline Keyboard expected, sendMessage by default uses replyMarkup
	requests.get('https://api.telegram.org/bot'+botToken+'/sendMessage?parse_mode=Markdown&chat_id='+debugId+'&text='+str(response))

	return(str(users))


@app.route('/sendMenuAllUsers'+botToken, methods=['GET'])
def sendMenuAllUsers():
	print("time to send full menu")
	for user in users:
		# send only if registered
		if users[user][0] >= 0:
			sendMenu(user, users[user][0])
			print("sent full menu to "+user+", "+users[user][1])
	return("Menu successfully sent.")


@app.route('/')
def root():
	return "<a href='http://t.me/"+botUsername+"'>http://t.me/"+botUsername+"</a>"

@app.route('/<path:path>')
def catch_all(path):
	return "<a href='http://t.me/"+botUsername+"'>http://t.me/"+botUsername+"</a>"


############# Start the flask server!

if __name__ == "__main__":
	#set bot webhook automatically
	print(requests.get('https://api.telegram.org/bot'+botToken+'/setWebhook?url='+appUrl+'/botWebhook'+botToken))
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)