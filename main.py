from typing import List, Optional

from pydantic import BaseModel

import time

from fastapi import FastAPI, Request

from starlette.middleware.base import BaseHTTPMiddleware


class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "mock-gpt-model"
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.1
    stream: Optional[bool] = False

# Middleware to log requests with incorrect paths
class LogIncorrectPathsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if response.status_code == 404:
            # Log the request path and other details
            print(f"Incorrect endpoint path: {request.url.path}, Method: {request.method}")
            # You can add more logging details if needed
        return response


app = FastAPI(title="OpenAI-compatible API")

app.add_middleware(LogIncorrectPathsMiddleware)

@app.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):

    print(request)
    
    if request.messages and request.messages[0].role == 'user':
      resp_content = request.messages[-1].content+" As a mock AI Assitant, I can only echo your last message:" #+ request.messages[-1].content
    else:
      resp_content = "As a mock AI Assitant, I can only echo your last message, but there were no messages!"

    return {
        "id": "1337",
        "object": "chat.completion",
        "created": time.time(),
        "model": request.model,
        "choices": [{
            "message": ChatMessage(role="assistant", content=resp_content)
        }]
    }

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}