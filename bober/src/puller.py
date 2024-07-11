"""
Helper script for fetching RCFs by their number for testing purposes.
This script uses asyncio to fetch the content simultaneously.
"""

import asyncio
from typing import Iterable

import httpx


async def fetch_rfc(rfc_number: int) -> str:
    url = f"https://www.rfc-editor.org/rfc/rfc{rfc_number}.txt"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

        return response.text


def print_rfc_head(number: int, content: str, top: int) -> None:
    print(f"Fetched RFC {number}:")
    print("------------------------")
    lines = content.lstrip().splitlines()
    for i, line in enumerate(lines[:top], start=1):
        print(f"{i}:\t {line}")
    print("...")
    print(f"printed {top}/{len(lines)} lines")
    print("")


async def main(rfc_range: Iterable[int]) -> None:
    for rfc_number in rfc_range:
        try:
            rfc_content = await fetch_rfc(rfc_number)
        except Exception as e:
            print(f"Error fetching RFC {rfc_number}: {e}")
            continue

        with open(f"examples/{rfc_number}.txt", "w+") as f:
            f.write(rfc_content)
        # print_rfc_head(rfc_number, rfc_content, top)


if __name__ == "__main__":
    asyncio.run(main(range(1, 20)))
