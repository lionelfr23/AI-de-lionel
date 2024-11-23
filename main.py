from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import openai

# Configura tu API Key
openai.api_key = "TU_API_KEY_AQUÍ"

# Configuración de la base de datos
DATABASE_URL = "sqlite:///./conversations.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de la base de datos
class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)

Base.metadata.create_all(bind=engine)

# Inicializa la app FastAPI
app = FastAPI()

# Modelo para solicitudes
class Message(BaseModel):
    message: str

@app.post("/chat")
async def chat(message: Message):
    user_message = message.message

    # Respuesta programada para el creador
    if "quién te creó" in user_message.lower() or "quién es tu creador" in user_message.lower():
        response_text = "Lionel Edersson Aragos Illanes"
    else:
        # Genera respuesta con OpenAI
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Eres una IA poderosa, profesional y amigable."},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=200,
                temperature=0.7
            )
            response_text = response["choices"][0]["message"]["content"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al conectar con OpenAI: {str(e)}")

    # Guarda la conversación en la base de datos
    db = SessionLocal()
    new_conversation = Conversation(user_message=user_message, bot_response=response_text)
    db.add(new_conversation)
    db.commit()
    db.close()

    return {"response": response_text}

@app.get("/history")
def get_history():
    # Devuelve el historial de conversaciones
    db = SessionLocal()
    conversations = db.query(Conversation).all()
    db.close()
    return [{"user_message": c.user_message, "bot_response": c.bot_response} for c in conversations]
