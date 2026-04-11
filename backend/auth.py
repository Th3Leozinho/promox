from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.orm import declarative_base
from passlib.context import CryptContext

DATABASE_URL = "postgresql+asyncpg://cbadmin:Leozinho191095%40@192.168.15.8:5432/postgres"

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


# ...existing code...





app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Evento de startup para criar as tabelas automaticamente
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with SessionLocal() as session:
        yield session

@app.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    if len(user.password) > 72:
        raise HTTPException(status_code=400, detail="Senha muito longa (máx. 72 caracteres)")
    result = await db.execute(select(Usuario).where(Usuario.username == user.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Usuário já existe")
    hashed_password = pwd_context.hash(user.password)
    db_user = Usuario(username=user.username, password=hashed_password)
    db.add(db_user)
    await db.commit()
    return {"msg": "Usuário cadastrado com sucesso"}

@app.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Usuario).where(Usuario.username == user.username))
    db_user = result.scalar_one_or_none()
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")
    return {"msg": "Login realizado com sucesso"}
