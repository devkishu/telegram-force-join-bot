import os
import json
from telegram import (
    Bot,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

# ============================================
# CONFIG
# ============================================
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")   # <--- REPLACE THIS WITH YOUR TOKEN
MAIN_ADMIN = 5341105960                 # <--- YOUR USER ID

# REQUIRED CHANNELS
REQUIRED_CHANNELS = [
    {"chat_id": "@newyonoapp", "url": "https://t.me/newyonoapp"},
    {"chat_id": "@AllYonoGiftsCode", "url": "https://t.me/AllYonoGiftsCode"},
    {"chat_id": "-1001722438750", "url": "https://t.me/+wYSxj-rmh6syNmY9"},
    {"chat_id": "-1002202294458", "url": "https://t.me/+ZmOA3GiM80FiY2Y1"},
]

# ============================================
# JSON HELPERS
# ============================================

def load_json(filename, default):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump(default, f)
    with open(filename, "r") as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

users = load_json("users.json", [])
admins = load_json("admins.json", [MAIN_ADMIN])

pending_admin_action = {}

# ============================================
# CHECK CHANNEL MEMBERSHIP
# ============================================

def check_user_in_channel(bot, user_id, chat_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ("member", "creator", "administrator")
    except:
        return False

# ============================================
# JOIN KEYBOARD
# ============================================

def build_join_keyboard():
    rows = []
    row = []
    for i, ch in enumerate(REQUIRED_CHANNELS, 1):
        row.append(InlineKeyboardButton("Join Now", url=ch["url"]))
        if i % 2 == 0:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("Verify", callback_data="verify")])
    return InlineKeyboardMarkup(rows)

# ============================================
# CONSTANT MESSAGES
# ============================================

WELCOME_TEXT = (
    "<b>Welcome To Our Instant Money Bot! 🤑🔥</b>\n\n"
    "<b>Channel Join Karke >> Apna Amount Claim Karo Payment Instant Coming ! 🚀</b>"
)

CASHBACK_MESSAGE = (
    "<b>You have joined all channels!</b>\n\n"
    "<b>You can now claim your cashback!! 🎉</b>\n\n"
    "<b>Go to https://qrco.de/bg6qJW & CLAIM your cashback now !! 🔥🔥</b>"
)

NEW_USER_TEMPLATE = (
    "🔥 NEW JOINED USER 🔥\n"
    "Name: {name}\n"
    "Username: @{username}\n"
    "ID: {user_id}\n"
    "Total Users: {total}"
)

# ============================================
# ADMIN PANEL KEYBOARD
# ============================================

def admin_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Total Users", callback_data="admin_total")],
        [InlineKeyboardButton("➕ Add Admin", callback_data="admin_add")],
        [InlineKeyboardButton("➖ Remove Admin", callback_data="admin_remove")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("👑 List Admins", callback_data="admin_list")],
        [InlineKeyboardButton("🔄 Refresh", callback_data="admin_panel")],
    ])

# ============================================
# /start Handler
# ============================================

def start(update: Update, context: CallbackContext):
    bot = context.bot
    user = update.effective_user
    chat_id = update.effective_chat.id
    user_id = user.id

    # Add new user to DB
    if user_id not in users:
        users.append(user_id)
        save_json("users.json", users)

        msg = NEW_USER_TEMPLATE.format(
            name=user.full_name,
            username=user.username or "No_Username",
            user_id=user_id,
            total=len(users),
        )

        for admin in admins:
            bot.send_message(admin, msg)

    bot.send_message(
        chat_id,
        WELCOME_TEXT,
        reply_markup=build_join_keyboard(),
        parse_mode="HTML"
    )

    # Already joined?
    missing = [c for c in REQUIRED_CHANNELS if not check_user_in_channel(bot, user_id, c["chat_id"])]
    if not missing:
        bot.send_message(chat_id, CASHBACK_MESSAGE, parse_mode="HTML")

# ============================================
# VERIFY BUTTON HANDLER
# ============================================

def verify(update: Update, context: CallbackContext):
    query = update.callback_query
    bot = context.bot
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    missing = [c for c in REQUIRED_CHANNELS if not check_user_in_channel(bot, user_id, c["chat_id"])]

    if missing:
        query.answer("❌ Please join all required channels first!", show_alert=True)
        return

    # Verified
    bot.send_message(chat_id, CASHBACK_MESSAGE, parse_mode="HTML")
    query.answer()

# ============================================
# /admin command
# ============================================

def admin_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in admins:
        return update.message.reply_text("⛔ You are not an admin.")
    update.message.reply_text("👑 <b>ADMIN PANEL</b>", parse_mode="HTML", reply_markup=admin_keyboard())

# ============================================
# ADMIN CALLBACKS
# ============================================

def admin_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    bot = context.bot
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    data = query.data

    if user_id not in admins:
        return query.answer("⛔ You are not an admin!", show_alert=True)

    if data == "admin_panel":
        query.edit_message_text("👑 <b>ADMIN PANEL</b>", parse_mode="HTML", reply_markup=admin_keyboard())

    elif data == "admin_total":
        query.edit_message_text(
            f"<b>Total Users:</b> {len(users)}",
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )

    elif data == "admin_list":
        txt = "<b>ADMINS:</b>\n" + "\n".join(str(a) for a in admins)
        query.edit_message_text(txt, parse_mode="HTML", reply_markup=admin_keyboard())

    elif data == "admin_add":
        pending_admin_action[user_id] = "add"
        bot.send_message(chat_id, "Send user ID to ADD:")
        query.answer()

    elif data == "admin_remove":
        pending_admin_action[user_id] = "remove"
        bot.send_message(chat_id, "Send user ID to REMOVE:")
        query.answer()

    elif data == "admin_broadcast":
        pending_admin_action[user_id] = "broadcast"
        bot.send_message(chat_id, "Send the message/photo/video/document you want to broadcast:")
        query.answer()

# ============================================
# ADMIN TEXT / MEDIA HANDLING
# ============================================

def admin_text_handler(update: Update, context: CallbackContext):
    bot = context.bot
    msg = update.message
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if user_id not in pending_admin_action:
        return

    action = pending_admin_action[user_id]

    # Add admin
    if action == "add":
        try:
            new_admin = int(msg.text)
            if new_admin not in admins:
                admins.append(new_admin)
                save_json("admins.json", admins)
                bot.send_message(chat_id, f"✅ {new_admin} added as admin.")
            else:
                bot.send_message(chat_id, "Already admin.")
        except:
            bot.send_message(chat_id, "Invalid ID.")
        del pending_admin_action[user_id]

    # Remove admin
    elif action == "remove":
        try:
            rem = int(msg.text)
            if rem == MAIN_ADMIN:
                bot.send_message(chat_id, "❌ Cannot remove main admin!")
            elif rem in admins:
                admins.remove(rem)
                save_json("admins.json", admins)
                bot.send_message(chat_id, f"❌ {rem} removed.")
            else:
                bot.send_message(chat_id, "Not an admin.")
        except:
            bot.send_message(chat_id, "Invalid ID.")
        del pending_admin_action[user_id]

    # BROADCAST (supports all media types)
    elif action == "broadcast":
        count = 0

        for uid in users:
            try:
                if msg.photo:
                    bot.send_photo(uid, msg.photo[-1].file_id, caption=msg.caption or "")
                elif msg.video:
                    bot.send_video(uid, msg.video.file_id, caption=msg.caption or "")
                elif msg.document:
                    bot.send_document(uid, msg.document.file_id, caption=msg.caption or "")
                elif msg.audio:
                    bot.send_audio(uid, msg.audio.file_id, caption=msg.caption or "")
                elif msg.text:
                    bot.send_message(uid, msg.text)
                count += 1
            except:
                pass

        bot.send_message(chat_id, f"📢 Broadcast sent to {count} users!")
        del pending_admin_action[user_id]

# ============================================
# MAIN
# ============================================

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("admin", admin_command))
    dp.add_handler(CallbackQueryHandler(verify, pattern="verify"))
    dp.add_handler(CallbackQueryHandler(admin_callback, pattern="admin_.*"))
    dp.add_handler(MessageHandler(Filters.private, admin_text_handler))

    print("Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
