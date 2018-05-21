from flask import Flask, request
import bs4 as bs
import requests
import json
import os
import datetime
import time
import pytz
import threading
app = Flask(__name__)
debug_print_on = True

######################### Global Variables #########################

myjsonUrl = 'https://api.myjson.com/bins/'+str(os.environ.get('myjsonId'))
db = requests.get(myjsonUrl).json()
users = db["users"]
botToken = db["config"]["botToken"]
extrasPhotoId = db["config"]["extrasPhotoId"]
botUsername = db["config"]["botUsername"]
appUrl = db["config"]["appUrl"]
debugId = db["config"]["debugId"]
secretSauce = db["config"]["secretSauce"]
messUrl = db["config"]["messUrl"]

types = {4: "Current Menu", 1: "Breakfast", 2: "Lunch", 3: "Dinner", 5: "Full Menu"}
BLDString = {0:{1:None, 2:None, 3:None, 4:None, 5:None}, 1:{1:None, 2:None, 3:None, 4:None, 5:None}}
inlineResults = {0:[], 1:[]}

replyMarkup = '{"keyboard":[["/dh1_menu","/dh2_menu"],["/dh1_extras","/dh2_extras"],["/dh1_notifs","/dh2_notifs"],["/both_notifs","/deregister"],["/refresh", "/help"]]}'
helpString = """UPDATE: The notifications have been disabled due to vacations. Remind @vishaaaal to turn them back on if you want! \n\n\nHi. This bot will send you notifications with Menu of SNU Mess of your choice - three times a day: 7:30AM, 11:30AM, 7:30PM.\n\n\nYou can also interact with it here or use it inline in any chat/groups by typing "@snumessbot".\n\n\n/dh1\_menu - Get today's DH1 Menu\n/dh2\_menu - Get today's DH2 Menu\n/dh1\_extras - DH1's Ala-Carte, Evening, Drinks menu.\n/dh2\_extras - DH2's Rollu, Evening, Drinks menu.\n/dh1\_notifs - Daily notifications for DH1\n/dh2\_notifs - Daily notifications for DH2\n/both\_notifs - Daily notifications for BOTH\n/deregister - NO daily notifications\n/refresh - Update menu from SNU website\n/help - Display this help menu\n\nGithub repo: https://github.com/FlameFractal/SNU-Mess-Menu-Notifs/\n\n\nTo report a bug, suggest improvements, ask anything - msg @vishaaaal."""

######################### Some important functions #########################

def debug_print(debug_message):
	if debug_print_on==True:
		print(str(debug_message))

def update_db():
	db["users"] = users
	requests.put(myjsonUrl, headers={'content-type':'application/json', 'data-type':'json'}, data=json.dumps(db)) # update users database

def sendMessage(user_id, msg):
	users[user_id]["last_botReply"] = (requests.get('https://api.telegram.org/bot'+botToken+'/sendMessage?parse_mode=Markdown&chat_id='+str(user_id)+'&text='+msg+'&reply_markup='+replyMarkup+'&disable_web_page_preview=TRUE').text).replace('"',"'")
	update_db()
	return users[user_id]["last_botReply"]

def sendPhoto(user_id, photo, caption=''):
	users[user_id]["last_botReply"] = (requests.get('https://api.telegram.org/bot'+botToken+'/sendPhoto?chat_id='+str(user_id)+'&photo='+str(photo)+'&caption='+str(caption)+'&replyMarkup='+replyMarkup).text).replace('"',"'")
	update_db()
	return users[user_id]["last_botReply"]

def answerInlineQuery(user_id, query_id, mess):
	users[user_id]["last_botReply"] = (requests.get('https://api.telegram.org/bot'+botToken+'/answerInlineQuery?inline_query_id='+str(query_id)+'&switch_pm_text=Slow net? Try inside&switch_pm_parameter=help&results='+json.dumps(inlineResults[mess])).text).replace('"',"'")
	update_db()
	return users[user_id]["last_botReply"]

def getDishes(menuItems, mess_choice, t): # here type can only be 1,2,3 .... handle 4,5 seperately
	s = "*DH"+str(mess_choice+1)+" "+types[t]+"*\n----------------\n"
	for dish in menuItems[t].find_all('p'):
		s = s+(dish.text).replace('"','').title().strip()+"\n" # why does dh2 menu always have "toast !!! somebody forgot an extra quote, remove it and other artefacts from dish names
	return s

def fetchMenuItems():
	global inlineResults
	global BLDString
	time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
	datestamp = "*"+time.strftime("%A")+", "+time.strftime("%d")+" "+time.strftime("%B")+" "+str(time.year)+"*\n\n"
	for mess_choice in (0,1): # construct strings for all 10 types of menus
		try:
			menuItems= ((bs.BeautifulSoup(requests.get(messUrl, timeout=1).text,'lxml')).find_all(id='dh2MenuItems'))[mess_choice].find_all('td')
			if('No Menu' in menuItems[0].text.strip()):
				raise requests.exceptions.RequestException("_No Menu Available!_")
			for t in types:
				if t==1 or t==2 or t==3: 
					BLDString[mess_choice][t] = datestamp + getDishes(menuItems, mess_choice, t)
				if t==4: # get according to current time
					if time.hour<=10: #breakfast - midnight to 10:59am      #send entire menu at breakfast
						BLDString[mess_choice][t] = datestamp + getDishes(menuItems, mess_choice,1)+"\n"+getDishes(menuItems, mess_choice,2)+"\n"+getDishes(menuItems, mess_choice,3)
					elif 11<=time.hour<=15: #lunch - 11am to 3:59pm
						BLDString[mess_choice][t] = datestamp + getDishes(menuItems, mess_choice,2)
					else: # dinner - 4pm to midnight
						BLDString[mess_choice][t] = datestamp + getDishes(menuItems, mess_choice,3)
				if t==5:
					BLDString[mess_choice][t] = datestamp + getDishes(menuItems, mess_choice,1)+"\n"+getDishes(menuItems, mess_choice,2)+"\n"+getDishes(menuItems, mess_choice,3)
		except requests.exceptions.RequestException as e:
			for t in types:
				BLDString[mess_choice][t] = datestamp+"*DH"+str(mess_choice+1)+" "+"*\n----------------\n"+"Oops. Error. Verify at "+messUrl+", and to refresh my menu send /refresh.\n\n*ERROR:* _"+str(e)+"_\n"
	
	# construct strings for fast inline response
	counter = 0
	inlineResults = {0:[], 1:[]}
	for mess_choice in (0,1):
		for t in types:
			inlineResults[mess_choice].append({"type":"article","id":str(counter),"title":"DH"+str(mess_choice+1)+" - "+types[t],"input_message_content":{"message_text":BLDString[mess_choice][t], "parse_mode": "Markdown"}})
			counter = counter+1
		inlineResults[mess_choice].append({"type":"photo","id":str(counter),"title":"DH"+str(mess_choice+1)+" - Extras Menu","photo_file_id":str(extrasPhotoId[mess_choice]),"description":"DH"+str(mess_choice+1)+" - Extras Menu","caption":"DH"+str(mess_choice+1)+" - Extras Menu"})
		counter = counter + 1

	# debug_print(str(BLDString)+"\n\n\n"+str(inlineResults))
	return "I'm up to date with SNU website now. Thanks!"

def sendCurrentMenuAllUsers():
	fetchMenuItems()
	for user_id in users:
		if "mess_choice" in users[user_id] and users[user_id]["mess_choice"] >= 0: # send only if registered for notifications
			if users[user_id]["mess_choice"] == 2:
				sendMessage(user_id, BLDString[0][4]+BLDString[1][4])
			else:
				sendMessage(user_id, BLDString[users[user_id]["mess_choice"]][4])
			debug_print("sent notification to "+user_id)
	return('')

def att(attended, conducted, percentage='75'):
	attended = int(attended)
	conducted = int(conducted)
	percentage = int(percentage)
	if not attended>0 or not conducted>0 or not attended<conducted or not 100>=percentage>=0:
		return '/att \[attended] \[conducted] \[req att % eg. 75] (optional)'
	temp = conducted
	temp2 = attended
	# can't miss
	if (attended/conducted < percentage/100):
		while(temp2/temp <= percentage/100):
			temp2 = temp2 + 1
			temp = temp + 1
		s = "You need to attend "+str(temp2-attended)+" more classes for final of %0.2f" %((temp2*100)/(temp))
		return s+"% = "+str(temp2)+"/"+str(temp)
	else: # can miss
	
		while(attended/temp>=percentage/100):
			temp = temp+1
		s = "You can miss "+str(temp-1-conducted)+" more classes for final of %0.2f" %((attended*100)/(temp-1))
		return s +"% = "+str(attended)+"/"+str(temp-1)

def webhook_handler(response):
	try:
		requests.get('https://api.telegram.org/bot'+botToken+'/sendMessage?parse_mode=Markdown&chat_id='+debugId+'&text='+str(response), timeout=1)
	except:
		debug_print('')

	if("inline_query" in response):
		field = "inline_query"
		user_id = str(response[field]["from"]["id"]) # get the user id 
		if user_id == '376483850':
			return 'spam blocked', 200
		query_id = str(response[field]["id"]) # get the query id 
		query_msg = str(response[field]["query"]) # get the message 
		if user_id in users:
			users[user_id]["last_query"] = str(response)
		else:
			users[user_id] = {}
		users[user_id]["last_query"] = str(response)
		users[user_id]["name"] = response[field]["from"]["first_name"] if "first_name" in response[field]["from"] else 'unknown' # get the first name
		if query_msg != '1' and query_msg != '2': # if not typed 1 or 2, show default
			query_msg = users[user_id]["mess_choice"]+1 if "mess_choice" in users[user_id] else "1" # if user hasnt entered query, show him his mess_choice menu !
		return(answerInlineQuery(user_id, query_id, int(query_msg)-1))
	
	if("message" in response):
		field = "message"
	elif("edited_message" in response):
		field = "edited_message"
	else:
		return str(response)

	# extract user information
	user_msg = str(response[field]["text"]) if "text" in response[field] else '' # get the message
	user_id = str(response[field]["from"]["id"]) if "id" in response[field]["from"] else '999' # get the id 
	if user_id == '376483850':
		return 'spam blocked', 200
	if user_id not in users:
		users[user_id] = {}
	users[user_id]["name"] = response[field]["from"]["first_name"] if "first_name" in response[field]["from"] else 'unknown' # get the first name
	users[user_id]["name"] = users[user_id]["name"] + " " + response[field]["chat"]["last_name"] if "last_name" in response[field]["from"] else users[user_id]["name"] # get the last name
	users[user_id]["username"] = response[field]["chat"]["username"]	if "username" in response[field]["chat"] else 'unknown' # get the username
	users[user_id]["last_query"] = str(response)
	if "mess_choice" not in users[user_id]:
		users[user_id]["mess_choice"] = 1

	botReply = ""
	if '/start' in user_msg :
		users[user_id]["mess_choice"] = 1
		botReply = "Hello there! Welcome!\nYour request for notifications has been registered.\nDefault Mess DH-2 selected.\nType '/help' to switch mess!"
	elif user_msg == '/dh1_notifs':
		users[user_id]["mess_choice"] = 0
		botReply = "Your request for notifications has been registered.\nMess DH-1 selected.\nThank you!"
	elif user_msg == '/dh2_notifs':
		users[user_id]["mess_choice"] = 1
		botReply =  "Your request for notifications has been registered.\nMess DH-2 selected.\nThank you!"
	elif user_msg == '/both_notifs':
		users[user_id]["mess_choice"] = 2
		botReply = "Your request for notifications has been registered.\nMess DH-1 and DH-2 selected.\nThank you!"
	elif user_msg == '/deregister':
		users[user_id]["mess_choice"] = -1
		botReply = "Your request for deregistering for notifications has been noted.\nThank you!"
	elif user_msg == '/dh1_menu':
		botReply = BLDString[0][5]
	elif user_msg == '/dh2_menu':
		botReply = BLDString[1][5]
	elif user_msg == '/dh1_extras':
		return(sendPhoto(user_id, extrasPhotoId[0], 'DH1 Extras Menu'))
	elif user_msg == '/dh2_extras':
		return(sendPhoto(user_id, extrasPhotoId[1], 'DH2 Extras Menu'))
	elif user_msg == '/refresh':
		botReply = '*'+str(fetchMenuItems())+'*'
	elif '/att' in user_msg:
		a = user_msg.split(' ')
		botReply = '/att \[attended] \[conducted] \[req att % eg. 75] (optional)' if len(a)<3 else att(a[1],a[2]) if len(a)==3 else att(a[1],a[2],a[3])
	elif '/adhoc_update'+secretSauce in user_msg: # admin function
		time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
		datestamp = "*"+time.strftime("%A")+", "+time.strftime("%d")+" "+time.strftime("%B")+" "+str(time.year)+"*\n\n"
		new_menu = user_msg.replace('/adhoc_update'+secretSauce,'')
		if '/dh1' in new_menu:
			new_menu = "*Menu for DH1*\n\n" + new_menu.replace('/dh1 ','').strip()
			for user_id in users:
				if "mess_choice" in users[user_id] and (users[user_id]["mess_choice"] == 0 or users[user_id]["mess_choice"] == 2):
					sendMessage(user_id, datestamp+new_menu.strip())
		elif '/dh2' in new_menu:
			new_menu = "*Menu for DH2*\n\n" + new_menu.replace('/dh2 ','')
			for user_id in users:
				if "mess_choice" in users[user_id] and (users[user_id]["mess_choice"] == 1 or users[user_id]["mess_choice"] == 2):
					sendMessage(user_id, datestamp+new_menu.strip())
		else:
			sendMessage(user_id,"Oops. Did not understand that.")
		return str(response)
	elif user_msg == '/help':
		botReply = helpString
	else:
		botReply =  "Oops! I don't understand that yet!\nType '/help' to see all the commands."
	sendMessage(user_id, botReply)
	return str(response)

######################### APIs to talk to the bot #########################

@app.route('/botWebhook'+botToken, methods=['POST'])
def fn():
	try:
		debug_print("starting new thread for webhook")
		threading.Thread(target=webhook_handler, args=[request.get_json()]).start()
	except:
		debug_print("coudln't start thread, responsing webhook normally")
		webhook_handler(request.get_json())
	return ' '

@app.route('/fetchMenuItems'+botToken, methods=['GET'])
def fn2():
	try:
		debug_print("starting new thread for fetching menu items")
		threading.Thread(target=fetchMenuItems).start()
	except:
		debug_print("coudln't start thread, fetching menu items normally")
		fetchMenuItems()
	return ' '

@app.route('/sendCurrentMenuAllUsers'+botToken, methods=['GET'])
def fn3():
	try:
		debug_print("started thread for sending notifications")
		threading.Thread(target=sendCurrentMenuAllUsers).start()
	except:
		debug_print("coudln't start thread, sending notifications normally")
		sendCurrentMenuAllUsers()
	return ' '

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
	return "<a href='http://t.me/"+botUsername+"'>http://t.me/"+botUsername+"</a>"

######################### Start the flask server! #########################

debug_print('webhook set - '+str(requests.get('https://api.telegram.org/bot'+botToken+'/setWebhook?url='+appUrl+'/botWebhook'+botToken))) #set bot webhook automatically
fetchMenuItems()

if __name__ == "__main__":
	app.run(threaded=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))