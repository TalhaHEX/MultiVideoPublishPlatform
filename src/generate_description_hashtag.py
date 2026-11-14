import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class GenerateDescriptionHashtag:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GROK_API_KEY")

    def generate_description_and_hashtags(
        self, first_language, second_language, third_language, topic, api_key=None
    ):
        GROK_API_KEY = api_key or self.api_key or os.getenv("GROK_API_KEY")

        if not GROK_API_KEY:
            print("Error: GROK_API_KEY not found. Please set GROK_API_KEY in your environment variables or .env file.")
            return None

        url = "https://api.x.ai/v1/chat/completions"

        prompt = f"""
        Generate a short video description about '{topic}' in three languages:
        1. {first_language}
        2. {second_language}
        3. {third_language}

        Then, generate relevant hashtags for the video.
        Important: The hashtags should always be in English.

        Format:
        {first_language}: [description]
        {second_language}: [description]
        {third_language}: [description]
        Hashtags: [hashtags in English]
        """

        payload = {
            "model": "grok-2-1212",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }

        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            result = response.json()["choices"][0]["message"]["content"]
            return self.parse_generated_content(result)
        except Exception as e:
            print(f"Error generating content: {e}")
            return None

    def parse_generated_content(self, content):
        """Parse the generated content into structured format"""
        lines = content.strip().split("\n")
        parsed = {"lang1_desc": "", "lang2_desc": "", "lang3_desc": "", "hashtags": ""}

        for line in lines:
            if ":" in line:
                if "Hashtags" in line or "hashtags" in line:
                    parsed["hashtags"] = line.split(":", 1)[1].strip()
                elif not parsed["lang1_desc"]:
                    parsed["lang1_desc"] = line.split(":", 1)[1].strip()
                elif not parsed["lang2_desc"]:
                    parsed["lang2_desc"] = line.split(":", 1)[1].strip()
                elif not parsed["lang3_desc"]:
                    parsed["lang3_desc"] = line.split(":", 1)[1].strip()

        return parsed


# Example usage
if __name__ == "__main__":
    gen = GenerateDescriptionHashtag()
    result = gen.generate_description_and_hashtags(
        "English", "Spanish", "French", "AI Automation"
    )
    print(result)
