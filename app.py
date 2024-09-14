from fastapi import FastAPI, UploadFile, Header
from pydantic import BaseModel
from typing import Annotated

class user_prompt(BaseModel):
    text: str | None = "<no-prompt>"    # user query
    top_k: int | None = 3               # return top k results found
    threshold: float | None = 0.5       # threshold for similarity

app = FastAPI()

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
async def user_chat(prompt: user_prompt, user_id: Annotated[str | None, Header(convert_underscores=False)] = None):
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

    if prompt.text == "<no-prompt>":
        return { "bot_message": "prompt a valid query", "user_message": prompt, "user_info": user_id }
    
    if prompt.top_k <= 0 or prompt.top_k > 10:
        return { "bot_message": "invalid top k value", "user_message": prompt, "user_info": user_id }
    
    if prompt.threshold > 1.0 or prompt.threshold < 0.0:
        return { "bot_message": "invalid threshold value", "user_message": prompt, "user_info": user_id }
    
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