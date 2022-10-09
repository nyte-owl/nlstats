from typing import List

from pydantic import BaseModel
from sqlalchemy import select

from log import get_logger
from ..database import get_session
from ..mappers import ConversionRule

logger = get_logger(__name__)


class ReadConversionRule(BaseModel):
    parsed_title: str
    final_title: str

    class Config:
        orm_mode = True


def read_all_conversion_rules() -> List[ReadConversionRule]:
    with get_session() as session:
        data = session.execute(select(ConversionRule)).scalars().all()

    return [ReadConversionRule.from_orm(item) for item in data]
