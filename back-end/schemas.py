from pydantic import BaseModel, HttpUrl
from typing import Optional


class URLParseRequest(BaseModel):
    url: HttpUrl


class URLParseResponse(BaseModel):
    original_url: str
    scheme: Optional[str]
    domain: Optional[str]
    port: Optional[str]
    path: Optional[str]
    query: Optional[str]
    fragment: Optional[str]
