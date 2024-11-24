from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import  Column, Integer, String
from fastapi import FastAPI

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:0053@localhost/test"

# создание движка
engine = create_engine(SQLALCHEMY_DATABASE_URL)

#создаем базовый класс для моделей
class Base(DeclarativeBase): pass
 
# создаем модель, объекты которой будут храниться в бд
class Person(Base):
    __tablename__ = "people"
 
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer,)
 
# создаем таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI()