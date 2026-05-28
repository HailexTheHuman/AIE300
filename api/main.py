import fastapi
import uvicorn
import pymongo
from dotenv import load_dotenv
import os
from pydantic import BaseModel
import requests as http_requests
from groq import Groq # first one the API worked for...
import json

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# from claude
class Item(BaseModel):
    name: str
    price: float
    
    

    def forward(self, x):
        return self.layer2(self.relu(self.layer1(x)))

app = fastapi.FastAPI()
mongo_url = os.getenv("DATABASE_URL")
mongo_client = pymongo.MongoClient(mongo_url)
mongo_db = mongo_client["aie_database"]
items_collection = mongo_db["items"]


class PredictionRequest(BaseModel):
    features: list[float]

if not mongo_url:
    raise RuntimeError("DATABASE_URL environment variable is not set")

def get_next_id():
    counter = mongo_db["counters"].find_one_and_update(
        {"_id": "item_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=pymongo.ReturnDocument.AFTER
    )
    return counter["seq"]

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/")
def read_items():
    try:
        items = list(items_collection.find({}, {"_id": 0}))
        return fastapi.responses.JSONResponse(status_code=200, content={"items": items})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/items/{item_id}")
def read_item(item_id: int):
    item = items_collection.find_one({"id": item_id}, {"_id": 0})
    if item is None:
        return fastapi.responses.JSONResponse(status_code=404, content={"error": "Item not found"})
    return fastapi.responses.JSONResponse(status_code=200, content={"item": item})

@app.post("/items/")
def create_item(item: Item):
    item_data = item.model_dump()
    item_data["id"] = get_next_id()
    try:
        items_collection.insert_one(item_data)
        created_item = items_collection.find_one({"id": item_data["id"]}, {"_id": 0})
        return fastapi.responses.JSONResponse(status_code=201, content={"item": created_item})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    item_data=item.model_dump()
    try:
        result = items_collection.update_one({"id": item_id}, {"$set": item_data})
        if result.matched_count == 0:
            return fastapi.responses.JSONResponse(status_code=404, content={"error": "Item not found"})
        updated_item = items_collection.find_one({"id": item_id}, {"_id": 0})
        return fastapi.responses.JSONResponse(status_code=200, content={"item_id": item_id, "item": updated_item})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    try:
        result = items_collection.delete_one({"id": item_id})
        if result.deleted_count == 0:
            return fastapi.responses.JSONResponse(status_code=404, content={"error": "Item not found"})
        return fastapi.responses.JSONResponse(status_code=200, content={"item_id": item_id, "status": "deleted"})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})



# @app.post("/predict")
@app.post("/predict")
def predict(req: PredictionRequest):
    try:
        response = http_requests.post(
            "http://model_service:8001/predict",
            json={"features": req.features}
        )
        return response.json()
    except Exception as e:
        return fastapi.responses.JSONResponse(
            status_code=500,
            content={"error": f"Model service error: {str(e)}"}
        )


class ChatRequest(BaseModel):
    message: str
    conversation_history: list = []

class ChatResponse(BaseModel):
    reply: str
    conversation_history: list

@app.post("/chat")
def chat(request: ChatRequest):
    messages = [
        {"role": "system", "content": "You are a helpful assistant for an item management and Iris flower classification app. Help users manage their items and understand Iris flower predictions. Be concise and helpful."}
    ]
    messages.extend(request.conversation_history)
    messages.append({"role": "user", "content": request.message})

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=512
        )
        reply = response.choices[0].message.content

        updated_history = request.conversation_history + [
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": reply}
        ]
        return ChatResponse(reply=reply, conversation_history=updated_history)

    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail=str(e))

class AnalyzeRequest(BaseModel):
    content: str

@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    system_prompt = """You are a data analysis assistant for an item management app.
Analyze the provided item description and respond with ONLY valid JSON in this exact format:
{
  "categories": ["category1", "category2"],
  "tags": ["tag1", "tag2", "tag3"],
  "sentiment": "positive" or "negative" or "neutral",
  "summary": "one sentence summary"
}
Do not include any text outside the JSON object. No markdown, no backticks."""

    few_shot = """Example:
Input: "Vintage leather wallet, brown color, good condition, priced at $45"
Output: {"categories": ["accessories", "vintage"], "tags": ["leather", "wallet", "brown"], "sentiment": "positive", "summary": "A well-priced vintage leather wallet in good condition."}

Now analyze this:
""" + request.content

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": few_shot}
            ],
            max_tokens=512,
            temperature=0.2
        )
        raw = response.choices[0].message.content.strip().strip("```json").strip("```").strip()
        result = json.loads(raw)

        required = ["categories", "tags", "sentiment", "summary"]
        for field in required:
            if field not in result:
                raise ValueError(f"Missing field: {field}")

        return result

    except json.JSONDecodeError:
        raise fastapi.HTTPException(status_code=422, detail="LLM returned invalid JSON. Try again.")
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail=str(e))


@app.on_event("shutdown")
def shutdown_event():
    mongo_client.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)