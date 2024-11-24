from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationError
from fastapi.responses import FileResponse
import pgsql
from enum import Enum
from datetime import datetime, date
import re

app = FastAPI()

async def lifespan(app):
    app.db_connection = await pgsql.connect_to_db()
    yield
    await app.db_connection.close()

app = FastAPI(lifespan=lifespan)

class Author(BaseModel):
    id: int
    name: str
    age: int

class Book(BaseModel):
    id: int
    name: str
    author: Author

class BookAdd(BaseModel):
    name: str
    author_id: int

authors = [
    {"id": 1, "name": "J. K. Rowling", "age": 47},
    {"id": 2, "name": "Abeme", "age": 42},
    {"id": 3, "name": "wegsd", "age": 23},
    {"id": 4, "name": "dfdfdfdfd", "age": 52}
]

books = [
    {"id": 1, "name": "Garry Potter", "author": authors[0]},
    {"id": 2, "name": "Aboba", "author": authors[2]},
    {"id": 3, "name": "fsfas", "author": authors[1]},
    {"id": 4, "name": "sdsdsd", "author": authors[3]}
]

@app.get("/")
async def main():
    return FileResponse('./about.html')

@app.get('/books')
async def show_books():
    return [Book(**book) for book in books]

@app.get('/authors')
async def show_users():
    return [Author(**user) for user in authors]

@app.get('/book/{book_id}')
async def find_book(book_id: Optional[int] = None):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")
    


@app.post('/book/add')
async def add_book(book: BookAdd):

    author = next((author for author in authors if author["id"] == book.author_id), None)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    
    new_book_id = len(books) + 1
    new_book = {
        "id": new_book_id,
        "name": book.name,
        "author": author
        }
    books.append(new_book)
    
    return Book(**new_book)

@app.get("/table/{table_name}")
async def root(table_name: str):
    result = await app.db_connection.fetch(f"SELECT * FROM {table_name}")
    return {"result": result}






students = [{
  "student_id": 1,
  "first_name": "Иван",
  "last_name": "Иванов",
  "date_of_birth": "1998-05-15",
  "email": "ivan.ivanov@example.com",
  "phone_number": "+71234567890",
  "address": "г. Москва, ул. Пушкина, д. 10, кв. 5",
  "enrollment_year": 2017,
  "major": "Информатика",
  "course": 3,
  "special_notes": "Без особых примет"
}
]


class Major(str, Enum):
    informatics = "Информатика"
    economics = "Экономика"
    law = "Право"
    medicine = "Медицина"
    engineering = "Инженерия"
    languages = "Языки"

class Student(BaseModel):
    student_id: int
    phone_number: str = Field(default=..., description="Номер телефона в международном формате, начинающийся с '+'")
    first_name: str = Field(default=..., min_length=1, max_length=50, description="Имя студента, от 1 до 50 символов")
    last_name: str = Field(default=..., min_length=1, max_length=50, description="Фамилия студента, от 1 до 50 символов")
    date_of_birth: date = Field(default=..., description="Дата рождения студента в формате ГГГГ-ММ-ДД")
    email: EmailStr = Field(default=..., description="Электронная почта студента")
    address: str = Field(default=..., min_length=10, max_length=200, description="Адрес студента, не более 200 символов")
    enrollment_year: int = Field(default=..., ge=2002, description="Год поступления должен быть не меньше 2002")
    major: Major = Field(default=..., description="Специальность студента")
    course: int = Field(default=..., ge=1, le=5, description="Курс должен быть в диапазоне от 1 до 5")
    special_notes: Optional[str] = Field(default=None, max_length=500, description="Дополнительные заметки, не более 500 символов")

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, values: str) -> str:
        if not re.match(r'^\+\d{1,15}$', values):
            raise ValueError('Номер телефона должен начинаться с "+" и содержать от 1 до 15 цифр')
        return values

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, values: date):
        if values and values >= datetime.now().date():
            raise ValueError('Дата рождения должна быть в прошлом')
        return values
    

@app.post('/student')
async def add_student(student: Student):

    # student = next((studs for studs in students if studs["student_id"] == student.student_id), None)
    # if not student:
    #     raise HTTPException(status_code=404, detail="Student not found")
    
    new_student_id = len(students) + 1
    new_student = {
            "student_id": new_student_id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "date_of_birth": student.date_of_birth,
            "email": student.email,
            "phone_number": student.phone_number,
            "address": student.address,
            "enrollment_year": student.enrollment_year,
            "major": student.major,
            "course": student.course,
            "special_notes": student.special_notes
        }
    students.append(new_student)
    
    return Student(**new_student)

@app.get('/students') 
async def show_students():
    return [Student(**student) for student in students]