# SNU-Mess-Menu-Notifs

A python-scraper telegram-bot that sends Mess Menu push-notifications right before meal timings!

Start this bot [https://t.me/SNUMessBot](https://t.me/SNUMessBot), sit back and relax!

## ToDo

[] check time and send that time's menu only

[] save users obj to a file

## Program Flow

### Webhook (Telegram Commands) 

![flow1](/imgs/flow1.png)





### Periodic Push Notifications

![flow2](/imgs/flow2.png)

## Screenshots

![screenshot](/imgs/screenshot.png)

## Version history
	5. added telegram commands
	4. ability to subscribe new users to notifications
	3. scheduled thrice a day using heroku scheduler and cron.py
	2. created a telegram bot, and a flask server app, tested sendMessage for one hard-coded user in the script
	1. scraped mess menu using beautifulsoup and templated the message