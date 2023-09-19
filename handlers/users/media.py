from aiogram.types import ContentType, Message, InputFile, MediaGroup

from keyboards.inline import ikb_menu
from loader import dp


@dp.message_handler(content_types=ContentType.PHOTO)
async def send_photo_file_id(message: Message):
    await message.reply(message.photo[-1].file_id)


@dp.message_handler(content_types=ContentType.VIDEO)
async def send_video_file_id(message: Message):
    await message.reply(message.video.file_id)


@dp.message_handler(text='/photo')
async def send_photo(message: Message):
    chat_id = message.from_user.id
    photo_file_id = 'AgACAgIAAxkBAAIBQmLrbqAp-WVyIMs667gVVm1PQqjRAAIaxjEbSOdhS2GLbqFnR37KAQADAgADeQADKQQ'
    photo_bytes = InputFile(path_or_bytesio='media/2.JPG')

    video_file_id = 'BAACAgIAAxkBAAIBS2LrcB13uwba0FZS1hT54-t8oBF4AAKlFwACs1hASzj5O7NS75pwKQQ'

    # await dp.bot.send_photo(chat_id=chat_id, photo=photo_file_id)
    # await dp.bot.send_video(chat_id=chat_id, video=video_file_id)
    await dp.bot.send_photo(chat_id=chat_id, photo=photo_bytes, caption='Картинг', reply_markup=ikb_menu)


@dp.message_handler(text='/album')
async def send_album(message: Message):
    album = MediaGroup()
    photo_file_id = 'AgACAgIAAxkBAAIBQmLrbqAp-WVyIMs667gVVm1PQqjRAAIaxjEbSOdhS2GLbqFnR37KAQADAgADeQADKQQ'
    photo_bytes = InputFile(path_or_bytesio='media/2.JPG')
    video_file_id = 'BAACAgIAAxkBAAIBS2LrcB13uwba0FZS1hT54-t8oBF4AAKlFwACs1hASzj5O7NS75pwKQQ'

    album.attach_photo(photo=photo_file_id)
    album.attach_photo(photo=photo_bytes, caption='Картинг')
    album.attach_video(video=video_file_id)

    await message.answer_media_group(media=album)
