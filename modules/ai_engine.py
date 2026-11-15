import json
import os
import requests

CONFIG_FILE = "config.json"

class AIEngine:
    def __init__(self):
        self.config = self.load_config()

    def load_config(self) -> dict:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "active_provider": "openrouter",
            "active_model": "google/gemini-2.0-flash-exp:free",
            "keys": {
                "openrouter": "",
                "groq": "",
                "openai": "",
                "anthropic": ""
            }
        }

    def save_config(self, new_config: dict):
        self.config = new_config
        with open(CONFIG_FILE, "w") as f:
            json.dump(new_config, f, indent=4)

    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        provider = self.config.get("active_provider", "openrouter")
        model = self.config.get("active_model", "google/gemini-2.0-flash-exp:free")
        api_key = self.config.get("keys", {}).get(provider, "")

        if not api_key:
            return f"❌ Error: No API key provided for '{provider}'. Please go to Settings and enter your key."

        try:
            if provider == "openrouter":
                url = "https://openrouter.ai/api/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://zartostudios.local",
                    "X-Title": "Zartogrify"
                }
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                }
                res = requests.post(url, headers=headers, json=payload, timeout=45)
                res_data = res.json()
                if "error" in res_data:
                    return f"❌ OpenRouter API Error: {res_data['error'].get('message', res_data['error'])}"
                return res_data['choices'][0]['message']['content']

            elif provider == "groq":
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": model,
                    "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
                }
                res = requests.post(url, headers=headers, json=payload, timeout=30)
                res_data = res.json()
                if "error" in res_data:
                    return f"❌ Groq API Error: {res_data['error'].get('message', res_data['error'])}"
                return res_data['choices'][0]['message']['content']

            elif provider == "openai":
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": model,
                    "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
                }
                res = requests.post(url, headers=headers, json=payload, timeout=30)
                res_data = res.json()
                if "error" in res_data:
                    return f"❌ OpenAI API Error: {res_data['error'].get('message', res_data['error'])}"
                return res_data['choices'][0]['message']['content']

        except Exception as e:
            return f"❌ Connection Exception: {str(e)}"

        return "❌ Unsupported Provider selected."
