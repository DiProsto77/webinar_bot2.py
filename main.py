from pyrogram import Client
from pyrogram.errors import UserDeactived, BotBlocked
from datetime import datetime, timedelta
import asyncio
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Подключение к базе данных
engine = create_engine('postgresql+asyncpg://user.password@localhost/db_name')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Класс модели пользователя
class User(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	created_at = Column(DateTime, default=datetime.now)
	status = Column(String, default='alive')
	status_updated_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<User(id={self.id}, status={self.status})>"

Base.metadata.create_all(engine)        

# Иницализация клиента Pyrogram
api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
with Client('webinar_bot', api_id, api_hash) as app:
# Функция для отправки сообщения пользователю
    async def send_message(user, message):
        try:
            await app.send_message(user.id, message)
            user.status = 'finished'
        exept (UserDeactived, BotBlocked):     
        # Обработка ошибок при отправке сообщения
        user.status = 'dead'
        user.status_updated_at = datetime.now()
        await session.commit()
            
    async def main():
        while True:
            # Получение "готовых для получения сообщения" пользователей
            users = session.query(User).filter_by(status='alive').all()

            for user in users:
                now = datetime.now()

                # Отправка первого сообщения клиенту
                if user.status_updated_at + timedelta(hours=24) < now:
                    # Если прошло 24 часа с последнего обновления статуса, считаем пользователя "закончившим воронку"
                    user.status = 'finished'
                    user.status_updated_at = datetime.now()
                    await session.commit()
                    continue

                if user.status == 'alive':
                    if now - user.created_at >= timedelta(minutes=6):
                        # Отправка первого сообщения через 6 минут после регистрации
                        await send_message(user, 'Текст1')
                    continue

                if user.status == 'finished':
                    continue

                # Получение последнего сообщения пользователя
                last_message = session.query(UserMessage).filter_by(user_id=user_id).order_by(UserMessage.id.desc()).first()

                if last_message is not None and last_message.trigger_cancel:
                    # Если пользователь отменил отправку последнего сообщения
                    user.status = 'finished'
                    user.status_updated_at = datetime.now()
                    continue
                if last_message is None:
                    continue

                if last_message.message == 'Текст1':
                    if now - last_message.created_at >= timedelta(minutes=33):
                        # Отправка второго сообщения через 39 минут после отправки первого сообщения
                        await send_message(user, 'Текст2')
                    continue
                    
                if last_message.message == 'Текст2':
                    if last_message.trigger1 in ['просто', 'слово']:
                        # Отправка третьего сообщения через 24 часа и 2 часа после отправки второго сообщения или после отмены
                        await send_message(user, 'Текст3')
                    continue

            await asyncio.sleep(60) # Пауза в 1 минуту перед следующей итерацией

app = Client("webinar_bot")
loop = asyncio.get_event_loop()
task = loop.create_task(main())
app.run()
