from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# Configurações do Proxmox (ajuste para produção)
PROXMOX_HOST = "192.168.15.7"
PROXMOX_USER = "root@pam"
PROXMOX_PASSWORD = "Leozinho19@"
PROXMOX_NODE = "pve"

# Modelos
class VMCreateRequest(BaseModel):
    name: str
    cores: int
    memory: int
    disk: int
    iso: str

class VMActionRequest(BaseModel):
    vmid: int

# Instância do Proxmox
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
