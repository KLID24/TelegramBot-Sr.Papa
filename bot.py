import telebot, firebase_admin, auth

from keys.secrets import TELEGRAM_TOKEN, FIREBASE_URL
from firebase_admin import credentials
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

bot = telebot.TeleBot(TELEGRAM_TOKEN)
orders: list[dict] = []

def fb_update_name(name: str):
    ref = firebase_admin.db.reference("user")
    ref.set({
        "name": name
    })

def is_user_allowed(user_id: int, chat_id: int):
    if not auth.is_user_allowed(user_id):
        bot.send_message(chat_id, "ℹ️ ¡Usted no esta registrado, por favor escriba /login!")
        return False
    return True

@bot.message_handler(commands=['info', 'start', 'help'])
def send_welcome(msg: Message):
    bot.reply_to(msg, "ℹ️ ¡Hola! Soy el bot del café Sr.Papa.\n\nEscribe tu nombre y/o apellido separados por un espacio (por ejemplo: Name: Ivan Petrov o Name: Juan).\n\nTambién puedes simplemente reenviar el mensaje del bot de Tilda.")
    bot.reply_to(msg, 'ℹ️ Los comandos disponibles son: \n\n/start, /info o /help Mostrar este mensaje \n/login Empezar el dialogo de registracion\n/list Mostrar todos los pedidos guardados y elegir el pedido selecionado para el robot')

    is_user_allowed(msg.from_user.id, msg.chat.id)

@bot.message_handler(commands=['login'])
def prompt_password(msg: Message):
    user_id = msg.from_user.id
    bot.send_message(msg.chat.id, "ℹ️ ¡Por favor entre la contraseña!")
    bot.register_next_step_handler(msg, handle_password)

def handle_password(msg: Message):
    user_id = msg.from_user.id
    password = msg.text

    if auth.verify_password(password):
        auth.allow_user(user_id)
        bot.send_message(msg.chat.id, "✅ Contraseña correcta. ¡Bienvenido!")
    else:
        bot.send_message(msg.chat.id, "❌ Contraseña incorrecta. Inténtalo de nuevo.")
        bot.register_next_step_handler(msg, handle_password)  # loop again

@bot.message_handler(commands=['list'])
def send_orders_list(msg: Message):
    if not is_user_allowed(msg.from_user.id, msg.chat.id):
        return

    keyboard = InlineKeyboardMarkup()

    if len(orders):
        for index, order in enumerate(orders):
            name = order["name"]
            button = InlineKeyboardButton(text=name, callback_data=str(index))
            keyboard.add(button)

        bot.send_message(msg.chat.id, "ℹ️ Elige el order:", reply_markup=keyboard)
    else:
        bot.send_message(msg.chat.id, "ℹ️ ¡Aún no hay pedidos! Por favor insértelos")

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call: CallbackQuery):
    index = int(call.data)
    selected_order = orders[index]
    
    # Respond to the user based on the selected option
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f'ℹ️ Informacion sobre el pedido: \n\n{selected_order["details"]}')
   
    fb_update_name(selected_order_name)
    bot.send_message(call.message.chat.id, f'✅ Nombre "{selected_order["name"]}" selecionado')

@bot.message_handler(func=lambda message: True)
def save_name(msg: Message):
    if not is_user_allowed(msg.from_user.id, msg.chat.id):
        return

    new_order = {
        "name": "",
        "details": ""
    }

    # Search for the line with the name
    for line in msg.text.split("\n"):
        if not new_order["name"] and line.startswith("Name:"):
            name = line.replace("Name:", "").strip()
            new_order["name"] = name

            bot.reply_to(msg, f"✅ Nombre guardado: {name}")
            continue

        new_order["details"] += line + "\n"
    
    # If the name is not found
    if not new_order["name"]:
        bot.reply_to(msg, '⚠️ Nombre no encontrado. Asegúrate de que el mensaje contenga una línea como: "Name: Danil"')
        return

    orders.append(new_order)

if __name__ == "__main__":
    # Initializing firebasez
    firebase_admin.initialize_app(
        credentials.Certificate("keys/firebase.json"), 
        {
            "databaseURL": FIREBASE_URL
        }
    )

    bot.polling()