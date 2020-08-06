
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from telegram import ParseMode
import mysql.connector

TOKEN = "token"

db = mysql.connector.connect(
    host="localhost",
    user="user",
    password="password",
    database="getidbot"
)


def start_handler(bot, update):
    update.message.reply_text("Hello, send a username like @username and i might be able to send back the information of that user including their id number")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (str(update.message.from_user.id), ))
    if len(cursor.fetchall()) == 0:
        cursor.execute("INSERT INTO users (user_id, username) VALUES (%s, %s)", (update.message.from_user.id, update.message.from_user.username))
    db.commit()
    cursor.close()


def username_handler(bot, update):
    text = update.message.text
    if text:
        if text[0] == '@':
            if text.count(' ') == 0:
                cursor = db.cursor()
                cursor.execute("SELECT * FROM users WHERE username = %s", (text[1:], ))
                result = cursor.fetchone()
                print(text)
                print(result)
                if result is not None:
                    username = result[1]
                    firstname = ''
                    lastname = ''
                    user_id = result[0]
                    update.message.reply_text(f"Username: @{username}\nFirst name: <i>{firstname}</i>\nLast name: <i>{lastname}</i>\nID: <code>{user_id}</code>", parse_mode=ParseMode.HTML)
                else:
                    update.message.reply_text(f"Sorry, Username {text} was not found in database")
                cursor.close()
                return
    update.message.reply_text("Invalid username, please make sure that you send it in @username format")


def not_text_message_handler(bot, update):
    update.message.reply_text("Please send the username in text format")


def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start_handler))
    dispatcher.add_handler(MessageHandler(Filters.text, username_handler))
    dispatcher.add_handler(MessageHandler(Filters.all, not_text_message_handler))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
