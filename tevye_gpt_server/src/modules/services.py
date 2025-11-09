import os
import aiohttp

from abc import ABC, abstractmethod


class ServiceHandler(ABC):
    @abstractmethod
    async def request(self, service_request):
        ...


class ChatCompletion(ServiceHandler):
    async def request(self, service_request):
        url = os.getenv("OPENAI_API")
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=service_request) as resp:
                    response_data = await resp.json()
                    return response_data
            except Exception as e:
                return {"error": str(e)}
