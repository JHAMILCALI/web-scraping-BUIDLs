from __future__ import annotations

from pathlib import Path
import random
import time

from playwright.sync_api import sync_playwright

URL = "https://dorahacks.io/hackathon/boring-ai/hackers"
API_TEMPLATE = "https://dorahacks.io/api/hackathon/boring-ai/hackers/?page={page}&page_size={page_size}"
OUTPUT_FILE = Path("hackers_buidl_submitted.txt")
MIN_DELAY_SECONDS = 2.0
MAX_DELAY_SECONDS = 5.0
MAX_RETRIES = 3
BLOCKING_STATUS_CODES = {403, 429}


def _extract_username(item: dict) -> str | None:
    hacker = item.get("hacker") or {}
    username = (hacker.get("username") or "").strip()
    return username or None


def _extract_buidl_url(item: dict) -> str | None:
    submitted_buidl = item.get("submitted_buidl") or {}
    buidl_id = submitted_buidl.get("id")
    if not buidl_id:
        return None
    return f"https://dorahacks.io/buidl/{buidl_id}"


def _sleep_between_requests() -> None:
    delay = random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)
    time.sleep(delay)


def _fetch_page_with_backoff(page, api_url: str):
    for attempt in range(1, MAX_RETRIES + 1):
        _sleep_between_requests()
        response = page.request.get(api_url, timeout=90_000)

        if response.status == 200:
            text = response.text()
            if "Human Verification" in text:
                return None
            return response

        if response.status in BLOCKING_STATUS_CODES and attempt < MAX_RETRIES:
            backoff_seconds = 2 ** attempt
            time.sleep(backoff_seconds)
            continue

        return None
    return None


def extract_hackers_with_submitted_buidl() -> list[tuple[str, str]]:
    with sync_playwright() as p:
        # Headed mode avoids anti-bot blocks observed in this page.
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=90_000)
        page.wait_for_load_state("networkidle", timeout=90_000)
        page.wait_for_timeout(8_000)

        rows: list[tuple[str, str]] = []
        page_number = 1
        page_size = 50

        while True:
            api_url = API_TEMPLATE.format(page=page_number, page_size=page_size)
            response = _fetch_page_with_backoff(page, api_url)
            if response is None:
                break

            payload = response.json()
            items = payload.get("results") or []
            if not items:
                break

            for item in items:
                username = _extract_username(item)
                buidl_url = _extract_buidl_url(item)
                if username and buidl_url:
                    rows.append((username, buidl_url))

            if not payload.get("next"):
                break
            page_number += 1

        browser.close()

    unique_rows: list[tuple[str, str]] = []
    seen = set()
    for username, buidl_url in rows:
        if not username or not buidl_url:
            continue
        key = (username, buidl_url)
        if key in seen:
            continue
        unique_rows.append(key)
        seen.add(key)
    return unique_rows


def main() -> None:
    rows = extract_hackers_with_submitted_buidl()
    output_lines = [f"{username} | {buidl_url}" for username, buidl_url in rows]
    OUTPUT_FILE.write_text("\n".join(output_lines), encoding="utf-8")
    print(f"Total con BUIDL Submitted: {len(rows)}")
    print(f"Archivo generado: {OUTPUT_FILE.resolve()}")
    for line in output_lines:
        print(line)


if __name__ == "__main__":
    main()
