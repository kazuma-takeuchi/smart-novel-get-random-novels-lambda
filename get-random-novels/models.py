from typing import Dict, List
from datetime import date, datetime

from pydantic import BaseModel, validator
from elasticsearch_dsl import FacetedSearch, TermsFacet

from utils.date_utils import get_today, relative_date

ALIAS = "smart-novel"


class NovelFacetedSearch(FacetedSearch):
    index = ALIAS
    # fields that should be searched
    fields = ['description']

    facets = {
        # use bucket aggregations to define facets
        'tag': TermsFacet(field='tag.keyword', size=20),
        # timezoneが怪しいので削除
        # 'created_at': DateHistogramFacet(field='created_at', interval='day', format="%Y-%m-%d"),
    }

    def highlight(self, search):
        s = search.highlight('description', fragment_size=300)
        return s


class FiltersModel(BaseModel):
    tag: List[str] = []


class DateModel(BaseModel):
    from_: datetime = relative_date(get_today(), days=-30)
    to: datetime = get_today()

    @validator('to', always=True)
    def to_larger_than_from(cls, v, values, **kwargs):
        if 'from_' in values and v < values['from_']:
            raise ValueError('from:{f} must be smaller than to:{t}'.format(
                f=values['from_'],
                t=v
            ))
        return v

    class Config:
        fields = {
            'from_': 'from'
        }


class SearchRequests(BaseModel):
    limit: int = 10
    


class SearchResponse(BaseModel):
    count: int
    total: int
    novels: List[Dict]


if __name__ == "__main__":

    pass
