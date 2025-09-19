import os
import asyncio
from .google.genai._api_client import BaseApiClient
from .google.genai.client import AsyncClient
from .google.genai.errors import APIError


async def letsGo(modelName):
    try:
        baseClient = BaseApiClient(api_key=os.environ["GOOGLE_GENAI_API_KEY"])
        client = AsyncClient(api_client=baseClient)
    except KeyError:
        return 1000
    except Exception:
        return -1

    # check if model exists
    try:
        response = await client.models.generate_content(
            model=modelName,
            contents="Hello",
        )
    except APIError as e:
        if (e.code == 404):
            return 404


def main(modelName):
    return asyncio.run(letsGo(modelName))
