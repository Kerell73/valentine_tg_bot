import requests

def alert_receiver(receiver_id, bot_token):
    message = "✨Тобі прийшла нова валентинка!✨ "
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    keyboard = {
        "inline_keyboard": [[{"text": "Подивитися валентинки 💌", "callback_data": "check_valentines"}]]
    }

    data = {
        "chat_id": receiver_id,
        "text": message,
        "reply_markup": keyboard
    }

    response = requests.post(url, json=data)
    return response.json()