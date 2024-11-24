import asyncpg

async def connect_to_db():
    return await asyncpg.connect(
        host="localhost", 
        database="test", 
        user="postgres",
        password="0053"
    )