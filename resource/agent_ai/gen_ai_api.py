from app.util.config import settings
import requests
import json


class GenAIAPI:
    def __init__(self, message: str):
        self.model = settings.GEN_AI_MODEL
        self.url = settings.GEN_AI_URL
        self.headers = {"Content-Type": "application/json"}
        self.message = message

    def send_prompt(self, question: str):
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.message},
                {"role": "user", "content": question}
            ],
            "stream": False
        }
        response = requests.post(self.url, headers=self.headers, data=json.dumps(data), stream=True)
        if response.status_code == 200:
            try:
                content = ""
                for chunk in response.iter_content(chunk_size=None):
                    if chunk:
                        parsed_chunk = chunk.decode('utf-8').replace("data: ", '"')
                        if parsed_chunk == "[DONE]":
                            break
                        try:
                            message = json.loads(parsed_chunk)
                            content += message.get("message", {}).get("content", "")
                        except Exception as e:
                            print(f"Error GenAI message: {e}")
                return content
            except json.JSONDecodeError as e:
                print(f"Decodification JSON Error: {e}")
        else:
            print(f"Error: {response.status_code}: {response.text}")
            return None