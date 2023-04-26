import asyncio
import random
import requests
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import Message, PollAnswer
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.methods.send_poll import SendPoll
from tools import get_all_questions
from aiogram.methods.send_message import SendMessage


from db import Database
from config import Config
from playgorund import test_user_code


router = Router()


class Form(StatesGroup):
    name = State()
    contact = State()
    about = State()
    role = State()
    language = State()
    quiz = State()


@router.message(Command(commands=["start"]))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receive messages with `/start` command
    """
    await state.set_state(Form.name)
    await message.answer_sticker(sticker="CAACAgIAAxkBAAEIsRtkROjacZqSsL7kyTLQInXSN3slTgAC-ysAAo3foUvDv_DvDanAdS8E")
    await message.reply("Привет! Чтобы пройти тест скажи как тебя зовут")


@router.message(Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    kb = [
        [
            types.KeyboardButton(text="Отправить ☎️",
                                 request_contact=True, resize_keyboard=True),
        ],
    ]

    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)

    await message.reply("Отправь нам свой номер телефона, чтобы мы могли с тобой связаться", reply_markup=keyboard)
    await state.set_state(Form.contact)


@router.message(Form.contact)
async def process_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.contact.phone_number)

    await message.answer_sticker(sticker="CAACAgIAAxkBAAEIsStkROxORZdQUNPOozcw31AmhFhMVgACQCQAAqPzoEu8-sqUeoIrUC8E")
    await message.reply("Расскажи немного о себе!\nВ каких проектах учавствовал, какими знаниями обладаешь", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Form.about)


@router.message(Form.about)
async def process_about(message: types.Message, state: FSMContext):
    await state.update_data(about=message.text)
    await state.set_state(Form.role)
    await SendPoll(
        chat_id=message.from_user.id,
        question="Choose your preferred area:",
        options=[value["name"] for value in questions],
        is_anonymous=False,
    )


class User_quiz_session:
    def __init__(self, timer):
        self.question_list: list = []
        self.score = 0
        self.index = 0
        self.timer = timer

    def add_question(self, question):
        self.question_list.append(question)

    def timer_stop(self):
        self.timer.cancel()


class Quiz:
    def __init__(self, question=None, option=[], answer=[], question_type=None):
        self.question = question
        self.options = option
        self.answer = answer
        self.question_type = question_type


@router.poll_answer(Form.role)
async def process_role(message: PollAnswer, state: FSMContext):
    await state.update_data(role=questions[message.option_ids[0]]["name"])
    await state.update_data(language=questions[message.option_ids[0]]["language"])
    await state.set_state(Form.quiz)
    data = questions[message.option_ids[0]]["questions"]

    random.shuffle(data)

    for question in data:
        random.shuffle(question["options"])

    timer = asyncio.create_task(start_timer(30, message.user.id, state))

    quiz_session = User_quiz_session(timer)

    for i, question in enumerate(data):
        answer_options = []
        for j, option in enumerate(question["options"]):
            answer_options.append(option)

        correct_answers = [option_num for option_num, option in enumerate(
            question["options"]) if option in question["answer"]]

        quiz = Quiz(question['question'], answer_options,
                    correct_answers,  question["type"])

        quiz_session.add_question(quiz)
    await send_question(message.user.id, quiz_session.question_list[0])
    await state.update_data(quiz=quiz_session)


async def start_timer(time: int, chat_id: int, state):
    await asyncio.sleep(time)
    await quiz_end(chat_id, state)


async def quiz_end(chat_id: int, state: FSMContext):
    data = await state.get_data()
    await state.set_state(State())
    quiz_session = data["quiz"]
    quiz_session.timer_stop()

    user = data["name"]
    contacts = data["contact"]
    about = data["about"]
    role = data["role"]
    score = quiz_session.score

    score_percentage = (quiz_session.score / quiz_session.index) * 100

    if score_percentage < 50:
        result_message = "Вы не прошли тест."
    elif 50 <= score_percentage < 70:
        result_message = "У вас средний уровень знаний."
    else:
        result_message = "Вы отлично постарались! Максимальная оценка!"

    repository.save_user(chat_id, user, contacts, about, role, score)
    await SendMessage(chat_id=chat_id,
                      text=f"Имя - [{user}]\nКонтакты - [{contacts}]\nО себе - [{about}]\nВы прошли тест {role}! Вы получили вот столько баллов {quiz_session.score} . Вы ответили правильно на {quiz_session.score} / {quiz_session.index} вопросов. Оценка - [{result_message}]")


@router.poll_answer(Form.quiz)
async def handle_answer(message: PollAnswer, state: FSMContext):
    data = await state.get_data()
    quiz_session = data["quiz"]
    index = quiz_session.index
    right_answ = quiz_session.question_list[index].answer
    if message.option_ids == right_answ:
        quiz_session.score += 1

    quiz_session.index += 1
    if index+1 == len(quiz_session.question_list):
        await quiz_end(message.user.id, state)
        return
    await send_question(message.user.id, quiz_session.question_list[index+1])
    await state.update_data(quiz=quiz_session)


@router.message(Form.quiz)
async def handle_answer_code(message: types.Message, state: FSMContext):
    data = await state.get_data()
    quiz_session = data["quiz"]
    index = quiz_session.index
    lang = data["language"]
    file = f"./cache/{message.document.file_id}"
    download_file(config.token, message.document.file_id, file)
    result = test_user_code(
        lang, file, quiz_session.question_list[index])
    if result:
        quiz_session.score += 1
    quiz_session.index += 1
    if index+1 == len(quiz_session.question_list):
        await quiz_end(message.from_user.id, state)
        return
    await send_question(message.from_user.id, quiz_session.question_list[index+1])
    await state.update_data(quiz=quiz_session)


async def run_bot(token: str) -> None:
    dp = Dispatcher()
    dp.include_router(router)

    bot = Bot(token, parse_mode="HTML")
    await dp.start_polling(bot)


async def send_question(chat_id: int, question: Quiz):
    if question.question_type == "question":
        await SendPoll(
            chat_id=chat_id,
            question=question.question,
            options=question.options,
            is_anonymous=False,
            allows_multiple_answers=True,
        )

    if question.question_type == "code":
        await SendMessage(
            chat_id=chat_id,
            text=f'{question.question} (код необходим файлом)'
        )


def download_file(bot_token, file_id, file_path):
    url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}"
    response = requests.get(url)
    json_data = response.json()
    file_url = f"https://api.telegram.org/file/bot{bot_token}/{json_data['result']['file_path']}"
    response = requests.get(file_url)
    with open(file_path, "wb") as f:
        f.write(response.content)


if __name__ == "__main__":
    config = Config()
    repository = Database(config)
    questions = get_all_questions()
    asyncio.run(run_bot(config.token))
