from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from db import init_db, add_user, save_valentine, get_user_valentines, find_users_by_name, find_users_by_username, get_user_by_id
from alerts import alert_receiver

TOKEN = "TOKEN"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    existing_user = get_user_by_id(user.id)

    if existing_user:
        keyboard = [
            [InlineKeyboardButton("Перевірити валентинки 📫", callback_data='check_valentines')],
            [InlineKeyboardButton("Відправити валентинку 💌", callback_data='send_valentine')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Привіт! Ти вже є в базі 🫵🥸 Ось список доступних дій 💘",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text("Привіт 🙋🏿‍♂️ Давай зареєструємось. Напиши своє ім'я:")
        context.user_data['step'] = 'get_first_name'


async def check_valentines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    valentines = get_user_valentines(user_id)

    if valentines:
        response = "\n\n".join(
            [f"Від: {'Анонімно' if v[2] else v[1]}\nТекст: {v[0]}" for v in valentines]
        )

        await update.callback_query.answer()
        await update.callback_query.edit_message_text(f"Твої валентинки 📫\n\n{response}")
    else:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Поки що тут пусто 🤷🏿‍♂️")

    keyboard = [
        [InlineKeyboardButton("Перевірити валентинки 📫", callback_data='check_valentines')],
        [InlineKeyboardButton("Відправити валентинку 💌", callback_data='send_valentine')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text("Ось список доступних дій:", reply_markup=reply_markup)


async def send_valentine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    keyboard = [
        [InlineKeyboardButton("Так", callback_data='anonymous_yes')],
        [InlineKeyboardButton("Ні", callback_data='anonymous_no')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        "Надіслати валентинку анонімно? 🥷🏿",
        reply_markup=reply_markup
    )


async def set_anonymous(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['is_anonymous'] = query.data == 'anonymous_yes'
    await query.edit_message_text("Щоб надіслати валентинку, напиши ім'я та прізвище отримувача або його @username 🫂")
    context.user_data['step'] = 'get_receiver'


async def collect_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get('step')

    if step == 'get_first_name':
        context.user_data['first_name'] = update.message.text
        await update.message.reply_text("Напиши своє прізвище:")
        context.user_data['step'] = 'get_last_name'

    elif step == 'get_last_name':
        context.user_data['last_name'] = update.message.text
        user = update.effective_user
        add_user(user.id, user.username, context.user_data['first_name'], context.user_data['last_name'])

        keyboard = [
            [InlineKeyboardButton("Перевірити валентинки 📫", callback_data='check_valentines')],
            [InlineKeyboardButton("Відправити валентинку 💌", callback_data='send_valentine')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Привіт! Ти вже є в базі 🫵🥸 Ось список доступних дій 💘",
            reply_markup=reply_markup
        )
        context.user_data.clear()

    elif step == 'get_receiver':
        receiver_query = update.message.text.strip()

        # Перевірка на пошук по юзернейму
        if receiver_query.startswith('@'):
            username = receiver_query[1:]  # Видаляємо символ '@'
            possible_receivers = find_users_by_username(username)
        else:
            possible_receivers = find_users_by_name(receiver_query)

        if possible_receivers:
            keyboard = [
                [InlineKeyboardButton(user[1], callback_data=f"select_receiver_{user[0]}")]
                for user in possible_receivers
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Обери одержувача зі списку 👇", reply_markup=reply_markup)
        else:
            await update.message.reply_text(
                "Не знайдено користувачів, які відповідають твоєму запиту 😭 Спробуй ще раз..."
            )

    elif step == 'get_valentine_text':
        valentine_text = update.message.text.strip()

        sender_id = update.effective_user.id
        receiver_id = context.user_data.get('receiver_id')
        is_anonymous = context.user_data.get('is_anonymous', False)

        if receiver_id:
            save_valentine(sender_id, receiver_id, valentine_text, is_anonymous=is_anonymous)

            keyboard = [
                [InlineKeyboardButton("Подивитись валентинки 📫", callback_data='check_valentines')],
                [InlineKeyboardButton("Відправити ще одну валентинку 💌", callback_data='send_valentine')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "Валентинка успішно відправлена!",
                reply_markup=reply_markup
            )

            await alert_receiver(receiver_id, TOKEN)
        else:
            await update.message.reply_text("Сталася помилка. Спробуйте ще раз.")

        context.user_data.clear()

async def select_receiver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    receiver_id = int(query.data.split('_')[-1])
    context.user_data['receiver_id'] = receiver_id
    await query.edit_message_text("Напиши текст валентинки ✍️💋")
    context.user_data['step'] = 'get_valentine_text'

def main():
    init_db()
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_user_data))
    application.add_handler(CallbackQueryHandler(check_valentines, pattern='^check_valentines$'))
    application.add_handler(CallbackQueryHandler(send_valentine, pattern='^send_valentine$'))
    application.add_handler(CallbackQueryHandler(set_anonymous, pattern='^anonymous_(yes|no)$'))
    application.add_handler(CallbackQueryHandler(select_receiver, pattern='^select_receiver_\\d+$'))

    application.run_polling()

if __name__ == "__main__":
    main()