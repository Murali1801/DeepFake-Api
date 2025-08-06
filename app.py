import os
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, origins=[
    "http://localhost",
    "http://localhost:3000",
    "https://verisightai.vercel.app"
])

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

PROMPT = """
You are an advanced AI misinformation detection and verification system with real-time web search and multi-modal input analysis.

Input:
- User provides content that can be:
  - Text or article URL
  - Image (analyze for manipulation/deepfake)
  - Video URL or description (analyze for manipulation)

Tasks:
1. Analyze input and classify as Real, Fake, Misleading, or Unverifiable.
2. Provide a JSON report with verdict, confidence, evidence, explanation, and credibility proof.

Output ONLY the following JSON format:

{{
  "input_type": "{input_type}",
  "input_content": "{input_content}",
  "verdict": "Real | Fake | Misleading | Unverifiable",
  "confidence_score": 0-100,
  "evidence": [
    {{
      "source_title": "Source title",
      "source_url": "https://source-link.com",
      "summary": "How this source supports or refutes the content",
      "similarity_score": 0-100,
      "reputation_score": 0-100
    }}
  ],
  "analysis_summary": "Clear explanation of findings and verdict.",
  "credibility_proof": [
    {{
      "claim_verified": "Exact claim or element verified or disproven",
      "matched_fact": "Fact or data from a source supporting/refuting the claim",
      "source_proof_url": "https://source-link.com"
    }}
  ]
}}
Do not include anything outside this JSON.
"""

@app.route("/analyze-content", methods=["POST"])
def analyze_content():
    input_type = request.form.get("input_type")
    input_content = request.form.get("input_content")

    image_b64 = None

    # Handle image
    if "image" in request.files:
        image_file = request.files["image"]
        input_type = "image"
        image_bytes = image_file.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        input_content = f"data:{image_file.mimetype};base64,{image_b64}"

    # Handle video (as URL or description)
    elif input_type == "video" and input_content:
        pass  # Already captured

    # Handle text
    elif input_type == "text" and input_content:
        pass  # Already captured

    else:
        return jsonify({"error": "Missing or unsupported input_type or input_content"}), 400

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}" if OPENROUTER_API_KEY else "",
        "Content-Type": "application/json",
    }

    openrouter_url = "https://openrouter.ai/api/v1/chat/completions"

    if input_type == "image":
        payload = {
            "model": "qwen/qwen2.5-vl-32b-instruct:free",
            "messages": [
                {"role": "system", "content": PROMPT.format(input_type=input_type, input_content="Image uploaded")},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": input_content}
                    ]
                }
            ],
            "temperature": 0.1,
            "max_tokens": 1500,
        }
    else:
        prompt = PROMPT.format(input_type=input_type, input_content=input_content.replace('"', '\\"'))
        payload = {
            "model": "mistralai/mistral-small-3.2-24b-instruct:free",
            "messages": [
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 1500,
        }

    try:
        response = requests.post(openrouter_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        content = data["choices"][0]["message"]["content"]

        import json
        try:
            return jsonify(json.loads(content))
        except json.JSONDecodeError:
            return jsonify({"raw_response": content})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "OpenRouter API request failed", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


