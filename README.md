# SNU-Mess-Menu-Notifs

A telegram-bot that sends Mess Menu push-notifications right before meal timings! Start this bot [https://t.me/SNUMessBot](https://t.me/SNUMessBot), sit back and relax!

<br><br>

## Screenshots

![screenshot](/imgs/screenshot.png)

<br><br>

## Version history

	17. manual refresh command, threading, attendance
	16. performance improvement
	15. support inline mode!
	14. reduce LOC by 20%
	13. dining hall 2 - extra items picture
	12. improved db
	11. manual menu-update notification by admin
	10. Handle connection errors to snu mess website. 
	9. subscribe to both mess and de-register from notifications. add help menu.
	8. handle 'no menu available', use env vars, post debug msgs to private telegram channel
	7. save and retrieve 'users', incase of restart/crash
	6. send menu based on time of B/L/D
	5. added telegram commands
	4. ability to subscribe new users to notifications
	3. scheduled thrice a day using heroku scheduler and cron.py
	2. created a telegram bot, and a flask server app, tested sendMessage for one hard-coded user in the script
	1. scraped mess menu using beautifulsoup and templated the message

<br><br>

## Functions

![](/imgs/functions.PNG)

<br><br>

## Program Flow

#### Webhook (Telegram Commands)

![flow1](/imgs/flow1.png)

#### Periodic Push Notifications

![flow2](/imgs/flow2.png)

<br><br>
