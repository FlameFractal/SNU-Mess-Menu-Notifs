from flask import Flask, request
import bs4 as bs
import requests
import json
import os
import datetime
app = Flask(__name__)
debug_print_on = True

######################### Global Variables #########################

botToken = str(os.environ.get('botToken'))
myjsonId = str(os.environ.get('myjsonId'))
botUsername = str(os.environ.get('botUsername'))
appUrl = str(os.environ.get('appUrl'))
debugId = str(os.environ.get('debugId'))
secretSauce = str(os.environ.get('secretSauce'))
myjsonUrl = 'https://api.myjson.com/bins/'+myjsonId;
messUrl = 'http://messmenu.snu.in/messMenu.php/'
replyMarkup = '{"keyboard":[["/dh1_menu", "/dh2_menu"],["/dh1_notifs", "/dh2_notifs"],["/both_notifs", "/deregister"],["/dh2_extras", "/help"]]}'
users = requests.get(myjsonUrl).json() # { user_id:{mess_choice: (-1:deregister, 0:DH1, 1:DH2), name:, username} }

######################### Some important functions #########################

def debug_print(debug_message):
	if debug_print_on==True:
		print(debug_message)

def sendMessage(user_id, msg):
	requests.get('https://api.telegram.org/bot'+botToken+'/sendMessage?parse_mode=Markdown&chat_id='+str(user_id)+'&text='+msg+'&reply_markup='+replyMarkup+'&disable_web_page_preview=TRUE')

def sendPhoto(user_id, photo, caption=''):
	requests.get('https://api.telegram.org/bot'+botToken+'/sendPhoto?chat_id='+str(user_id)+'&photo='+str(photo)+'&caption='+str(caption)+'&replyMarkup='+replyMarkup)

def fetchMenuItems(mess_choice):
	try:
		menuItems = ((bs.BeautifulSoup(requests.get(messUrl, timeout=1).text,'lxml')).find_all(id='dh2MenuItems'))[mess_choice].find_all('td')
		if('No Menu' in menuItems[0].text.strip()):
			error = "_No Menu Available!_"
			flag = False
		else:
			error = ""
			flag = True
	except requests.exceptions.RequestException as e:
		menuItems = ""
		error = str(e)
		flag = False
	return flag, error, menuItems

def getBLDString(mess_choice, bld): #bld can be 1-Breakfast, 2-Lunch, 3-Dinner, 4-Current, 5-Full
	flag, error, menuItems = fetchMenuItems(mess_choice)
	if (flag==False):
		BLDString = "Encountered connection error while fetching this item. Please verify at "+messUrl+".\n\n_"+error+"_\n"
	else: # got the menu from the website
		BLDString = "*DH"+str(mess_choice+1)
		t = datetime.datetime.now()
		datestamp = "*"+t.strftime("%A")+", "+t.strftime("%C")+" "+t.strftime("%B")+" "+str(t.year)+"*\n\n"
		
		if bld==1: 
			BLDString = BLDString+" "+"Breakfast*\n----------------\n"
		elif bld==2:
			BLDString = BLDString+" "+"Lunch*\n----------------\n"
		elif bld==3:
			BLDString = BLDString+" "+"Dinner*\n----------------\n"
		if bld==4: # get according to current time
			t = datetime.datetime.now()
			if t.hour<5: #send entire menu at breakfast
				return datestamp+getBLDString(mess_choice,1) + "\n\n" + getBLDString(mess_choice,2) + "\n\n" + getBLDString(mess_choice,3)
			elif 5<=t.hour<=12:
				return datestamp+getBLDString(mess_choice,2)
			else:
				return datestamp+getBLDString(mess_choice,3)
		if bld==5:
			return datestamp+getBLDString(mess_choice,1) + "\n\n" + getBLDString(mess_choice,2) + "\n\n" + getBLDString(mess_choice,3)
		
		for dish in menuItems[bld].find_all('p'):
			BLDString = BLDString+dish.text+"\n"

	return BLDString

def sendFullMenu(user_id, mess):
	sendMessage(user_id, getBLDString(mess, 5))

def sendCurrentMenuAllUsers():
	for user_id in users:
		if users[user_id]["mess_choice"] >= 0: # send only if want notifications
			sendMessage(user_id, getBLDString(users[user_id]["mess_choice"], 4))
			debug_print("sent full menu to "+user_id+", "+users[user]["name"])

######################### APIs to talk to the bot #########################

@app.route('/botWebhook'+botToken, methods=['POST'])
def webhook_handler():
	user_msg = ''
	response = request.get_json()
	requests.get('https://api.telegram.org/bot'+botToken+'/sendMessage?parse_mode=Markdown&chat_id='+debugId+'&text='+str(response))
	
	if("channel_post" in response):
		return ''
		
	field = "message" if ("message" in response) else "edited_message" # check if new message or edited message
	user_id = str(response[field]["chat"]["id"]) # get the id 
	users[user_id]["name"] = response[field]["chat"]["first_name"] # get the first name
	if "last_name" in response[field]["chat"]: # get the last name
		users[user_id]["name"] = users[user_id]["name"] + " " + response[field]["chat"]["last_name"]
	if "username" in response[field]["chat"]: # get the username
		users[user_id]["username"] = response[field]["chat"]["username"]
	if "text" in response[field]: 
		user_msg = str(response[field]["text"])

	if user_msg == '/start':
		sendMessage(user_id, "Hello there! Welcome!")
		sendMessage(user_id, "Your request for notifications has been registered.\nDefault Mess DH-2 selected.\nType '/help' to switch mess!")
		users[user_id]["mess_choice"] = 1
	elif user_msg == '/dh1_notifs':
		users[user_id]["mess_choice"] = 0
		sendMessage(user_id, "Your request for notifications has been registered.\nMess DH-1 selected.\nThank you!")
	elif user_msg == '/dh2_notifs':
		users[user_id]["mess_choice"] = 1
		sendMessage(user_id, "Your request for notifications has been registered.\nMess DH-2 selected.\nThank you!")
	elif user_msg == '/both_notifs':
		users[user_id]["mess_choice"] = 2
		sendMessage(user_id, "Your request for notifications has been registered.\nMess DH-1 and DH-2 selected.\nThank you!")
	elif user_msg == '/deregister':
		users[user_id]["mess_choice"] = -1
		sendMessage(user_id, "Your request for deregistering for notifications has been noted.\nThank you!")
	elif user_msg == '/dh1_menu':
		sendFullMenu(user_id, 0)
	elif user_msg == '/dh2_menu':
		sendFullMenu(user_id, 1)
	elif user_msg == '/dh2_extras':
		sendPhoto(user_id, 'AgADBQAD2qcxG0eK2VfpzkXxLhHWRaQYzDIABHPxFna3WsVEDKgDAAEC', 'DH2 extras menu')
	elif '/adhoc_update'+secretSauce in user_msg: # admin function
		new_menu = user_msg.replace('/adhoc_update'+secretSauce,'')
		if '/dh1' in new_menu:
			new_menu = new_menu.replace('/dh1 ','')
			new_menu = "*Menu for DH1*\n\n"+new_menu
			for user in users:
				if users[user]["mess_choice"] == 0 or users[user]["mess_choice"] == 2:
					sendMessage(user, new_menu.strip())
		elif '/dh2' in new_menu:
			new_menu = new_menu.replace('/dh2 ','')
			new_menu = "*Menu for DH2*\n\n"+new_menu
			for user in users:
				if users[user]["mess_choice"] == 1 or users[user]["mess_choice"] == 2:
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

Github repo: https://github.com/FlameFractal/SNU-Mess-Menu-Notifs/\n

To report a bug or suggest improvements, please contact @vishaaaal, thank you.""")
	else:
		sendMessage(user_id, "Oops! I don't understand that yet!\nType '/help' to see all the commands.")
	requests.put(myjsonUrl, headers={'content-type':'application/json', 'data-type':'json'}, data=json.dumps(users)) # update users database
	return str(response)

@app.route('/sendCurrentMenuAllUsers'+botToken, methods=['GET'])
def fn():
	sendCurrentMenuAllUsers()
	return 'sent menu to all users'

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
	return "<a href='http://t.me/"+botUsername+"'>http://t.me/"+botUsername+"</a>"

######################### Start the flask server! #########################

if __name__ == "__main__":
	debug_print(users)
	debug_print(requests.get('https://api.telegram.org/bot'+botToken+'/setWebhook?url='+appUrl+'/botWebhook'+botToken)) #set bot webhook automatically
	app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)