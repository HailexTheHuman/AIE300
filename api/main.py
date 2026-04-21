import fastapi
import uvicorn
import pymongo
from dotenv import load_dotenv
import os
from pydantic import BaseModel

load_dotenv()

# from claude
class Item(BaseModel):
    name: str
    price: float

app = fastapi.FastAPI()
mongo_url = os.getenv("DATABASE_URL")
mongo_client = pymongo.MongoClient(mongo_url)
mongo_db = mongo_client["aie_database"]
items_collection = mongo_db["items"]

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

@app.on_event("shutdown")
def shutdown_event():
    mongo_client.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)