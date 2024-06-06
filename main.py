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


        ENDPOINT_TOKEN = "eqh1yJeycnzufbQ8FKO7Difuiudn6yK6MlKdMHkKkqvKcLFB-lyx8BvdaMaX_xI3iJOltfZY12Qb-uvP1V5tdQ"

        response = requests.post(
            "https://free-mimas-rust-khi-4.dave.craft.ai/endpoints/product-llm-emulator-depl",
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

    resp_content = "Once upon a time, in the crystal-clear waters of the Pacific Ocean, there lived a small, vibrant orange clownfish named Maris. Maris was a young, curious fish, who spent most of his days exploring the intricate coral reefs, playing with his friends, and learning about the wonders of the underwater world.\n\n     Maris lived with his family in a cozy, protective anemone called home, called Anemoneville. Anemoneville was nestled in a sheltered cove, surrounded by a vibrant array of colorful corals, and teeming with a variety of fascinating marine life. Maris loved exploring the reef, and he was always on the lookout for new adventures.\n\n     One sunny day, as Maris was out exploring the reef, he came across a group of butterflyfish, flitting gracefully through the water. They were collecting bright blue pearls from the coral, their dazzling tails leaving a trail of sparkling light in their wake. Maris watched in awe, wondering what the pearls were for.\n\n     One of the butterflyfish, a wise old female named Bianca, noticed Maris watching and swam over to him. \"Hello, little clownfish,\" she said, her voice like the gentle lapping of waves against the shore. \"What brings you to our pearl gathering today?\"\n\n     \"I've never seen anything like this before,\" Maris replied, his eyes wide with wonder. \"What are those beautiful pearls for?\"\n\n     Bianca smiled, her scales shimmering in the sunlight. \"The pearls are for our king, the majestic emperor angelfish,\" she explained. \"He lives in the heart of the reef, in a magnificent palace made of coral and shells. The pearls are offered as a token of respect and gratitude for the protection and abundance he provides for us all.\"\n\n     Maris was amazed, and he couldn't help but feel a twinge of envy. He longed to meet the emperor angelfish and offer him a pearl, to be a part of something so grand and magical.\n\n     Determined to make his dream a reality, Maris set out on a journey to the heart of the reef, to find the emperor angelfish and offer him a pearl. He braved the treacherous currents, darted through the dense schools of fish, and navigated the maze-like coral formations. Along the way, he encountered many challenges and made new friends, but he never lost sight of his goal.\n\n     Finally, after many days and nights, Maris arrived at the palace of the emperor angelfish. It was a breathtaking sight to behold, a towering structure of vibrant corals, teeming with life and color. Maris offered his pearl to the emperor, who graciously accepted it, his gaze full of warmth and appreciation.\n\n     Maris felt a deep sense of pride and accomplishment, and he knew that he had truly become a part of something special. He returned to Anemoneville with a newfound appreciation for the beauty and wonders of the underwater world, and he spent the rest of his days sharing the stories of his adventures with his family and friends.\n\n     And so, Maris the clownfish became a legend, a symbol of courage and determination, and a reminder that even the smallest of creatures can achieve great things. And the pearl he had offered to the emperor became a cherished reminder of the adventure of a lifetime."

    resp_content = resp_content.replace("\n\n", "\n")

    print (resp_content)

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