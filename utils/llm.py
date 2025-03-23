import os
import aiohttp
import json
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HF_KEY")
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"


async def query_llm(transcript_text: str, question: str) -> str:
    try:
        prompt = f"Use the transcript to answer the question.\n\nTranscript: {transcript_text}\n\nQuestion: {question}\nAnswer:"

        payload = {
            "inputs": prompt,
            "parameters": {"max_length": 200, "temperature": 0.7, "top_p": 0.9},
        }

        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(HF_API_URL, headers=headers, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"Error from Hugging Face API: {response.status}")
                
                response_data = await response.json()

        # ✅ Extract the answer properly
        if isinstance(response_data, list) and len(response_data) > 0:
            generated_text = response_data[0]["generated_text"].strip()

            # ✅ Extract answer after "Answer:"
            if "Answer:" in generated_text:
                answer = generated_text.split("Answer:")[-1].strip()
            else:
                answer = generated_text

            return answer

        elif "error" in response_data:
            raise Exception(response_data["error"])
        else:
            return "Error: No valid response from Hugging Face API."

    except Exception as e:
        return f"Error during LLM processing: {str(e)}"
