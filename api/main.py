
import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import git
from pathlib import Path
from dotenv import load_dotenv
from zhipuai import ZhipuAI # Biblioteca Oficial GLM

# Carrega ambiente
load_dotenv()

app = FastAPI(title="NEXUS Agent API", version="1.0.0")

# --- 1. CONFIGURAÇÃO GERAL ---
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "./workspace")
ANTIGRAVITY_KIT_DIR = os.getenv("KIT_DIR", "./antigravity-kit")
GLM_API_KEY = os.getenv("GLM_API_KEY", "")

# Verifica se a chave existe, senão avisa
if not GLM_API_KEY:
    print("⚠️  AVISO: GLM_API_KEY não encontrada no ambiente!")

# Inicializa Cliente GLM
client = ZhipuAI(api_key=GLM_API_KEY)

# --- 2. INTEGRAÇÃO ANTIGRAVITY KIT ---
def get_antigravity_context():
    """Lê os arquivos essenciais do Kit para dar contexto ao Agente."""
    context = ""
    # Tenta ler o AGENTS.md se existir
    try:
        ag_path = Path(ANTIGRAVITY_KIT_DIR) / "AGENTS.md"
        if ag_path.exists():
            context += f"\n\n--- [CONTEXTO: AGENTS.md] ---\n{ag_path.read_text('utf-8')[:2000]}" # Limita a 2000 chars pra não estourar
    except Exception as e:
        print(f"Erro lendo contexto: {e}")
    return context

def sync_antigravity_kit():
    repo_url = "https://github.com/vudovn/antigravity-kit.git"
    if os.path.exists(ANTIGRAVITY_KIT_DIR):
        try:
            repo = git.Repo(ANTIGRAVITY_KIT_DIR)
            repo.remotes.origin.pull()
        except: pass
    else:
        try:
            git.Repo.clone_from(repo_url, ANTIGRAVITY_KIT_DIR)
        except: pass

sync_antigravity_kit()

# --- 3. CÉREBRO DO AGENTE (GLM REAL) ---
class ChatMessage(BaseModel):
    role: str
    content: str
    
class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "glm-4-flash" # Modelo rápido e barato

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not GLM_API_KEY:
        return {"reply": "⚠️ Erro: GLM_API_KEY não configurada no servidor (.env)."}

    # 1. Monta System Prompt com Contexto do Kit
    kit_context = get_antigravity_context()
    sys_prompt = "Você é o NEXUS, um agente de IA avançado vivendo na VPS do Fabrício.\n"
    sys_prompt += "Você tem acesso total a um ambiente de desenvolvimento (workspace).\n"
    sys_prompt += "Seja direto, técnico quando necessário, e parceiro.\n"
    sys_prompt += kit_context # Injeta o conhecimento do kit

    # 2. Prepara histórico
    glm_messages = [{"role": "system", "content": sys_prompt}]
    for msg in request.messages:
        glm_messages.append(msg.dict())

    try:
        # 3. CHAMA A IA DE VERDADE
        response = client.chat.completions.create(
            model=request.model,
            messages=glm_messages,
            stream=False,
        )
        
        reply_content = response.choices[0].message.content
        return {"reply": reply_content}

    except Exception as e:
        print(f"Erro GLM: {e}")
        return {"reply": f"⚠️ Erro ao processar no GLM: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
