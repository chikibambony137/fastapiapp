from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
import pgsql

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