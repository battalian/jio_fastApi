from typing import Optional

from pydantic import BaseModel


class Experiment(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    author_name: str
    tags: [str]
