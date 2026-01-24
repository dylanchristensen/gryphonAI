
import json
import urllib.request
import urllib.error
import time

class LLMInterface:
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager

    def _get_api_key(self):
        return self.settings_manager.get_setting("llm_api_key")

    def _get_model(self):
        return self.settings_manager.get_setting("llm_model") or "google/gemma-2-9b-it:free"

    def _call_openai(self, system_prompt, user_prompt):
        api_key = self._get_api_key()
        if not api_key:
            return {"error": "API Key not configured."}

        base_url = self.settings_manager.get_setting("llm_base_url")
        if not base_url or not base_url.strip():
            base_url = "https://openrouter.ai/api/v1"
        
        # Ensure base_url doesn't end with slash if we're appending /chat/completions
        # But commonly users might provide the full base like http://localhost:11434/v1
        # Let's assume standard OpenAI compatible endpoint structure: base + /chat/completions
        if base_url.endswith("/"):
            base_url = base_url[:-1]
            
        url = f"{base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "model": self._get_model(),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }

        retries = 3
        backoff = 1
        
        for attempt in range(retries + 1):
            try:
                req = urllib.request.Request(url, json.dumps(data).encode('utf-8'), headers)
                with urllib.request.urlopen(req) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    return {"content": result['choices'][0]['message']['content']}
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    if attempt < retries:
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                    else:
                        return {"error": "Rate limit exceeded (429). Please check your OpenAI API quota and billing details."}
                return {"error": f"HTTP Error: {e.code} {e.reason}"}
            except Exception as e:
                return {"error": str(e)}

    def refine_model(self, current_code, selection=None):
        system_prompt = "You are an expert in Monterey Phoenix (MP) modeling. Your task is to help the user flesh out their model by adding realistic details, assumptions, or completing the code."
        
        prompt = f"Here is the current MP code:\n\n{current_code}\n"
        if selection:
            prompt += f"\nFocus your suggestions on this selected part:\n{selection}\n"
        
        prompt += "\nPlease provide specific MP code suggestions to make this model more realistic and complete. Explain your changes briefly."

        return self._call_openai(system_prompt, prompt)

    def fetch_models(self):
        # Determine valid base URL
        base_url = self.settings_manager.get_setting("llm_base_url")
        if not base_url or not base_url.strip():
            base_url = "https://openrouter.ai/api/v1"
        if base_url.endswith("/"):
            base_url = base_url[:-1]

        url = f"{base_url}/models"
        api_key = self._get_api_key()
        headers = {
            "Content-Type": "application/json"
        }
        if api_key:
             headers["Authorization"] = f"Bearer {api_key}"

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                # OpenRouter and OpenAI return a list of objects with an 'id' field
                if 'data' in result:
                    return [model['id'] for model in result['data']]
                return []
        except Exception as e:
            return {"error": str(e)}

    def analyze_emergent_behavior(self, trace_json):
        system_prompt = "You are an expert in Monterey Phoenix (MP) modeling and trace analysis. Your task is to analyze trace data to identify potential emergent behaviors."
        
        # Truncate trace if too large, as a simple heuristic
        trace_str = json.dumps(trace_json, indent=2)
        if len(trace_str) > 10000:
            trace_str = trace_str[:10000] + "... (truncated)"

        prompt = f"Here is the trace data (JSON) generated from an MP model:\n\n{trace_str}\n\n"
        prompt += "Identify potential emergent behaviors, unexpected interactions, or interesting patterns in this trace. Provide a reasoned justification for each finding."

        return self._call_openai(system_prompt, prompt)
