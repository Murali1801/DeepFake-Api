# AI Fake News & Deepfake Detection Flask API

This Flask API provides a backend server that accepts text, image, or video inputs via **form-data**, analyzes the authenticity using the Qwen 2.5 VL model (`qwen/qwen2.5-vl-32b-instruct:free`) via OpenRouter API, and returns a detailed JSON report indicating if the input content is real, fake, misleading, or unverifiable.

---

## Features

- Accepts inputs as:
  - Text or article URLs
  - Image files (uploaded)
  - Video URLs or descriptions
- Automatically encodes images in base64 for multimodal AI model input
- Uses OpenRouter API to communicate with the Qwen vision-language model
- Returns structured JSON with:
  - Verdict and confidence score
  - Evidence sources and summaries
  - Clear explanation and credibility proof
- CORS enabled for local and specified frontend domains

---

## Getting Started

### Prerequisites

- Python 3.8+
- OpenRouter API key ([Get API key](https://openrouter.ai))

### Installation

1. Clone this repository or copy the files.
2. Create and activate a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
