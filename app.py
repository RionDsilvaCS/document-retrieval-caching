from fastapi import FastAPI, UploadFile, Header, Depends, HTTPException
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from src.db import crud, models, schemas
from src.db.postgres import SessionLocal, engine
from src.db.chroma_db import SearchStore, UploadStore

load_dotenv()

models.Base.metadata.create_all(bind=engine)

class user_prompt(BaseModel):
    text: str | None = "<no-prompt>"    # user query
    top_k: int | None = 3               # return top k results found
    threshold: float | None = 0.3       # threshold for similarity

app = FastAPI()

search_engine = SearchStore()
upload_engine = UploadStore()

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
    Route to retrive data

    Args:
        prompt : user prompt
        user_id : user id from header

    Returns:
        "bot_message" : response from the search engine
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

    top_k_results, inference_time = search_engine.search_top_k(text=prompt.text, top_k=prompt.top_k, threshold=prompt.threshold)

    bot_message = {
        "top_k_results": top_k_results,
        "top_k": prompt.top_k,
        "threshold": prompt.threshold,
        "inference_time (secs)": inference_time
    }

    return { "bot_message": bot_message, "user_message": prompt, "user_info": user_id }