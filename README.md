<<<<<<< HEAD
# promox
=======
# Painel Proxmox - Mini AWS

Este projeto é um painel web simples para gerenciamento de VMs no Proxmox, permitindo criar, iniciar, parar, reiniciar e acessar o console das VMs, simulando um mini AWS.

## Como rodar

### Backend (FastAPI)
1. Instale as dependências:
   ```bash
   pip install fastapi uvicorn proxmoxer
   ```
2. Configure as variáveis em `backend/main.py` (IP, usuário, senha, nó do Proxmox).
3. Rode o backend:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend
Abra o arquivo `frontend/index.html` no navegador.

## Funcionalidades
- Listar VMs
- Criar VM
- Iniciar, parar e reiniciar VM
- Acessar console (link noVNC)

## Observações
- O painel é um exemplo inicial e pode ser expandido para incluir autenticação, gerenciamento de usuários, snapshots, etc.
- Para produção, proteja o backend e configure HTTPS.
>>>>>>> 9ba5c76 (Projeto Painel Proxmox inicial)
