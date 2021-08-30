from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from time import sleep
from os import path, makedirs, listdir
from shutil import copyfile


import hide_car_number
import logging

TOKEN = "HERE IS A TOKEN"

# Объект бота
bot = Bot(token=TOKEN)
# Диспетчер для бота
dp = Dispatcher(bot)

# Configure logging
# logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(msg: types.Message):
    await msg.answer(f'{msg.from_user.first_name}, Я бот который скрывает номер автомобиля,'
                     f'\nДля старта отправьте изображение')


@dp.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):
    if msg.text.lower() == 'привет':
        await msg.reply('Привет! я бот который скрывает номер автомобиля')
    else:
        await msg.reply('Отправьте изображение с номером автомобиля, чтобы его скрыть')


@dp.message_handler(content_types=['photo'])
async def get_photo_messages(msg: types.Message):
    """
        Функция для обработки отправленных юзером изображений
        :return отправляет изображение со скрытым номером автомобиля
        Если на картинке не найден номер автомобиля - возвращает что не найден номер
    """
    await msg.reply('YES, ITS A PHOTO')
    current_path = path.dirname(path.abspath(__file__))   # C:\Users\tansh\selenium_course\car_hide

    # Если нет относительной директории, создаем новую
    directory = current_path + "\\original_photos\\"
    if not path.exists(directory):
        makedirs(directory)

    # Генерация названия фотографии
    edited_photos_path = current_path + "\\original_photos\\"
    num_files = len([f for f in listdir(edited_photos_path) if path.isfile(path.join(edited_photos_path, f))])

    cnt = num_files
    img_name = f"file_{cnt}.jpeg"

    # Загружаем оригинальные фотографии в папку original_photos
    res = await msg.photo[-1].download(f'original_photos/{img_name}')
    print("SAVED ORIGINAL PHOTO IN ", res.name)

    await msg.reply('Обработка изображения...')
    img_name = f'original_photos/{img_name}'

    # Функция для скрытия номера автомобиля
    car_number_exists = hide_car_number.edit_photo(img_name)

    if car_number_exists:
        try:
            await bot.send_photo(msg.chat.id, photo=open(current_path + f"\edited_photos\hidden_{img_name[16:]}", 'rb'))
        except FileNotFoundError:
            print("FileNotFoundError -->  EDITED PHOTO (hidden car number image) NOT FOUND")
    else:
        await msg.reply('Не найден номер автомобиля')


@dp.message_handler()
async def echo(msg: types.Message):
    await message.answer("Отправьте изображение с номером автомобиля, чтобы его скрыть")


if __name__ == '__main__':
    executor.start_polling(dp)


