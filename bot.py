import telebot, firebase_admin

from keys.secrets import TELEGRAM_TOKEN, FIREBASE_URL
from firebase_admin import db, credentials
from telebot import types

bot = telebot.TeleBot(TELEGRAM_TOKEN)
Orders: list[dict] = []

@bot.message_handler(commands=['info', 'start'])
def send_welcome(msg):
    bot.reply_to(msg,         
"""
¡Hola! Soy el bot del café Sr.Papa.
            
Escribe tu nombre y/o apellido separados por un espacio (por ejemplo: Name: Ivan Petrov o Name: Juan).
            
También puedes simplemente reenviar el mensaje del bot de Tilda.
""")

@bot.message_handler(commands=['list'])
def send_orders_list(msg):
    keyboard = types.InlineKeyboardMarkup()

    for index, order in enumerate(Orders):
        name = order["name"]
        button = types.InlineKeyboardButton(text=name, callback_data=str(index))
        keyboard.add(button)

    bot.send_message(msg.chat.id, "Elige el order:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    # Get the data from the button pressed
    selected_order = Orders[int(call.data)]
    selected_order_details = selected_order["details"]
    
    # Respond to the user based on the selected option
    bot.answer_callback_query(call.id)  # Acknowledge the button press
    bot.send_message(call.message.chat.id, f"Informacion sobre el pedido: {selected_order_details}")

@bot.message_handler(func=lambda message: True)
def save_name(msg):
    text = msg.text
    is_name_saved = False

    order = {
        "name": "",
        "details": ""
    }

    # Search for the line with the name
    for line in text.split("\n"):
        if line.startswith("Name:") and not is_name_saved:
            name = line.split("Name:")[1].strip()
            order["name"] = name

            # ref = db.reference("user")
            # ref.set({
            #     "name": name
            # })
            
            bot.reply_to(msg, f"✅ Nombre guardado: {name}")
            is_saved = True
        else:
            order["details"] += line + "\n"
    
    # If the name is not found
    if is_name_saved:
        bot.reply_to(msg, '⚠️ Nombre no encontrado. Asegúrate de que el mensaje contenga una línea como: "Name: Danil"')
    else:
        Orders.append(order)

if __name__ == "__main__":
    firebase_admin.initialize_app(
        credentials.Certificate("keys/firebase.json"), 
        {
            'databaseURL': FIREBASE_URL
        }
    )

    bot.polling()