"""
Helper script for fetching RCFs by their number for testing purposes.
This script uses asyncio to fetch the content simultaneously.
"""

import asyncio
import datetime
import json
from pathlib import Path
from typing import Iterable

import httpx
from bs4 import BeautifulSoup

EXAMPLES = Path("bober/resources/examples")


async def fetch_rfc_metadata(rfc_number: int) -> dict:
    url = f"https://www.rfc-editor.org/rfc/rfc{rfc_number}.html"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        publication_date = soup.find(
            "meta", {"name": "citation_publication_date"}
        )["content"]
        publication_month, publication_year = publication_date.split(", ")

        # Convert the publication date to the desired format
        publication_date = datetime.datetime.strptime(
            f"{publication_month} 1, {publication_year}", "%B %d, %Y"
        ).strftime("%Y/%m/%d")

        metadata = {
            "num": rfc_number,
            "title": soup.find("meta", {"name": "citation_title"})["content"],
            "publish_at": publication_date,
            "authors": [
                author["content"]
                for author in soup.find_all("meta", {"name": "citation_author"})
            ],
        }

        return metadata


async def fetch_rfc(rfc_number: int) -> str:
    url = f"https://www.rfc-editor.org/rfc/rfc{rfc_number}.txt"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

        return response.text


async def main(rfc_range: Iterable[int]) -> None:
    for rfc_number in rfc_range:
        try:
            rfc_content = await fetch_rfc(rfc_number)
        except Exception as e:
            print(f"Error fetching RFC {rfc_number}: {e}")
            continue

        with open(EXAMPLES / "{rfc_number}.txt", "w") as f:
            f.write(rfc_content)


async def update_metadata(rfc_range: Iterable[int]):
    with open(EXAMPLES / "examples.json", "r") as f:
        metadata_list = json.load(f)

    for rfc_number in rfc_range:
        try:
            rfc_metadata = await fetch_rfc_metadata(rfc_number)
            metadata_list.append(rfc_metadata)
        except Exception as e:
            print(f"Error fetching RFC {rfc_number}: {e}")
            continue

    with open(EXAMPLES / "examples.json", "w") as f:
        json.dump(metadata_list, f, indent=2)


FAMOUS_RFCS = [
    826,
    951,
    2131,
    1034,
    1035,
    959,
    2068,
    792,
    791,
    1001,
    1002,
    1014,
    1057,
    1094,
    1813,
    977,
    821,
    822,
    768,
    793,
]

if __name__ == "__main__":
    asyncio.run(update_metadata(range(100, 200)))
