import requests

response = requests.post(
    "http://localhost:8000/api/v1/evaluate",
    json={"text": "What are the impacts of climate change on food?"}
    # json={"text": "Tell me about the transformer architecture in detail"}
    # json={"text": "What did we talk about transformer architecture just now?"}
    # json={"text": "summarize advancements in the field natural language processing on the year 2020"}
)
print(response.json())