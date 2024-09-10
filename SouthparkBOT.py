from telethon import TelegramClient, events
from dotenv import load_dotenv, set_key
import asyncio
import random
import os
import datetime

load_dotenv()
# Вставьте сюда свои данные
api_id = str(os.getenv('id'))
api_hash = str(os.getenv('hash'))
phone_number = str(os.getenv('number'))

# Список каналов. Для супергрупп с топиками используйте кортеж: (имя канала, ID топика)
channels = [
    str(os.getenv('channel')),  # Обычный канал
    (str(os.getenv('channelTwo')), 2637)  # Супергруппа с топиком (имя канала, ID топика)
]

# Добавляем параметры для эмуляции устройства
client = TelegramClient(
    str(os.getenv('suka')), api_id, api_hash,
    system_version='4.16.30-vxCUSTOM',  # Версия системы
    device_model='PC',  # Модель устройства
    app_version='7.2.1'  # Версия приложения
)


def generate_random_series():
    """Генерирует случайную серию для текущей даты."""
    today = datetime.datetime.now().strftime('%Y%m%d')
    random_number = random.randint(1000, 9999)
    return f"{today}-{random_number}"


async def delete_previous_message(channel, previous_message_id):
    """Удаляет предыдущее сообщение по его ID."""
    try:
        if previous_message_id:
            await client.delete_messages(channel, int(previous_message_id))
            print(f"Предыдущее сообщение с ID {previous_message_id} удалено.")
    except Exception as e:
        print(f"Ошибка при удалении сообщения с ID {previous_message_id}: {e}")


async def main():
    try:
        await client.start(phone_number)
        print("Клиент запущен.")

        # Получаем последний сохраненный ID сообщения для двух каналов из .env
        previous_message_id_channel_one = os.getenv('last_message_id_channel_one')
        previous_message_id_channel_two = os.getenv('last_message_id_channel_two')

        while True:
            # Получаем последние 1000 сообщений из первого канала
            messages = await client.get_messages(channels[0], limit=1000)
            print(f"Получено сообщений: {len(messages)}")

            # Фильтруем сообщения для нахождения видео
            video_messages = [msg for msg in messages if msg.video]

            if video_messages:
                # Рандомизация среди сообщений с видео
                random_video = random.choice(video_messages)
                print(f"Выбрано видео ID: {random_video.id}")

                # Получаем текстовое содержимое сообщения
                message_text = random_video.text or ""
                print(f"Текст сообщения: {message_text}")

                # Генерируем случайную серию
                random_series = generate_random_series()
                print(f"Случайная серия: {random_series}")

                # Формируем тексты для двух сообщений
                new_message_text_one = f"{message_text}\n\nСлучайная серия на сегодня\n\n[Все серии южного парка](https://t.me/southsparkvse)"
                new_message_text_two = f"{message_text}\n\nСлучайная серия на сегодня\n\n[Наш другой канал с фильмами и сериалами](https://t.me/apelsinovypodval)"

                # Отправляем сообщение в первый канал и удаляем предыдущее
                await delete_previous_message(channels[0], previous_message_id_channel_one)
                sent_message_one = await client.send_message(
                    channels[0],  # Назначение (первый канал)
                    new_message_text_one,  # Новый текст сообщения
                    file=random_video.video  # Пересылаем видео
                )
                print(f"Сообщение с видео и текстом переслано в {channels[0]}.")
                # Сохраняем ID отправленного сообщения в .env для первого канала
                set_key('.env', 'last_message_id_channel_one', str(sent_message_one.id))
                print(f"ID отправленного сообщения {sent_message_one.id} сохранен в .env для первого канала.")

                # Отправляем сообщение во второй канал (супергруппа с топиком) и удаляем предыдущее
                await delete_previous_message(channels[1][0], previous_message_id_channel_two)
                sent_message_two = await client.send_message(
                    channels[1][0],  # Назначение (второй канал)
                    new_message_text_two,  # Новый текст сообщения
                    file=random_video.video,  # Пересылаем видео
                    reply_to=channels[1][1]  # Отправляем в конкретный топик
                )
                print(f"Сообщение с видео и текстом переслано в топик {channels[1][1]} супергруппы {channels[1][0]}.")
                # Сохраняем ID отправленного сообщения в .env для второго канала
                set_key('.env', 'last_message_id_channel_two', str(sent_message_two.id))
                print(f"ID отправленного сообщения {sent_message_two.id} сохранен в .env для второго канала.")

                break  # Выход из цикла после успешной пересылки
            else:
                print("Видео не найдено, пробуем снова.")
                await asyncio.sleep(10)  # Ожидание перед новой попыткой

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        await client.run_until_disconnected()


if __name__ == '__main__':
    asyncio.run(main())
