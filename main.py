from typing import List, Optional
from pydantic import BaseModel
import time
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
import requests

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
    #   resp_content = request.messages[0].content+" As a mock AI Assitant, I can only echo your last message:" #+ request.messages[-1].content


        ENDPOINT_TOKEN = "XBQuxHax0-fWWPbF8HGvRzgPLMnKjDIZSYQ0Os1IU7EMBH26hRXnye6-X9a0oq7mgf18dKNgjJFVqLHJsL4K_w"

        response = requests.post(
            "https://clean-tarvos-burgundy-lambda-30.integration.craft.ai/endpoints/product-llm-emulator-depl",
            # Endpoint inputs: Commented inputs are optional, uncomment them to use them.
            json={
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "user": request.messages[0].role,
                "messages": {"text":request.messages[0].content},
                "stream": request.stream,
                "top_p": 0,
                "model": request.model,
                "temperature": request.temperature,
            },
            headers={"Authorization": f"EndpointToken {ENDPOINT_TOKEN}"},
        )

        if not response.ok:
            raise Exception(response.status_code, response.text)
        
        resp_content = response.json()["outputs"]["choices"][0]["message"]["content"]

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