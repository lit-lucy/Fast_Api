from enum import Enum
from typing import Union

from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing_extensions import Annotated

app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


class RequestBody(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None


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
async def create_or_update_item(item_id: int, item: RequestBody, q: Union[str, None] = None):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result


@app.get("/items/")
async def read_items(q: Annotated[Union[str, None], Query(min_length=5, max_length=20)] = ...):
    results = {"items": fake_items_db}
    if q:
        results.update({"q": q})
    return results


@app.post("/items/")
async def create_item(item: RequestBody):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


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
