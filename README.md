# Telegram-Direct-Bot
The bot can receive messages from other users who have a spamblock
***
## Functions
* **Bot can takes ``images`` and ``text``**
* **Admin can give ban and unban by ``ID``**
* **Admin can reply to ``incoming messages``**
* **ID of banned users are stored in a ``banned_users.json``**
* **When user writes to the bot, admin receives ``information`` about the user in addition to the user's message**
  ```
        f"Time: {time1}\n\n"
        f"Username: @{message.from_user.username}\n\n"
        f"ID: {message.from_user.id}\n"
        f"Message:\n{message.text}"
  ```
  **``Time`` - the time when the message was sent**  
  **``Username`` - senders username**  
  **``ID`` - senders ID**  
  **``Message`` - message that came from the sender**

***

## Commands
* **``/ping`` - pings the bot**
* **`/me` - your information. for example: ``language in app``, `ID`, `username`, `first name` and `last name`**

***

## Security
* **only ``ADMIN_ID`` view messages, also can give ban and unban**
* **every action is logged and transmitted to `ADMIN_ID`. For example: using commands**

***

## Using
1. **Set your `_TOKEN_` and `_ADMIN_ID_` in the script**
2. **Run the bot:**
```shell
   python direct_bot.py
```
3. **``Enjoy``**
  
