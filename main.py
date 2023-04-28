from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum

app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


class ItemType(str, Enum):
    food = "food"
    drink = "drink"
    other = "other"


@app.get("/")
async def read_root():
    return {"Hello": "Items"}


@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}


@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
        user_id: int, item_id: str, q: Union[str, None] = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "Long long long long long long description"}
        )
    return item


@app.get("/items/{item_id}")
async def read_item(item_id: str, needy: str, skip: int = 0, q: Union[str, None] = None, short: bool = False):
    item = {"item_id": item_id, "skip": skip, "needy": needy}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "Long long long long long long description"})
    return item


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_price": item.price, "item_id": item_id}


@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return fake_items_db[skip: skip + limit]


@app.get("/types/{item_type}")
async def get_item_types(item_type: ItemType):
    if item_type == ItemType.food:
        return {"item_type": item_type, "message": "Food is food"}
    elif item_type == ItemType.drink:
        return {"item_type": item_type, "message": "Drink is drink"}
    return {"item_type": item_type, "message": "Something else is something else"}


# Declaring a path parameter containing a path
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    read_root()

