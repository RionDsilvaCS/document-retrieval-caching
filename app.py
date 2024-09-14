from fastapi import FastAPI, UploadFile, Header, Depends, HTTPException
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from src.db import crud, models, schemas
from src.db.postgres import SessionLocal, engine

load_dotenv()

models.Base.metadata.create_all(bind=engine)

class user_prompt(BaseModel):
    text: str | None = "<no-prompt>"    # user query
    top_k: int | None = 3               # return top k results found
    threshold: float | None = 0.5       # threshold for similarity

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# /health route
@app.get("/health/")
async def health():
    """__summary__
    Route to check if server is boot up

    Returns:
        JSON response
    """

    return {"Server Status": "Successfully running 🎉"}

# /search route
@app.post("/search/")
async def user_chat(prompt: user_prompt, db: Session = Depends(get_db), user_id: Annotated[str | None, Header(convert_underscores=False)] = None):
    """_summary_
    Route to chat with RAG Agent

    Args:
        prompt : user prompt
        user_id : user id from header

    Returns:
        "bot_message" : response from the RAG Agent
        "user_message" : prompt by the user
        "user_info" : header information of the user
    """

    if user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized enter user id")
    
    if prompt.text == "<no-prompt>":
        return { "bot_message": "prompt a valid query", "user_message": prompt, "user_info": user_id }
    
    if prompt.top_k <= 0 or prompt.top_k > 10:
        return { "bot_message": "invalid top k value", "user_message": prompt, "user_info": user_id }
    
    if prompt.threshold > 1.0 or prompt.threshold < 0.0:
        return { "bot_message": "invalid threshold value", "user_message": prompt, "user_info": user_id }
    
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        err = crud.create_user(db=db, user_id=user_id)
    else:
        if db_user.count > 4:
            raise HTTPException(status_code=429, detail=f"user id '{user_id}' 5 request limit has exhausted")
        err = crud.update_user_count(db=db, user_id=user_id)

    # Dummy response
    bot_message = {
        "message": "I am great 🎉",
        "top_k_results": [
            {
                "message": "I am great 🎉"
            },
            {
                "message": "I am fine"
            },
            {
                "message": "I am good"
            }
        ],
        "top_k": prompt.top_k,
        "threshold": prompt.threshold
    }

    return { "bot_message": bot_message, "user_message": prompt, "user_info": user_id }