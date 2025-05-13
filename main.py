import asyncio
import os
import time
from pathlib import Path

import requests
from pyppeteer import launch
from pyppeteer.page import Page

from models.search_result import SearchResult


def download_video(url: str, file_name: str, folder_name: str) -> None:
    base_dir = Path(f"./downloads/{folder_name}")
    os.makedirs(base_dir, exist_ok=True)

    response = requests.get(url, stream=True)
    file_size = int(response.headers["Content-Length"])
    downloaded = 0
    with open(base_dir / f"{file_name}.mp4", "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            downloaded += len(chunk)
            print(
                f"Downloaded {downloaded / 1048576:0,.2f}/{file_size / 1048576:0,.2f} MB"
            )
            f.write(chunk)


async def find_buttons_and_download(page: Page, download_page: Page, anime_name: str):
    buttons = await page.querySelectorAll(".episode-item a")
    episodes_amount = len(buttons)
    print(f"Found {episodes_amount} episodes.")

    for index, button in enumerate(buttons):
        await button.click()
        time.sleep(1)

        print(page.url)

        await page.waitForSelector("#embed")
        video_page_url = await page.evaluate(
            """() => {
                const videoElement = document.querySelector("#embed");
                return videoElement ? videoElement.getAttribute("src") : null;
            }"""
        )

        await download_page.goto(video_page_url)
        video_url = await download_page.evaluate("""() => window.downloadUrl""")
        download_video(
            url=video_url,
            file_name=f"{anime_name} - {index + 1}",
            folder_name=anime_name,
        )

        print(f"Downloaded episode {index + 1} of {episodes_amount}")


async def main():
    browser = await launch(options={"headless": True})
    page = await browser.newPage()
    await page.goto("https://www.animeunity.so/")
    csrf_token = await page.evaluate(
        """() => {
            const csrfToken = document.querySelector('meta[name="csrf-token"]');
            return csrfToken ? csrfToken.getAttribute("content") : null;
        }"""
    )
    page_cookies = await page.cookies()
    page_cookies = {cookie["name"]: cookie["value"] for cookie in page_cookies}

    anime_name = input("Anime name: ")
    response = requests.post(
        "https://www.animeunity.so/livesearch",
        data={"title": anime_name},
        headers={
            "x-csrf-token": csrf_token,
            "x-xsrf-token": page_cookies["XSRF-TOKEN"],
        },
        cookies=page_cookies,
    )

    search_result = SearchResult.model_validate_json(response.text)
    if not search_result.records:
        print("No results found.")
        return

    print(f"Found {len(search_result.records)} results.")
    print("Which one do you want to download?")
    for index, record in enumerate(search_result.records):
        print(f"{index + 1}: {record.title_eng}")
    selected_index = (
        int(input("Enter the number of the anime you want to download: ")) - 1
    )
    if selected_index < 0 or selected_index >= len(search_result.records):
        print("Invalid selection.")
        return
    print(f"Selected: {search_result.records[selected_index].title_eng}")

    anime_name = search_result.records[selected_index].title_eng

    await page.goto(
        f"https://www.animeunity.so/anime/{search_result.records[0].id}-{search_result.records[0].slug}",
        {"waitUntil": "networkidle0"},
    )

    button_groups = await page.querySelectorAll(".btn-episode-nav")

    download_page = await browser.newPage()
    if len(button_groups) > 0:
        for index, button_group in enumerate(button_groups):
            await button_group.click()
            time.sleep(1)

            await find_buttons_and_download(
                page=page,
                download_page=download_page,
                anime_name=anime_name,
            )

    else:
        await find_buttons_and_download(
            page=page,
            download_page=download_page,
            anime_name=anime_name,
        )

    await browser.close()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

# https://www.animeunity.so/livesearch
