from __future__ import annotations

import asyncio
import json
import logging
import re
from collections import OrderedDict
from typing import Awaitable, Callable, Iterable

from openai import AsyncOpenAI
from openai import OpenAIError


logger = logging.getLogger(__name__)


StopChecker = Callable[[], Awaitable[bool]]


class OpenAIService:
    """
    Обертка над AsyncOpenAI для генерации SEO-фраз.
    Поддерживает несколько API-ключей и параллельные запросы.
    """

    def __init__(self, api_keys: Iterable[str]):
        self.clients = [AsyncOpenAI(api_key=key) for key in api_keys]
        if not self.clients:
            raise ValueError("Не заданы API-ключи OpenAI")

    async def generate_phrases(
        self,
        topic: str,
        keywords: str,
        count: int,
        stop_check: StopChecker | None = None,
    ) -> list[str]:
        """
        Возвращает не более `count` фраз. Умеет останавливаться, если stop_check=True,
        и прекращает работу при фатальных ответах API (например, региональные ограничения).
        """
        output: list[str] = []
        lock = asyncio.Lock()
        abort_event = asyncio.Event()

        prompt = [
            {
                "role": "system",
                "content": (
                    "I want you to act as an SEO semantic core phrase generator.\n"
                    "Answer only with JSON array format, without any keys, just the array.\n"
                    "Do not provide explanations.\n"
                    "Generate low-frequency key phrases for the topic. Each phrase should contain "
                    "between 4 to 12 words and be between 12 to 120 characters in length.\n"
                ),
            },
            {"role": "user", "content": f"Topic: {topic}.\nKeywords: {keywords}."},
        ]

        async def worker(client: AsyncOpenAI):
            nonlocal output
            while len(output) < count and not abort_event.is_set():
                if stop_check and await stop_check():
                    abort_event.set()
                    break
                try:
                    phrases = await self._request_phrases(client, prompt)
                except UnsupportedRegionError as exc:
                    abort_event.set()
                    raise exc
                except Exception as exc:  # pragma: no cover - сетевые ошибки
                    logger.error("OpenAI request failed: %s", exc)
                    if stop_check and await stop_check():
                        abort_event.set()
                        break
                    await asyncio.sleep(1)
                    continue

                async with lock:
                    for phrase in phrases:
                        if phrase not in output and len(output) < count:
                            output.append(phrase)

                # небольшая пауза, чтобы не спамить API
                await asyncio.sleep(0.2)

        tasks = [asyncio.create_task(worker(client)) for client in self.clients]
        try:
            await asyncio.gather(*tasks)
        finally:
            abort_event.set()
            for t in tasks:
                if not t.done():
                    t.cancel()

        return output[:count]

    async def _request_phrases(
        self, client: AsyncOpenAI, messages: list[dict]
    ) -> list[str]:
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=2000,
                temperature=1,
                top_p=1,
                frequency_penalty=0.1,
                presence_penalty=0.1,
            )
        except OpenAIError as exc:  # pragma: no cover - зависимость от внешнего API
            msg = str(exc)
            if "unsupported_country_region_territory" in msg:
                raise UnsupportedRegionError(msg)
            raise

        content = response.choices[0].message.content or ""
        return self._parse_response(content)

    @staticmethod
    def _parse_response(raw: str) -> list[str]:
        """
        Пытаемся распарсить JSON массив, иначе возвращаем список строк.
        """
        cleaned = raw.replace("```", "").replace("json", "").strip()

        # Попытка json.loads
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except json.JSONDecodeError:
            pass

        # fallback: делим по запятым/строкам и убираем кавычки/скобки
        cleaned = re.sub(r"[\\[\\]]", "", cleaned)
        parts = re.split(r",|\\n", cleaned)
        normalized = [part.strip().strip('"').strip("'") for part in parts if part.strip()]
        # удаляем дубликаты, сохраняя порядок
        return list(OrderedDict.fromkeys(normalized))


class UnsupportedRegionError(RuntimeError):
    """Возникает, если OpenAI вернул ограничение по региону."""
