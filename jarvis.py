import telebot
import requests
import os
import time
from gradio_client import Client, file

API_TOKEN = '7429787753:AAGw3qj4MIFASXryKogE9Zc_x3-mnMmIXHY'
bot = telebot.TeleBot(API_TOKEN)
client = Client("KingNish/JARVIS")

def download_file(url, local_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(local_path, 'wb') as f:
            f.write(response.content)
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return False

def predict_voice(voice_file_path):
    try:
        result = client.predict(
            audio=file(voice_file_path),
            model="Mixtral 8x7B",
            seed=0,
            api_name="/predict"
        )
        return result
    except Exception as e:
        print(f"Error predicting voice: {e}")
        return None

def predict_text(text):
    try:
        result = client.predict(
            text=text,
            model="Mixtral 8x7B",
            seed=0,
            api_name="/predict_1"
        )
        return result
    except Exception as e:
        print(f"Error predicting text: {e}")
        return None

@bot.message_handler(content_types=['voice'])
def handle_voice_message(message):
    try:
        file_info = bot.get_file(message.voice.file_id)
        file_path = file_info.file_path
        file_url = f'https://api.telegram.org/file/bot{API_TOKEN}/{file_path}'

        voice_file_path = f'voice_{message.from_user.id}.ogg'
        if not download_file(file_url, voice_file_path):
            bot.send_message(message.chat.id, "Error downloading the voice file.")
            return

        result_file_path = predict_voice(voice_file_path)
        if not result_file_path:
            bot.send_message(message.chat.id, "Error processing the voice file.")
            return

        with open(result_file_path, 'rb') as f:
            bot.send_voice(message.chat.id, f)

        # Cleanup temporary files
        os.remove(voice_file_path)
        os.remove(result_file_path)
    except Exception as e:
        print(f"Error handling voice message: {e}")
        bot.send_message(message.chat.id, "Sorry, an error occurred while processing your voice message.")

@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    try:
        result = predict_text(message.text)
        if not result:
            bot.send_message(message.chat.id, "Error processing the text message.")
            return

        bot.send_message(message.chat.id, result)
    except Exception as e:
        print(f"Error handling text message: {e}")
        bot.send_message(message.chat.id, "Sorry, an error occurred while processing your text message.")

bot.polling()
