import os
import asyncio
import markdown as md
from .google.genai._api_client import BaseApiClient
from .google.genai.client import AsyncClient
from .google.genai.errors import APIError

rate_limit_event = asyncio.Event()
rate_limit_event.set()  # Start in the "GO" state.

# asynchronously creating API calls with semaphore
async def call_api(client, item, semaphore, event, modelName):
    async with semaphore:

        tries = 0
        while True:
            await event.wait()

            # if a word gets an error the third time then something is really wrong, skipping it.
            # this once happened when I was testing the script. For some reason RESOURCE EXHAUSTED error was popping up
            # after every break of 90 seconds, which shouldn't be the case. Guess it was a period of high demand on Google servers
            if tries > 2:
                return

            try:
                tries += 1

                response = await client.models.generate_content(
                    model=modelName,
                    contents=f"Define the word or phrase: {item}. Explain how it differs from its synonyms.",
                )
                return (item, response.text)  # Success!
            except APIError:
                # this word encountered an error (usually RESOURCE EXHAUSTED) which means we run out of quota for this minute and this model
                # setting a flag to stop the calls if not set already, continuing calling after 75 seconds
                if event.is_set():
                    event.clear()
                    await asyncio.sleep(75)
                    event.set()

            except Exception:
                # something unexpected happened, skipping this word
                return


async def letsGo(items, concurrencyLimit, modelName):
    try:
        baseClient = BaseApiClient(api_key=os.environ["GOOGLE_GENAI_API_KEY"])
        client = AsyncClient(api_client=baseClient)
    except Exception:
        return []

    semaphore = asyncio.Semaphore(concurrencyLimit)

    tasks = [call_api(client, item, semaphore, rate_limit_event, modelName) for item in items]

    results = await asyncio.gather(*tasks)

    # Filter out the None values from tasks that failed or were stopped and convert markdown into HTML
    results = [
        (res[0], md.markdown(res[1]).replace("\n", ""))
        for res in results
        if res is not None
    ]

    return results


def main(items, modelName, concurrencyLimit):
    results = asyncio.run(letsGo(items, concurrencyLimit, modelName))
    return results
