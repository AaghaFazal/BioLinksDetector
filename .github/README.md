# 🧬 Bio Link Detector

## Bio Link Detector is a smart Telegram bot that keeps group chats clean by removing users with unauthorized links in their bios. It includes admin controls, whitelisting, and logging


<details>
  <summary>✨ FEATURES</summary>
  <br>


✅ **Auto Bio Link Detection**  
Automatically deletes messages from users whose bios contain links.

🔧 **Admin Controls**  
Enable or disable detection, manage whitelisted users, and refresh the admin list.

💬 **Whitelisting**  
Allow trusted users to bypass detection and filtering checks.

🎁 **Bonus Mode**  
New users can send up to 2 messages before any restriction is applied.

📊 **Stats & Speed Tests**  
View bot uptime, memory usage, and perform internet speed tests.

📝 **Logging System**  
Optionally log new user activity (toggleable by bot admins).

📢 **Broadcast System**  
Bot admins can send or forward a message to all users at once, excluding groups.

</details>

---


<details>
  <summary>🛠️ COMMANDS</summary>
  <br>

**General Commands:**  
- `/biolink` – Enable or disable bio link detection.
- `/allow` — Whitelist a user (reply or use username)  
- `/remove` — Remove a user from the whitelist  
- `/list` — Show all whitelisted users  
- `/refresh` – Re-fetches admin list and updates database.  
- `/stats` — Show bot performance and resource usage  
- `/privacy` — Display privacy policy  

🔒 **Bot Admin-Only Commands:**  
- `/broadcast` — Send or forward a message to all users  
- `/stop` — Stop an ongoing broadcast  
- `/logs` — Enable or disable user logging  
- `/speedtest` — Run an internet speed test  

</details>

---   


## 🚀 ONE-CLICK DEPLOY

Deploy the bot to Heroku with a single click:



[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://dashboard.heroku.com/new?template=https://github.com/AaghaFazal/BioLinksDetector)


## 💻 Local Hosting or VPS Deployment Guide 🗄️

A simple guide to deploy this project on a local machine or VPS using Ubuntu 20.04 or 22.04.

---

## 📋 Prerequisites

- Ubuntu 20.04 or 22.04
- Python 3 installed
- A basic understanding of the terminal

---

## 🚀 Deployment Steps

<details>
  <summary>🛠️ Ubuntu 20.04/22.04</summary>
  <br>

1.  🔄 Upgrade and Update the System
```bash
sudo apt-get update && sudo apt-get upgrade -y
```

2. 🧰 Install Required Packages
```bash
sudo apt-get install python3 python3-pip git screen nano -y
```

3. 📥 Clone the Repository
```bash
git clone https://github.com/AaghaFazal/BioLinksDetector && cd BioLinksDetector
```

4. 📦 Install Python Dependencies
```bash
pip3 install -r requirements.txt
```

5. 🛠️ Configure Environment Variables
```bash
nano config.env
```

6. ▶️ Run the Bot in a `screen` Session (Keeps it Running in Background)
```bash
screen -R bot
```

7. ▶️ Run the Application
```bash
python3 bot.py
```

8. Detach screen (so the app keeps running)
```bash
CTRL + A then D
```

</details>

<details>
  <summary>📚 Libraries</summary>
  <br>

<ul>
  <li>Pyrogram</li>
  <li>MongoDB</li>
  <li>Speedtest CLI</li>
  <li>Python <code>asyncio</code></li>
</ul>

</details>


<a href="https://biolinksdetector.github.io/Bot" target="_blank" style="display: inline-block; margin: 20px 0; text-decoration: none; color: inherit;">
  We respect your privacy.<br>
  <img src="https://biolinksdetector.github.io/Bot/src/privacy_policy.png" alt="Privacy Policy" style="height: 40px; border-radius: 8px; cursor: pointer;">
</a>


### Note
### The bot must have <b>"Delete Messages"</b> admin permission in the group to work properly.
