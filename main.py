# Importação das bibliotecas necessárias
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do arquivo .env
# Este arquivo contém a chave da API do OpenAI e a URI do MongoDB
load_dotenv()

# Configuração da chave da API do OpenAI
# A chave é carregada a partir das variáveis de ambiente
openai.api_key = os.getenv("OPENAI_API_KEY")

# Conexão com o MongoDB
# A URI do MongoDB é carregada a partir das variáveis de ambiente
client = MongoClient(os.getenv("MONGO_URI"))
db = client.extremamente_aesthetic  # Nome do banco de dados
collection = db.texts  # Nome da coleção

# Inicialização do aplicativo FastAPI
app = FastAPI()

# Definição do modelo de dados para a entrada da API
# Este modelo espera um campo 'prompt' do tipo string
class TextPrompt(BaseModel):
    prompt: str

# Definição da rota POST para gerar texto
# A rota '/generate_text/' aceita um prompt e retorna um texto gerado pela IA
@app.post("/generate_text/")
async def generate_text(prompt: TextPrompt):
    try:
        # Chamada para a API do OpenAI para gerar um texto baseado no prompt fornecido
        response = openai.Completion.create(
            model="text-davinci-004",  # Modelo utilizado
            prompt=prompt.prompt,  # Prompt fornecido pelo usuário
            max_tokens=500  # Número máximo de tokens no texto gerado
        )
        text = response.choices[0].text.strip()  # Texto gerado pela IA

        # Armazenamento do prompt e do texto gerado no MongoDB
        result = collection.insert_one({"prompt": prompt.prompt, "text": text})

        # Retorno do texto gerado e do ID do documento no MongoDB
        return {"text": text, "id": str(result.inserted_id)}
    except Exception as e:
        # Tratamento de erros e retorno de uma mensagem de erro
        raise HTTPException(status_code=500, detail=str(e))

# Execução do servidor
# Este bloco é executado apenas se o script for executado diretamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
