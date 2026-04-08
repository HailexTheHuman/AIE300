import fastapi
import uvicorn

app = fastapi.FastAPI()

items_db: dict[int, dict] = {}
next_id = 1

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/")
def read_items():
    return fastapi.responses.JSONResponse(status_code=200, content={"items": list(items_db.values())})

@app.get("/items/{item_id}")
def read_item(item_id: int):
    item = items_db.get(item_id)
    if item is None:
        return fastapi.responses.JSONResponse(status_code=404, content={"error": "Item not found"})
    return fastapi.responses.JSONResponse(status_code=200, content={"item": item})

@app.post("/items/")
def create_item(item: dict):
    global next_id
    item["id"] = next_id
    items_db[next_id] = item
    next_id += 1
    return fastapi.responses.JSONResponse(status_code=201, content={"item": item})

@app.put("/items/{item_id}")
def update_item(item_id: int, item: dict):
    if item_id not in items_db:
        return fastapi.responses.JSONResponse(status_code=404, content={"error": "Item not found"})
    items_db[item_id].update(item)
    return fastapi.responses.JSONResponse(status_code=200, content={"item_id": item_id, "item": items_db[item_id]})

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id not in items_db:
        return fastapi.responses.JSONResponse(status_code=404, content={"error": "Item not found"})
    del items_db[item_id]
    return fastapi.responses.JSONResponse(status_code=200, content={"item_id": item_id, "status": "deleted"})

@app.get("/docs/")
def get_docs():
    return fastapi.responses.JSONResponse(status_code=200, content={"docs": "API documentation",
            "endpoints": [
                {"method": "GET", "path": "/items/"},
                {"method": "GET", "path": "/items/{item_id}"},
                {"method": "POST", "path": "/items/"},
                {"method": "PUT", "path": "/items/{item_id}"},
                {"method": "DELETE", "path": "/items/{item_id}"}
            ]})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)