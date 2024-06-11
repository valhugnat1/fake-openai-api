from typing import List, Optional
from pydantic import BaseModel
import time
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
import requests

ENDPOINT_TOKEN = "eqh1yJeycnzufbQ8FKO7Difuiudn6yK6MlKdMHkKkqvKcLFB-lyx8BvdaMaX_xI3iJOltfZY12Qb-uvP1V5tdQ"

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "mock-gpt-model"
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.1
    stream: Optional[bool] = False


class ChatCompletionRequestHF_chatui(BaseModel):
    model: str = "mock-gpt-model"
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.1
    top_p: Optional[float] = 0.95
    frequency_penalty: Optional[float] = 1.2
    stream: Optional[bool] = False
    stop: Optional[List]


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
    global ENDPOINT_TOKEN

    print("REQUEST : ", request.messages[-1])
    
    if request.messages and request.messages[len(request.messages)-1].role == 'user':
    #   resp_content = request.messages[0].content+" As a mock AI Assitant, I can only echo your last message:" #+ request.messages[-1].content

        response = requests.post(
            "https://free-mimas-rust-khi-4.dave.craft.ai/endpoints/product-llm-emulator-depl",
            # Endpoint inputs: Commented inputs are optional, uncomment them to use them.
            json={
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "user": request.messages[-1].role,
                "messages": {"text":request.messages[-1].content},
                "stream": request.stream,
                "top_p": 0,
                "model": request.model,
                "temperature": request.temperature,
            },
            headers={"Authorization": f"EndpointToken {ENDPOINT_TOKEN}"},
        )

        if not response.ok:
            raise Exception(response.status_code, response.text)
        
        resp_content = response.json()["outputs"]["choices"][len(response.json()["outputs"]["choices"])-1]["message"]["content"]

        print("RESPONSE : ", response.json()["outputs"]["choices"])

    else:
        resp_content = "As a mock AI Assitant, I can only echo your last message, but there were no messages!"

    resp_content = resp_content.replace("\n\n", "\n")

    print ("RETURN : ", resp_content)

    return {
        "id": "1337",
        "object": "chat.completion",
        "created": time.time(),
        "model": request.model,
        "choices": [{
            "message": ChatMessage(role="assistant", content=resp_content)
        }]
    }




@app.post("hf_chatui/chat/completions")
async def chat_completions(request: ChatCompletionRequestHF_chatui):
    global ENDPOINT_TOKEN

    print("REQUEST : ", request.messages[-1])
    
    if request.messages and request.messages[-1].role == 'user':
    #   resp_content = request.messages[0].content+" As a mock AI Assitant, I can only echo your last message:" #+ request.messages[-1].content


        response = requests.post(
            "https://free-mimas-rust-khi-4.dave.craft.ai/endpoints/product-llm-emulator-depl",
            # Endpoint inputs: Commented inputs are optional, uncomment them to use them.
            json={
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "user": request.messages[-1].role,
                "messages": {"text":request.messages[-1].content},
                "stream": request.stream,
                "top_p": 0,
                "model": request.model,
                "temperature": request.temperature,
            },
            headers={"Authorization": f"EndpointToken {ENDPOINT_TOKEN}"},
        )

        if not response.ok:
            raise Exception(response.status_code, response.text)
        
        resp_content = response.json()["outputs"]["choices"][-1]["message"]["content"]

        print("RESPONSE : ", response.json()["outputs"]["choices"])

    else:
        resp_content = "As a mock AI Assitant, I can only echo your last message, but there were no messages!"

    resp_content = resp_content.replace("\n\n", "\n")

    print ("RETURN : ", resp_content)

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