from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./hello.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models
class HelloMessage(Base):
    __tablename__ = "hello_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, index=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize database with default message if empty
def init_db():
    db = SessionLocal()
    try:
        message = db.query(HelloMessage).first()
        if not message:
            default_message = HelloMessage(id=1, message="Hello from FastAPI!")
            db.add(default_message)
            db.commit()
    finally:
        db.close()

init_db()

# Pydantic models for request validation
class MessageRequest(BaseModel):
    message: str

class UserRequest(BaseModel):
    name: str

class User(BaseModel):
    id: int
    name: str

# In-memory user storage
users_db: List[User] = [
    User(id=1, name="Alice"),
    User(id=2, name="Bob")
]

# Configure CORS for React frontend running on localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/hello")
async def get_hello():
    """
    Returns a greeting message from the database.
    """
    db = SessionLocal()
    try:
        message = db.query(HelloMessage).first()
        if message:
            return {"message": message.message}
        return {"message": "Hello from FastAPI!"}
    finally:
        db.close()


@app.get("/api/users")
async def get_users():
    """
    Returns a list of sample users.
    """
    return users_db


@app.post("/api/hello")
async def post_hello(request: MessageRequest):
    """
    Updates the greeting message in the database and returns the updated message.
    """
    db = SessionLocal()
    try:
        message = db.query(HelloMessage).first()
        if message:
            message.message = request.message
        else:
            message = HelloMessage(id=1, message=request.message)
            db.add(message)
        db.commit()
        db.refresh(message)
        return {"message": message.message}
    finally:
        db.close()


@app.patch("/api/hello")
async def patch_hello(request: MessageRequest):
    """
    Updates the greeting message in the database and returns the updated message.
    """
    db = SessionLocal()
    try:
        message = db.query(HelloMessage).first()
        if message:
            message.message = request.message
        else:
            message = HelloMessage(id=1, message=request.message)
            db.add(message)
        db.commit()
        db.refresh(message)
        return {"message": message.message}
    finally:
        db.close()


@app.post("/api/users")
async def create_user(request: UserRequest):
    """
    Creates a new user and adds it to the in-memory list.
    """
    new_id = max([u.id for u in users_db], default=0) + 1
    new_user = User(id=new_id, name=request.name)
    users_db.append(new_user)
    return new_user


