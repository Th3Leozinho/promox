class MaquinaAlugada(Base):
    __tablename__ = "maquinas_alugadas"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    vmid = Column(Integer)
    ip = Column(String)
    porta = Column(Integer)
    login = Column(String)
    senha = Column(String)
    chave_key = Column(String)
    dias_restantes = Column(Integer)
    created_at = Column(String)

class MaquinaAlugadaOut(BaseModel):
    vmid: int
    ip: str
    porta: int
    login: str
    senha: str
    chave_key: str
    dias_restantes: int

    class Config:
        orm_mode = True
# ENDPOINT para buscar informações completas da máquina alugada por vmid e chave_key
from fastapi import Query
@app.get("/maquina_alugada/{vmid}/{chave}", response_model=MaquinaAlugadaOut)
async def get_maquina_alugada(vmid: int, chave: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MaquinaAlugada).where(MaquinaAlugada.vmid == vmid, MaquinaAlugada.chave_key == chave)
    )
    maquina = result.scalar_one_or_none()
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina não encontrada")
    return maquina

from sqlalchemy import Column, Integer, String, select
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from proxmoxer import ProxmoxAPI
from pydantic import BaseModel
from typing import List

Base = declarative_base()

class Credencial(Base):
    __tablename__ = "credenciais"
    id = Column(Integer, primary_key=True, index=True)
    vmid = Column(Integer, index=True)
    login = Column(String)
    senha = Column(String)
    chave = Column(String)

class CredencialCreate(BaseModel):
    vmid: int
    login: str
    senha: str
    chave: str

class CredencialOut(BaseModel):
    id: int
    vmid: int
    login: str
    senha: str
    chave: str

    class Config:
        orm_mode = True


from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import Column, Integer, String, select
from passlib.context import CryptContext
from proxmoxer import ProxmoxAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Configuração do CORS para permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Banco de dados (ajuste a string conforme necessário)
DATABASE_URL = "postgresql+asyncpg://cbadmin:Leozinho191095%40@192.168.15.8:5432/postgres"
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Função para obter sessão do banco
async def get_db():
    async with SessionLocal() as session:
        yield session

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

# Evento de startup para criar as tabelas automaticamente
# Evento de startup para criar as tabelas automaticamente
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
# ENDPOINT para cadastrar credencial
@app.post("/credenciais", response_model=CredencialOut)
async def criar_credencial(cred: CredencialCreate, db: AsyncSession = Depends(get_db)):
    db_cred = Credencial(**cred.dict())
    db.add(db_cred)
    await db.commit()
    await db.refresh(db_cred)
    return db_cred


# Função para obter sessão do banco
async def get_db():
    async with SessionLocal() as session:
        yield session

# ENDPOINT para listar credenciais de um usuário
@app.get("/credenciais", response_model=List[CredencialOut])
async def listar_credenciais(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Credencial))
    return result.scalars().all()

@app.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Sempre trunca a senha para 72 caracteres (bcrypt limitation)
    password = user.password[:72]
    result = await db.execute(select(Usuario).where(Usuario.username == user.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Usuário já existe")
    hashed_password = pwd_context.hash(password)
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

# Configurações do Proxmox (ajuste para produção)
PROXMOX_HOST = "192.168.15.7"
PROXMOX_USER = "root@pam"
PROXMOX_PASSWORD = "Leozinho19@"
PROXMOX_NODE = "pve"

class VMCreateRequest(BaseModel):
    name: str
    cores: int
    memory: int
    disk: int
    iso: str

class VMActionRequest(BaseModel):
    vmid: int

proxmox = ProxmoxAPI(
    PROXMOX_HOST, user=PROXMOX_USER, password=PROXMOX_PASSWORD, verify_ssl=False
)

@app.get("/vms")
def listar_vms():
    vms = proxmox.nodes(PROXMOX_NODE).qemu.get()
    return vms

@app.post("/vms/create")
def criar_vm(req: VMCreateRequest):
    # Exemplo simples, ajuste conforme seu template
    vmid = proxmox.cluster.nextid.get()
    proxmox.nodes(PROXMOX_NODE).qemu.create(
        vmid=vmid,
        name=req.name,
        cores=req.cores,
        memory=req.memory,
        ide2=f"local:iso/{req.iso},media=cdrom",
        sata0=f"local:{req.disk}",
        net0="virtio,bridge=vmbr0"
    )
    return {"status": "VM criada", "vmid": vmid}

@app.post("/vms/start")
def start_vm(req: VMActionRequest):
    proxmox.nodes(PROXMOX_NODE).qemu(req.vmid).status.start.post()
    return {"status": "VM iniciada"}

@app.post("/vms/stop")
def stop_vm(req: VMActionRequest):
    proxmox.nodes(PROXMOX_NODE).qemu(req.vmid).status.stop.post()
    return {"status": "VM parada"}

@app.post("/vms/reboot")
def reboot_vm(req: VMActionRequest):
    proxmox.nodes(PROXMOX_NODE).qemu(req.vmid).status.reboot.post()
    return {"status": "VM reiniciada"}

@app.get("/vms/{vmid}/status")
def status_vm(vmid: int):
    status = proxmox.nodes(PROXMOX_NODE).qemu(vmid).status.current.get()
    return status

@app.get("/vms/{vmid}/console")
def console_vm(vmid: int):
    # Retorna a URL do noVNC do Proxmox
    url = f"https://{PROXMOX_HOST}:8006/?console=kvm&novnc=1&vmid={vmid}&node={PROXMOX_NODE}"
    return {"url": url}

@app.get("/isos")
def listar_isos():
    # Busca ISOs no storage 'local' do Proxmox
    isos = proxmox.nodes(PROXMOX_NODE).storage('local').content.get()
    iso_list = [item['volid'].split('/')[-1] for item in isos if item['content'] == 'iso']
    return iso_list
