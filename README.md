# mednotegen
Generate fake doctor notes or patient reports as PDFs

## Installation

### 1. Create a virtual environment and install base requirements
```sh
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Usage

### Generate with Faker/templates (default):
```sh
python -m mednotegen.cli --type doctor_note --count 5 --output output_dir
python -m mednotegen.cli --type patient_report --count 5 --output output_dir
```

### Generate with LLM (OpenAI):
```sh
export OPENAI_API_KEY=your-key-here
python -m mednotegen.cli --type doctor_note --count 2 --output output_dir --use-llm
```

- Requires `OPENAI_API_KEY` in your environment.
- LLM mode uses GPT-3.5/4 for realistic synthetic notes.
