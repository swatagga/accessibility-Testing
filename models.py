import requests

api_key = "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"
url = "https://api.groq.com/v1/models"

headers = {
    "Authorization": f"Bearer {api_key}"
}

response = requests.get(url, headers=headers)
print(response.json())