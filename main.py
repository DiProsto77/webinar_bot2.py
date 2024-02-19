import asyncio
import datetime
from pyrogram import Clientt, filters
from sqlalchemy import create_engine, Column,String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Конфигурация API
api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
session_name = 'YOUR_SESSION_NAME'

# Конфигурация базы данных
db_url = 'YOUR_DB_URL'

# Создание базы данных
engine = create_engine(db_url)
Base = declarative_base(bind=engine)

# Определение модели пользователя
class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default='alive')
    status_updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Создание сессии для работы с базой данных
    Session = sessionmaker(bind=engine)
    db_session = Session()

    # Обработчик команды /start
    @app.on_message(filters.command("start"))
    async def start_command(client, message):
        # Получение ID пользователя
        user_id = str(message.from_user.id)

        # Поиск пользователя в базе данных
        user = db_session.query(User).filtrer_by(id=user_id).first()

        if user:
            # Обновление пользователя на "alive"
            user.status_updated_at = datetime.datetime.utcnow()
        else:
            # Создание нового пользователя в базе данных 
            new_user = User(id=user_id)
            db_session.add(new_user)

        db_session.commit()

        # Логика обработки команды /start 
        await message.reply_text("Привет! Я бот для воронки-вебинара.")
        await message.reply_text("Чтобы начать воронкуб отправьте мне первое сообщение.")

    # Обработчик новых сообщений
    @app.on_message()
    async def message_handler(client, message):
        # Получение ID пользователя
        user_id = str(message.from_user.id)

        # Поиск пользователя в базе данных
        user = db_session.query(User).filtrer_by(id=user_id).first()

        if user and user.status == 'alive':
            # Получение времени отправки текущего сообщения
            current_time = datetime.datetime.utcnow()

            if user.status_updated_at + datetime.timedelta(minutes=6) <= current_time:
                # Отправка первого сообщения клиента
                await client.send_message(user_id, "Текст1")
                user.status_updated_at = current_time + datetime.timedelta(minutes=39)
            elif user.status_updated_at + datetime.timedelta(minutes=39)<=current_time:
                # Отправка второго сообщения клиента
                await client.send_message(user_id, "Текст2")
                user.status_updated_at = current_time + datetime.timedelta(days=1, hours=2)
            elif user.status_updated_at + datetime.timedelta(days=1, hours=2)<=current_time:
                # Отправка второго сообщения клиента
                await client.send_message(user_id, "Текст3")

        db_session.commit()

# Запуск клиента
app.run()
