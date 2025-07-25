import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.search import SearchParameters, x_source
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

client = Client(api_key=os.getenv("XAI_API_KEY"))

chat = client.chat.create(
    model="grok-4",
    search_parameters=SearchParameters(
        mode="auto",
        return_citations=True,
        sources=[x_source(included_x_handles=["arbitrum"])],
        from_date=datetime(2025, 1, 1),
        to_date=datetime(2025, 7, 23),
        max_search_results=30
        ),

)

system_prompt = """You are a blockchain research expert that is capable of analyzing protocol updates and you can reason about the impact of these updates on the blockchain ecosystem for the year 2025.

You will be given a blockchain name and you must use X and website sources to find the latest updates on the blockchain. 

These updates can be:
- Blockchain integrations with external protocols
- Mainnet updates
- Testnet updates
- Partnership announcements
- Product supports going live
- Media posts
- Ecosystem collaboration

You must then map these updates on a timeline in chronological order.

Give a chronological report of the updates for the year 2025. Only output the chronologically ordered list of updates, no other text.

Blockchain: {blockchain_name}
"""

# system_prompt = """Pull all tweets related to the integration of the input blockchain with eigenDA and succinct.
# You must then map these updates on a timeline in chronological order.

# Give a chronological report of the updates. Only output the chronologically ordered list of updates, no other text.

# Blockchain: {blockchain_name}
# """

chat.append(user(system_prompt.format(blockchain_name="Arbitrum")))

response = chat.sample()
print(response.content)
print(response.citations)