from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="My FastAPI App", version="1.0")

# Sample data model
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    in_stock: bool

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}

# Example GET endpoint
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "message": "This is a GET request"}

# Example POST endpoint
@app.post("/items/")
def create_item(item: Item):
    return {"message": "Item created successfully", "item": item}

# Example health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}
