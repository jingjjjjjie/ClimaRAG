import requests

response = requests.post(
    "http://localhost:8000/api/v1/query",
    # json={"text": "What are the impacts of climate change on food?"}
    json={"text": "Tell me about the climate change in detail"}
    # json={"text": "Summarize advancements in the field of climate change on the year 2020"}
    # json={"text": "What did we talk about climate change just now?"}
)
print(response.json())