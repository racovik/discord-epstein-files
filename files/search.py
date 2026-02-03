from typing import List
import httpx
from dataclasses import dataclass
import asyncio
import re
from urllib.parse import quote

BASE_URL = "https://www.justice.gov/multimedia-search"


@dataclass
class Source:
    document_id: str
    start_page: int
    end_page: int
    origin_file_name: str
    origin_file_uri: str
    bucket: str
    key: str
    content_type: str
    processed_at: str
    indexed_at: str
    source: str
    dataset: str


@dataclass
class Hit:
    source: Source
    content: str


headers = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0"
    ),
}


def _strip_html_regex(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def _process_hit_content(contents: dict) -> str:
    contents_ = "\n".join(contents)
    return _strip_html_regex(contents_)


def _get_dataset_from_uri(uri: str) -> str:
    dataset = uri.split("/")[-2]
    return dataset


def _process_hits(hit_data: dict) -> List[Hit]:
    hits_list = hit_data["hits"]["hits"]
    hits = []
    for hit in hits_list:
        source = hit["_source"]
        _source = Source(
            document_id=source["documentId"],
            start_page=source["startPage"],
            end_page=source["endPage"],
            origin_file_name=source["ORIGIN_FILE_NAME"],
            origin_file_uri=quote(source["ORIGIN_FILE_URI"], safe=":/"),
            bucket=source["bucket"],
            key=source["key"],
            content_type=source["contentType"],
            processed_at=source["processedAt"],
            indexed_at=source["indexedAt"],
            source=source["source"],
            dataset=_get_dataset_from_uri(source["ORIGIN_FILE_URI"]),
        )
        content = _process_hit_content(hit["highlight"]["content"])
        hits.append(
            Hit(
                source=_source,
                content=content,
            )
        )
    return hits


client = httpx.AsyncClient(headers=headers)


async def search(keys: str, page: int = 1) -> list[Hit]:
    params = {"keys": keys, "page": page}
    response = await client.get(url=BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()
    hits = _process_hits(data)
    return hits


if __name__ == "__main__":
    result = asyncio.run(
        search(
            "bolsonaro",
        )
    )
    for hit in result:
        print(
            f"{hit.source.document_id} | {hit.source.origin_file_name} | {hit.source.processed_at}\n{hit.content}\n\n"
        )
