import json
import os
from typing import Dict
import logging
import traceback
from pydantic import ValidationError
from elasticsearch import ElasticsearchException

from utils.date_utils import timestamp_to_iso, jst_now_str
from models import SearchRequests, SearchResponse
from connections import build_client
from exceptions import InvalidESDocumentError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

NG_WORDS = ["エロ", "R18", "R15", "えちえち", "エッチ", "BL", "ロリ"]
ES_INDEX_NAME = os.getenv('ES_INDEX_NAME')

def err(status_code: int, err_reason):
    traceback.print_exc()
    response_data = {
        "message": err_reason
    }
    return json.dumps(response_data),


def execute_search(es, params: Dict):
    limit = params['limit']
    response = es.search(
        index=ES_INDEX_NAME, 
        size=limit, 
        body={
            "query": {
                "bool": {
                    "must": [
                        {"bool": {"must_not": {"terms": {"description": NG_WORDS}}}},
                        {"bool": {"must_not": {"terms": {"title": NG_WORDS}}}}
                    ],
                    "filter": [
                        {"bool": {"must_not": {"term": {"genre": "BL"}}}},
                        {"bool": {"must_not": {"terms": {"tag": ["R15", "R18"]}}}}
                    ]
                }
            },
            "sort": {
                "_script" : {
                    "script" : "Math.random()",
                    # "lang" : "groovy",
                    "type" : "number"
                }
            }
        })
    return response


def extract_novels(response):
    try:
        novels = []
        for hit in response["hits"]["hits"]:
            hit_dict = hit["_source"]
            novel = {
                "title": hit_dict["title"],
                "author": hit_dict["author"],
                "url": hit_dict["url"],
                "site_name": hit_dict["site_name"],
                "genre": hit_dict["genre"],
                "updated_time": timestamp_to_iso(hit_dict["updated_time"] / 1000),
                "tag": [{"name": t} for t in hit_dict["tag"]]
            }
            novels.append(novel)
    except Exception as e:
        logger.error(f"DOCUMENT DATA ERROR,{e}")
        raise InvalidESDocumentError

    return novels


def create_response_data(response) -> Dict:
    total = response['hits']["total"]["value"]
    novels = extract_novels(response)
    ret = {
        "count": len(response["hits"]["hits"]), 
        "total": total,
        "novels": novels
    }
    return ret


def lambda_handler(event, context):
    """Search Web-novel Documents on Elasticsearch
    1. Validation Check Requests
    2. Search Document
    3. Transfrom Search Response to HTTP response data
    """
    try:
        request_json = event #.get_json()
        logger.info(f"Request parameters:{request_json}")
        parameters = SearchRequests(**request_json).dict()

        es = build_client()

        logger.info(f"BEGIN search, parameters:{parameters}")
        response = execute_search(es, parameters)
        logger.info("END search")
        
        logger.info(response)
        logger.info("Search results, total_count:{total}".format(
            total=response['hits']["total"]["value"]))
        response_data = create_response_data(response)
        response_data = SearchResponse(**response_data).dict()

        return response_data
    except ValidationError as e:
        logger.error(f"ValidationError:{e}")
        return err(400, f"Validation error:{e}")
    except ElasticsearchException as e:
        logger.error(f"ElasticsearchException:{e}")
        return err(500, "Database connection error")
    except InvalidESDocumentError as e:
        logger.error(f"InvalidESDocumentError:{e}")
        return err(500, "Internal Data error")
    except Exception:
        return err(500, "Unexpected error")
