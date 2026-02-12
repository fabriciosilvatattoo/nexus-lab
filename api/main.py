
import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import requests
import git
from pathlib import Path
from dotenv import load_dotenv

# Carrega ambiente
load_dotenv()

app = FastAPI(title="NEXUS Agent API", version="1.0.0")

# --- 1. CONFIGURAÇÃO GERAL ---
# Onde o Agente vai trabalhar na VPS (Sandbox)
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "./workspace")
ANTIGRAVITY_KIT_DIR = os.getenv("KIT_DIR", "./antigravity-kit")

# Chave GLM (se não tiver no env, pega do argumento)
GLM_API_KEY = os.getenv("GLM_API_KEY", "")

# --- 2. INTEGRAÇÃO ANTIGRAVITY KIT ---
def sync_antigravity_kit():
    """Baixa ou atualiza o Antigravity Kit do GitHub."""
    repo_url = "https://github.com/vudovn/antigravity-kit.git"
    if os.path.exists(ANTIGRAVITY_KIT_DIR):
        print(f"🔄 Atualizando Kit em {ANTIGRAVITY_KIT_DIR}...")
        try:
            repo = git.Repo(ANTIGRAVITY_KIT_DIR)
            repo.remotes.origin.pull()
        except Exception as e:
            print(f"⚠️ Erro ao atualizar kit: {e}")
    else:
        print(f"📥 Clonando Kit para {ANTIGRAVITY_KIT_DIR}...")
        git.Repo.clone_from(repo_url, ANTIGRAVITY_KIT_DIR)

# Inicializa Kit ao subir
sync_antigravity_kit()

# --- 3. CÉREBRO DO AGENTE (GLM) ---
class ChatMessage(BaseModel):
    role: str
    content: str
    
class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "glm-4-plus"

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint principal. Recebe mensagem do usuário, processa com o Kit
    e retorna a resposta do Agente.
    """
    
    # 1. Monta o Contexto do Sistema (System Prompt)
    # Lendo o Agente Principal do Kit (ex: orchestrator ou o próprio antigravity)
    sys_prompt = "Você é o NEXUS, um agente de IA avançado vivendo na VPS do Fabrício.\n"
    sys_prompt += "Você tem acesso total a um ambiente de desenvolvimento (workspace).\n"
    sys_prompt += "Sua missão é desenvolver apps, scripts e automações conforme solicitado.\n"
    
    # Injeta regras do Kit (exemplo simplificado - na real leríamos os arquivos .md)
    try:
        with open(f"{ANTIGRAVITY_KIT_DIR}/AGENTS.md", "r") as f:
            sys_prompt += f"\n\n--- REGRAS DO ANTIGRAVITY KIT ---\n{f.read()}"
    except:
        pass

    # 2. Prepara mensagens para o GLM
    glm_messages = [{"role": "system", "content": sys_prompt}]
    for msg in request.messages:
        glm_messages.append(msg.dict())

    # 3. Chama API do GLM
    headers = {
        "Authorization": f"Bearer {GLM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Mockando chamada real por enquanto (precisamos da URL exata do GLM 4)
    # response = requests.post("https://open.bigmodel.cn/api/paas/v4/chat/completions", ...)
    
    return {"reply": "Olá Fabrício! Sou o NEXUS. Já estou com o Antigravity Kit carregado na memória. O que vamos construir hoje?"}

# --- 4. FERRAMENTAS DE DESENVOLVIMENTO (VPS) ---

@app.post("/dev/create-file")
async def create_file(path: str, content: str):
    """Cria arquivos no workspace da VPS."""
    full_path = Path(WORKSPACE_DIR) / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)
    return {"status": "created", "path": str(full_path)}

@app.get("/dev/list-files")
async def list_files(path: str = "."):
    """Lista arquivos no workspace."""
    full_path = Path(WORKSPACE_DIR) / path
    if not full_path.exists():
        return []
    return [p.name for p in full_path.iterdir()]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
