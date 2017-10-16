# SNU-Mess-Menu-Notifs

A python-scraper telegram-bot that sends Mess Menu push-notifications right before meal timings!

<br>

Start this bot [https://t.me/SNUMessBot](https://t.me/SNUMessBot), sit back and relax!

<br><br>

## Program Flow

#### Webhook (Telegram Commands)

![flow1](/imgs/flow1.png)

#### Periodic Push Notifications

![flow2](/imgs/flow2.png)

<br><br>

## Screenshots

![screenshot](/imgs/screenshot.png)

<br><br>

## Version history

	8. handle 'no menu available', use env vars, post debug msgs to private telegram channel
	7. save and retrieve 'users', incase of restart/crash
	6. send menu based on time of B/L/D
	5. added telegram commands
	4. ability to subscribe new users to notifications
	3. scheduled thrice a day using heroku scheduler and cron.py
	2. created a telegram bot, and a flask server app, tested sendMessage for one hard-coded user in the script
	1. scraped mess menu using beautifulsoup and templated the message