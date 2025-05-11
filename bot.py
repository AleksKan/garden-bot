from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from db import init_db, add_vegetable, get_vegetables
from config import TOKEN, ADMIN_ID

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать! Напишите /menu, чтобы увидеть доступные овощи.")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vegs = get_vegetables()
    keyboard = [[InlineKeyboardButton(f"{name} ({quantity}) - {price}₴", callback_data=str(id_))] for id_, name, quantity, price in vegs]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите овощ:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    veg_id = int(query.data)
    user_data[query.from_user.id] = {"veg_id": veg_id}
    await query.edit_message_text("Введите нужное количество (например: 300 грамм):")

async def handle_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    if uid in user_data and "veg_id" in user_data[uid] and "quantity" not in user_data[uid]:
        user_data[uid]["quantity"] = update.message.text
        await update.message.reply_text("Введите адрес доставки (улица и дом):")
    elif uid in user_data and "quantity" in user_data[uid]:
        user_data[uid]["address"] = update.message.text
        vegs = get_vegetables()
        veg_id = user_data[uid]["veg_id"]
        veg = next((v for v in vegs if v[0] == veg_id), None)
        if veg:
            msg = (
                f"🛒 Новый заказ:\n"
                f"Овощ: {veg[1]}\n"
                f"Кол-во: {user_data[uid]['quantity']}\n"
                f"Адрес: {user_data[uid]['address']}\n"
                f"От: @{update.message.from_user.username or update.message.from_user.first_name}"
            )
            await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
            await update.message.reply_text("Спасибо! Ваш заказ отправлен.")
            user_data.pop(uid)

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("Нет доступа.")
        return
    try:
        name, quantity, price = ' '.join(context.args).split(',')
        add_vegetable(name.strip(), quantity.strip(), float(price.strip()))
        await update.message.reply_text("Овощ добавлен.")
    except:
        await update.message.reply_text("Ошибка! Используйте формат: /add Название, количество, цена")

def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("add", add))  # пример: /add Морковь, 5 кг, 120
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quantity))

    app.run_polling()

if __name__ == "__main__":
    main()
