from datetime import datetime, time, timedelta
from enum import Enum
from typing import Union, List, Dict, Any
from uuid import UUID

from fastapi import FastAPI, Query, Path, Body, Cookie, Header
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing_extensions import Annotated

app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: Union[str, None] = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: Union[float, None] = None
    images: Union[List[Image], None] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
                "images": [
                    {
                        "url": "http://example.com/baz.jpg",
                        "name": "The Foo live"
                    },
                    {
                        "url": "http://example.com/dave.jpg",
                        "name": "The Baz"
                    }
                ]
            }
        }


class Offer(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    items: List[Item]


class User(BaseModel):
    username: str
    full_name: Union[str, None] = None


class BaseUser(BaseModel):
    username: str
    email: EmailStr
    full_name: Union[str, None] = None


class UserIn(BaseUser):
    password: str


class ItemType(str, Enum):
    food = "food"
    drink = "drink"
    other = "other"


@app.get("/")
async def read_root():
    return {"Hello": "Items"}


@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer


@app.post("/images/multiple")
async def create_multiple_images(images: List[Image]):
    for image in images:
        image.url = image.url + " is nice"
    return images


# Accept any dict as long as it has int keys and values of float type
@app.post("/index-weights/")
async def create_index_weights(weights: Dict[int, float]):
    return weights


@app.post("/user/")
async def create_user(user: UserIn) -> BaseUser:
    return user


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


@app.get("/items/{item_id}", response_model=Item, response_model_exclude_unset=True)
async def read_item(
        size: Annotated[float, Query(gt=0, lt=10.5)],
        # gt: greater than, le: less than or equal
        item_id: Annotated[int, Path(title="The ID of the item to get", gt=0, le=1000)],
        q: Annotated[Union[str, None], Query(alias="item-query")] = None

):
    results = {"item_id": item_id, "size": size}
    if q:
        results.update({"q": q})
    return results


# "importance" parameter will be added to request body
@app.put("/items/{item_id}")
async def create_or_update_item(
        item_id: UUID,
        start_datetime: Annotated[Union[datetime, None], Body()] = None,
        end_datetime: Annotated[Union[datetime, None], Body()] = None,
        repeat_at: Annotated[Union[time, None], Body()] = None,
        process_after: Annotated[Union[timedelta, None], Body()] = None,
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "repeat_at": repeat_at,
        "process_after": process_after,
        "start_process": start_process,
        "duration": duration
    }


# embed=True will include "item" in the schema in the request body
@app.put("/items/{item_id}/without_user")
async def update_item(item_id: int, item: Annotated[Item, Body(embed=True)]):
    results = {"item_id": item_id, "item": item}
    return results


@app.get("/items/", response_model=List[Item])
async def read_items(
        q: Annotated[Union[List[str], None],
        Query(title="Query list", description="Takes several queries, min length validation "
                                              "only works in OpenAPI",
              alias="item-query-list", deprecated=True, min_length=2)] = ["item1", "item2"],
        ads_id: Annotated[Union[str, None], Cookie()] = None,
        user_agent: Annotated[Union[str, None], Header()] = None,
        x_token: Annotated[Union[List[str], None], Header()] = None
) -> Any:
    results = {"items": fake_items_db, "ads_id": ads_id, "User-Agent": user_agent, "X-Token values": x_token}
    if q:
        results.update({"q": q})
    return [
        Item(name="Portal Gun", price=42.0),
        Item(name="Pure", price=39.0),
    ]


@app.post("/items/", response_model=Item)
async def create_item(item: Item) -> Any:
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item


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
