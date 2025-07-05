# mednotegen

## Synthea Integration for Synthetic Health Data

This project uses [Synthea™](https://github.com/synthetichealth/synthea) to generate realistic synthetic patient data for doctor notes and reports.

### How to Set Up Synthea

1. **Clone Synthea**
   ```sh
   git clone https://github.com/synthetichealth/synthea.git
   ```
2. **Build the Synthea JAR**
   ```sh
   cd synthea
   ./gradlew build check test
   cp build/libs/synthea-with-dependencies.jar .
   cd ..
   ```
   Ensure `synthea-with-dependencies.jar` is in the `synthea/` directory at the root of your project.

3. **Java Requirement**
   You must have Java (JDK 8 or newer) installed. To install on macOS:
   ```sh
   brew install openjdk@17
   echo 'export PATH="/usr/local/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```
   Or download from [Oracle](https://www.oracle.com/java/technologies/downloads/).


### Attribution

See `README_SYNTHEA_NOTICE.md` and `LICENSE-APACHE-2.0` for license and attribution requirements.
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
python -m mednotegen.cli --count 5 --output output_dir
```

### Generate with LLM (OpenAI):
```sh
export OPENAI_API_KEY=your-key-here
python -m mednotegen.cli --count 2 --output output_dir --use-llm
```

- Requires `OPENAI_API_KEY` in your environment.
- LLM mode uses GPT-3.5/4 for realistic synthetic patient reports.
