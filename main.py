import time
from random import randint
import markdown

import numpy as np
import soundfile as sf
import yaml
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, ReplyKeyboardRemove, FSInputFile
from scipy.signal import resample

from models import IeltsSample, FirstIelts, ThirdIelts, SecondIelts, ToeflSample, FirstToefl, SecondToefl, ThirdToefl, \
    FourthToefl
from speaking_api_sdk import SpeakingApiSdk

# Initialize bot and dispatcher
BOT_TOKEN = "8191176893:AAG2an5Eyw050DFTUJ4a_ml3MrEcD0tMOUc"
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
speaking_api_sdk = SpeakingApiSdk()
with open("messages_config.yaml", "r", encoding="utf-8") as f:
    messages_config = yaml.safe_load(f)
    ielts = messages_config["ielts"]
    toefl = messages_config["toefl"]


# Define FSM states
class SpeakingState(StatesGroup):
    # IELTS
    passing_ielts_speaking_1_part = State()
    passing_ielts_speaking_2_part = State()
    passing_ielts_speaking_2_followup_part = State()
    passing_ielts_speaking_3_part = State()
    finished_ielts = State()
    ielts_sample = IeltsSample(0, FirstIelts(), SecondIelts(), ThirdIelts())
    ielts_sample_id = 0
    current_ielts_part = 0
    ielts_chatting_with_bot = State()
    ielts_answer = ""
    ielts_audio_path = ""
    # TOEFL
    passing_toefl_speaking_1_part = State()
    passing_toefl_speaking_2_part = State()
    passing_toefl_speaking_3_part = State()
    passing_toefl_speaking_4_part = State()
    finished_toefl = State()
    toefl_sample = ToeflSample(0, FirstToefl(), SecondToefl(), ThirdToefl(), FourthToefl(), )
    toefl_sample_id = 0
    current_toefl_part = 0


# Define the main menu keyboard
menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎙️ IELTS Speaking Practice"), KeyboardButton(text="🎙️ TOEFL Speaking Practice")],
        [KeyboardButton(text="📂 Speaking Materials")],
        [KeyboardButton(text="📚 IELTS Reading & Writing Practice"),
         KeyboardButton(text="📚 TOEFL Reading & Writing Practice")]
    ],
    resize_keyboard=True
)


# Command handlers
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer(messages_config["start_message"].format(username=message.from_user.first_name),
                         reply_markup=menu_kb, )


# Command handlers
@dp.message(Command("exit"))
@dp.message(F.text.lower().contains("exit"))
async def exit_command(message: Message, state: FSMContext):
    await message.answer(messages_config["start_message"].format(username=message.from_user.first_name),
                         reply_markup=menu_kb, )
    await state.set_state(None)


@dp.message(F.text.lower().contains("speaking materials"))
async def helpful_materials(message: Message):
    await message.answer(messages_config["helpful_materials"], reply_markup=menu_kb, )


@dp.message(F.text.lower().contains("ielts reading & writing practice"))
async def ielts_reading_and_writing(message: Message):
    chat_id = message.chat.id
    await message.answer(ielts["reading_and_writing"])
    documents = [
        ("static/samples/ielts/writing_sample.pdf", """
            ✍️ IELTS Writing Practice
Prepare for Task 1 and Task 2 with this comprehensive writing practice set.
            """),
        ("static/samples/ielts/reading_sample.pdf", """
        📖 IELTS Reading Practice
Boost your reading skills with 3 practice sections and 40 questions.   
        """),
        ("static/samples/ielts/answer_keys.pdf", """
        ✅ IELTS Answer Key
Check your answers and track your progress with this detailed answer key.
        """),
    ]

    for doc in documents:
        file_input = FSInputFile(doc[0])
        await bot.send_document(chat_id, file_input, caption=doc[1])


@dp.message(F.text.lower().contains("toefl reading & writing practice"))
async def toefl_reading_and_writing(message: Message):
    chat_id = message.chat.id
    await message.answer(toefl["reading_and_writing"])
    documents = [
        ("static/samples/toefl/all_combined_sample.pdf", """
            ✍️ TOEFL Writing & Reading Practice with Answer Key
            Prepare for all tasks with this comprehensive practice set.
            Also contains Answer Keys so you can check yourself later
            """),

    ]

    for doc in documents:
        file_input = FSInputFile(doc[0])
        await bot.send_document(chat_id, file_input, caption=doc[1])


@dp.message(F.text.lower().contains("ielts speaking practice"))
async def start_ielts(message: Message, state: FSMContext):
    await message.answer(ielts["info"])
    _ielts_sample = speaking_api_sdk.get_ielts_sample(randint(3, 3))
    await state.update_data(ielts_sample=_ielts_sample)
    menu = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="❌ Exit")]
    ],resize_keyboard=True)
    await message.answer(ielts["first_part"], reply_markup=menu)
    await message.answer(_ielts_sample.first.content)
    await state.set_state(SpeakingState.passing_ielts_speaking_2_part)
    await state.update_data(current_ielts_part=1)
    await state.update_data(ielts_sample_id=_ielts_sample.id)


@dp.message(F.content_type == "voice" and StateFilter(SpeakingState.passing_ielts_speaking_2_part))
async def ielts_2_part(message: Message, state: FSMContext):
    user_data = await state.get_data()
    _ielts_sample: IeltsSample = user_data["ielts_sample"]

    file_id = message.voice.file_id
    user_id = message.from_user.id
    current_ielts_part = user_data["current_ielts_part"]
    print(current_ielts_part)
    # Get file information from Telegram
    file_info = await bot.get_file(file_id)
    # Set the file path for saving
    file_path = f"voices/ielts/{user_id}_{current_ielts_part}.ogg"
    # Download and save the file
    await bot.download_file(file_info.file_path, file_path)

    await message.answer(ielts["second_part"], reply_markup=None)
    await message.answer(_ielts_sample.second.content, parse_mode=ParseMode.HTML)
    await state.set_state(SpeakingState.passing_ielts_speaking_2_followup_part)
    await state.update_data(current_ielts_part=2)


@dp.message(F.content_type == "voice" and StateFilter(SpeakingState.passing_ielts_speaking_2_followup_part))
async def ielts_2_followup_part(message: Message, state: FSMContext):
    user_data = await state.get_data()
    _ielts_sample: IeltsSample = user_data["ielts_sample"]

    file_id = message.voice.file_id
    user_id = message.from_user.id
    current_ielts_part = user_data["current_ielts_part"]
    print(current_ielts_part)
    # Get file information from Telegram
    file_info = await bot.get_file(file_id)
    # Set the file path for saving
    file_path = f"voices/ielts/{user_id}_{current_ielts_part}.ogg"
    # Download and save the file
    await bot.download_file(file_info.file_path, file_path)
    # Process to the next level
    await message.answer(_ielts_sample.second.followup, parse_mode=ParseMode.HTML)
    await state.set_state(SpeakingState.passing_ielts_speaking_3_part)
    await state.update_data(current_ielts_part=22)


@dp.message(F.content_type == "voice" and StateFilter(SpeakingState.passing_ielts_speaking_3_part))
async def ielts_3_part(message: Message, state: FSMContext):
    user_data = await state.get_data()
    _ielts_sample: IeltsSample = user_data["ielts_sample"]

    file_id = message.voice.file_id
    user_id = message.from_user.id
    current_ielts_part = user_data["current_ielts_part"]
    print(current_ielts_part)
    # Get file information from Telegram
    file_info = await bot.get_file(file_id)
    # Set the file path for saving
    file_path = f"voices/ielts/{user_id}_{current_ielts_part}.ogg"
    # Download and save the file
    await bot.download_file(file_info.file_path, file_path)
    # Process to the next level
    await message.answer(ielts["third_part"], reply_markup=None)
    await message.answer(_ielts_sample.third.content, parse_mode=ParseMode.HTML)
    await state.set_state(SpeakingState.finished_ielts)
    await state.update_data(current_ielts_part=3)


@dp.message(F.content_type == "voice" and StateFilter(SpeakingState.finished_ielts))
async def finish_ielts(message: Message, state: FSMContext):
    # Get the file ID of the voice message
    file_id = message.voice.file_id
    user_id = message.from_user.id
    user_data = await state.get_data()
    current_ielts_part = user_data["current_ielts_part"]
    ielts_sample_id = user_data["ielts_sample_id"]
    print(current_ielts_part)
    # Get file information from Telegram
    file_info = await bot.get_file(file_id)
    # Set the file path for saving
    file_path = f"voices/ielts/{user_id}_{current_ielts_part}.ogg"
    # Download and save the file
    await bot.download_file(file_info.file_path, file_path)
    # data, samplerate = sf.read(file_path)
    # sf.write(f"voices/ielts/{user_id}_{current_ielts_part}.wav", data, samplerate)

    input_files = ["static/first_part.ogg",
                   f"voices/ielts/{user_id}_1.ogg",
                   "static/second_part.ogg",
                   f"voices/ielts/{user_id}_2.ogg",
                   "static/follow_up_questions.ogg",
                   f"voices/ielts/{user_id}_22.ogg",
                   "static/third_part.ogg",
                   f"voices/ielts/{user_id}_3.ogg", ]
    unix_time = time.time()
    output_file = f"voices/ielts/{user_id}_{unix_time}_final.ogg"
    merge_ogg_files(output_file, input_files)
    menu = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="❌ Exit")]
    ],resize_keyboard=True)
    await message.answer("✅ Mock exam complete! ⏳ Awaiting AI's response.", reply_markup=menu)
    await state.set_state(SpeakingState.ielts_chatting_with_bot)
    _ielts_answer = speaking_api_sdk.answer_ielts(output_file, f"{user_id}_{unix_time}_final.ogg", ielts_sample_id)
    await state.update_data(ielts_answer=_ielts_answer.content)
    await state.update_data(ielts_audio_path=output_file)

    print(_ielts_answer.content.strip())
    print("_______")
    for segment in _ielts_answer.content.split("\n"):
        print(segment)
        if segment:
            # segment = segment.replace("**","__").replace("*","").replace("__","**").replace(".","\.").replace("")
            import re

            REFACTOR_REGEX = r"(?<!\\)(_|\*|\[|\]|\(|\)|\~|`|>|#|\+|-|=|\||\{|\}|\.|\!)"
            segment = re.sub(REFACTOR_REGEX, lambda t: "\\"+t.group(), segment)
            segment = segment.replace("\\*\\*", "**")
            print(segment)

            await message.answer(segment,parse_mode=ParseMode.MARKDOWN_V2)
            time.sleep(0.1)
    await message.answer("Now you can ask me somme questions about the scoring")

@dp.message(StateFilter(SpeakingState.ielts_chatting_with_bot))
async def ask_ai_ielts(message: Message, state: FSMContext):
    user_data = await state.get_data()
    ielts_answer = user_data["ielts_answer"]
    ielts_audio_path = user_data["ielts_audio_path"]
    message_text = message.text
    menu = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="❌ Exit")]
    ],resize_keyboard=True)
    ielts_answer += f"\n User: {message_text}"
    await message.answer("✅ Your question was sent! ⏳ Awaiting AI's response.", reply_markup=menu)
    ai_response = speaking_api_sdk.ask_ai_ielts(ielts_answer, audio=ielts_audio_path).content
    for segment in ai_response.split("\n"):
        if segment:
            segment = segment.replace("*","")
            await message.reply(segment)
            time.sleep(0.1)


@dp.message(F.text.lower().contains("toefl speaking practice"))
async def start_toefl(message: Message, state: FSMContext):
    await message.answer(toefl["info"])
    _toefl_sample = speaking_api_sdk.get_toefl_sample(randint(1, 1))
    await state.update_data(toefl_sample=_toefl_sample)
    menu = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="❌ Exit")]
    ],resize_keyboard=True)

    await message.answer(toefl["first_part"], reply_markup=menu)
    await message.answer(_toefl_sample.first.content)
    await state.set_state(SpeakingState.passing_toefl_speaking_2_part)
    await state.update_data(current_toefl_part=1)
    await state.update_data(toefl_sample_id=_toefl_sample.id)


@dp.message(F.content_type == "voice" and StateFilter(SpeakingState.passing_toefl_speaking_2_part))
async def toefl_2_part(message: Message, state: FSMContext):
    user_data = await state.get_data()
    _toefl_sample: ToeflSample = user_data["toefl_sample"]

    file_id = message.voice.file_id
    user_id = message.from_user.id
    current_toefl_part = user_data["current_toefl_part"]
    print(current_toefl_part)
    # Get file information from Telegram
    file_info = await bot.get_file(file_id)
    # Set the file path for saving
    file_path = f"voices/toefl/{user_id}_{current_toefl_part}.ogg"
    # Download and save the file
    await bot.download_file(file_info.file_path, file_path)

    await message.answer(toefl["second_part"], reply_markup=None)
    await message.answer(_toefl_sample.second.content, parse_mode=ParseMode.HTML)
    await state.set_state(SpeakingState.passing_toefl_speaking_3_part)
    await state.update_data(current_toefl_part=2)


@dp.message(F.content_type == "voice" and StateFilter(SpeakingState.passing_toefl_speaking_3_part))
async def toefl_3_part(message: Message, state: FSMContext):
    user_data = await state.get_data()
    _toefl_sample: ToeflSample = user_data["toefl_sample"]

    file_id = message.voice.file_id
    user_id = message.from_user.id
    current_toefl_part = user_data["current_toefl_part"]
    print(current_toefl_part)
    # Get file information from Telegram
    file_info = await bot.get_file(file_id)
    # Set the file path for saving
    file_path = f"voices/toefl/{user_id}_{current_toefl_part}.ogg"
    # Download and save the file
    await bot.download_file(file_info.file_path, file_path)
    # Process to the next level
    await message.answer(toefl["third_part"], reply_markup=None)
    await message.answer(_toefl_sample.third.content, parse_mode=ParseMode.HTML)
    await state.set_state(SpeakingState.passing_toefl_speaking_4_part)
    await state.update_data(current_toefl_part=3)


@dp.message(F.content_type == "voice" and StateFilter(SpeakingState.passing_toefl_speaking_4_part))
async def toefl_4_part(message: Message, state: FSMContext):
    user_data = await state.get_data()
    _toefl_sample: ToeflSample = user_data["toefl_sample"]

    file_id = message.voice.file_id
    user_id = message.from_user.id
    current_toefl_part = user_data["current_toefl_part"]
    print(current_toefl_part)
    # Get file information from Telegram
    file_info = await bot.get_file(file_id)
    # Set the file path for saving
    file_path = f"voices/toefl/{user_id}_{current_toefl_part}.ogg"
    # Download and save the file
    await bot.download_file(file_info.file_path, file_path)
    # Process to the next level
    await message.answer(toefl["fourth_part"], reply_markup=None)
    await message.answer(_toefl_sample.fourth.audio, parse_mode=ParseMode.HTML)
    await message.answer(_toefl_sample.fourth.content, parse_mode=ParseMode.HTML)
    await state.set_state(SpeakingState.finished_toefl)
    await state.update_data(current_toefl_part=4)


@dp.message(F.content_type == "voice" and StateFilter(SpeakingState.finished_toefl))
async def finish_toefl(message: Message, state: FSMContext):
    # Get the file ID of the voice message
    file_id = message.voice.file_id
    user_id = message.from_user.id
    user_data = await state.get_data()
    current_toefl_part = user_data["current_toefl_part"]
    toefl_sample_id = user_data["toefl_sample_id"]
    print(current_toefl_part)
    # Get file information from Telegram
    file_info = await bot.get_file(file_id)
    # Set the file path for saving
    file_path = f"voices/toefl/{user_id}_{current_toefl_part}.ogg"
    # Download and save the file
    await bot.download_file(file_info.file_path, file_path)

    input_files = ["static/first_part.ogg",
                   f"voices/toefl/{user_id}_1.ogg",
                   "static/second_part.ogg",
                   f"voices/toefl/{user_id}_2.ogg",
                   "static/third_part.ogg",
                   f"voices/toefl/{user_id}_3.ogg",
                   "static/fourth_part.ogg",
                   f"voices/toefl/{user_id}_4.ogg", ]
    unix_time = time.time()
    output_file = f"voices/toefl/{user_id}_{unix_time}_final.ogg"
    merge_ogg_files(output_file, input_files)

    await message.answer("You have finished your mock exam", reply_markup=menu_kb)
    await state.set_state(None)
    toefl_answer = speaking_api_sdk.answer_toefl(output_file, f"{user_id}_{unix_time}_final.ogg", toefl_sample_id)
    await message.answer(toefl_answer.content)


def merge_ogg_files(output_path, ogg_files, target_samplerate=44100):
    """
    Merges multiple OGG files into one, resampling if necessary.

    Parameters:
        output_path (str): Path to save the combined OGG file.
        ogg_files (list): List of paths to input OGG files.
        target_samplerate (int): Desired sample rate for the combined file.
    """
    combined_data = []

    for ogg_file in ogg_files:
        # Load OGG file
        data, samplerate = sf.read(ogg_file)
        # Resample if sample rate differs
        if samplerate != target_samplerate:
            num_samples = int(len(data) * target_samplerate / samplerate)
            data = resample(data, num_samples)
        combined_data.append(data)

    # Concatenate all audio data
    final_data = np.concatenate(combined_data)

    # Save to the output OGG file
    sf.write(output_path, final_data, target_samplerate, format='OGG')
    print(f"Combined OGG file saved as {output_path}")


def text_to_html(text):
    """
  Converts plain text to basic HTML with basic formatting.

  Args:
    text: The input plain text string.

  Returns:
    The converted HTML string.
  """

    html_text = ""

    # Replace newlines with <br> tags
    html_text = text.replace("\n", "<br>")

    # Basic formatting (more can be added)
    html_text = html_text.replace("**", "<b>")  # Bold
    html_text = html_text.replace("__", "<i>")  # Italic

    return html_text


if __name__ == "__main__":
    dp.run_polling(bot, skip_updates=True)
