
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from telegram import ParseMode
import sqlite3

TOKEN = "token"
DB_FILE = "getid.db"

conn = None

# database functions
def initialize_database():
    connection = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                            id integer PRIMARY KEY,
                            user_id integer,
                            username text,
                            firstname text,
                            lastname text,
                            display_username text
                        );""")
    cursor.close()
    return connection


def get_user_by_username(username):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username.lower(), ))
    result = cursor.fetchone()
    cursor.close()
    return result


def get_user_by_id(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id, ))
    result = cursor.fetchone()
    cursor.close()
    return result


def add_user(user_id, username, firstname, lastname):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users(user_id,username,firstname,lastname,display_username) VALUES(?,?,?,?,?)",
                   (user_id, username.lower(), firstname, lastname, username))
    conn.commit()
    cursor.close()


# bot functions
def update_data(update):
    user = update.message.from_user
    result = get_user_by_username(user.username)
    if result is None:
        add_user(user.id, user.username, user.first_name, user.last_name)
        return True

    elif (result[0] == user.id and result[2] == user.first_name and result[3] == user.last_name):
        return False
    else:
        cursor = conn.cursor()
        cursor.execute(""" UPDATE users
                            SET user_id=?,
                                firstname=?,
                                lastname=?,
                                display_username=?
                            WHERE username=?
                        """, (user.id, user.first_name, user.last_name, user.username, user.username.lower()))
        conn.commit()
        cursor.close()
        return True


def start_handler(bot, update):
    update.message.reply_text("Send a username like @username and i might be able to send back the information of that user including their id number\n\
<i>Note: Users might change their usernames so some results might not be true</i>", parse_mode=ParseMode.HTML)
    update_data(update)


def username_handler(bot, update):
    update_data(update)
    text = update.message.text
    if text:
        if text[0] == '@':
            if text.count(' ') == 0:
                result = get_user_by_username(text[1:])
                if result is not None:
                    username = result[5]
                    firstname = result[3]
                    lastname = result[4]
                    user_id = result[1]
                    update.message.reply_text(f"Username: @{username}\nFirst name: <i>{firstname}</i>\nLast name: <i>{lastname}</i>\nID: <code>{user_id}</code>", parse_mode=ParseMode.HTML)
                else:
                    update.message.reply_text(f"Sorry, Username {text} was not found in database")
                return

    update.message.reply_text("Invalid username, please make sure that you send it in @username format")


def me_handler(bot, update):
    update_data(update)
    user = update.message.from_user
    username = user.username
    firstname = user.first_name
    lastname = user.last_name
    user_id = user.id
    update.message.reply_text(f"Username: @{username}\nFirst name: <i>{firstname}</i>\nLast name: <i>{lastname}</i>\nID: <code>{user_id}</code>", parse_mode=ParseMode.HTML)


def not_text_message_handler(bot, update):
    update_data(update)
    update.message.reply_text("Please send the username in text format")


def main():
    global conn

    conn = initialize_database()

    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start_handler))
    dispatcher.add_handler(CommandHandler('me', me_handler))
    dispatcher.add_handler(MessageHandler(Filters.text, username_handler))
    dispatcher.add_handler(MessageHandler(Filters.all, not_text_message_handler))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
