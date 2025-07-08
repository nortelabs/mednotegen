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

## Configuration (`config.yaml`)

You can customize patient generation and report output using a `config.yaml` file. Example options:

```yaml
count: 10                    # Number of reports to generate
output_dir: output_dir       # Output directory for PDFs
use_llm: false               # Use LLM for report generation
seed: 1234                   # Random seed for reproducibility
reference_date: "20250628"   # Reference date for data generation (YYYYMMDD)
clinician_seed: 5678         # Optional: separate seed for clinician assignment
gender: female               # male, female, or any
min_age: 30                  # Minimum patient age
max_age: 60                  # Maximum patient age
state: New York              # Synthea state parameter
modules:
  - cardiovascular-disease
  - diabetes      
  - hypertension
  - asthma          
local_config: custom_synthea.properties  # Custom Synthea config file
local_modules: ./synthea_modules         # Directory for custom modules
```

- **count**: Number of reports to generate
- **output_dir**: Directory to save generated PDFs
- **use_llm**: If true, uses OpenAI LLM for report text
- **seed**: Random seed for reproducibility
- **reference_date**: Reference date for age calculations (YYYYMMDD)
- **clinician_seed**: Optional, separate seed for clinician assignment
- **gender**: Gender filter for patients (`male`, `female`, or `any`)
- **min_age**, **max_age**: Age range for patients
- **state**: US state for Synthea simulation
- **modules**: Synthea disease modules to enable
- **local_config**: Path to a custom Synthea config file
- **local_modules**: Directory for custom Synthea modules

---

### More Synthea Modules
For an up-to-date and complete list of available modules, see the [official Synthea modules directory](https://github.com/synthetichealth/synthea/tree/master/src/main/resources/modules).

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

---

## Example Patient Report Output

```
Mekhi724 Kemmer911
==================
Race:           White
Ethnicity:      Non-Hispanic
Gender:         F
Age:            33
Birth Date:     1983-11-04
Marital Status: M
--------------------------------------------------------------------------------
ALLERGIES: N/A
--------------------------------------------------------------------------------
MEDICATIONS:
2013-08-22 [CURRENT] : Acetaminophen 160 MG for Acute bronchitis (disorder)
1996-05-12 [CURRENT] : Acetaminophen 160 MG for Acute bronchitis (disorder)
1995-04-13 [CURRENT] : Acetaminophen 160 MG for Acute bronchitis (disorder)
1984-01-14 [CURRENT] : Penicillin V Potassium 250 MG for Streptococcal sore throat (disorder)
--------------------------------------------------------------------------------
CONDITIONS:
2015-10-30 - 2015-11-07 : Fetus with chromosomal abnormality
2015-10-30 - 2015-11-07 : Miscarriage in first trimester
2015-10-30 - 2015-11-07 : Normal pregnancy
2013-08-22 - 2013-09-08 : Acute bronchitis (disorder)
1985-08-07 -            : Food Allergy: Fish
--------------------------------------------------------------------------------
CARE PLANS:
2013-08-22 [STOPPED] : Respiratory therapy
                         Reason: Acute bronchitis (disorder)
                         Activity: Recommendation to avoid exercise
                         Activity: Deep breathing and coughing exercises
--------------------------------------------------------------------------------
OBSERVATIONS:
2014-01-14 : Body Weight                              73.9 kg
2014-01-14 : Body Height                              163.7 cm
2014-01-14 : Body Mass Index                          27.6 kg/m2
2014-01-14 : Systolic Blood Pressure                  133.0 mmHg
2014-01-14 : Diastolic Blood Pressure                 76.0 mmHg
2014-01-14 : Blood Pressure                           2.0 
--------------------------------------------------------------------------------
PROCEDURES:
2015-10-30 : Standard pregnancy test for Normal pregnancy
2014-01-14 : Documentation of current medications
--------------------------------------------------------------------------------
ENCOUNTERS:
2015-11-07 : Encounter for Fetus with chromosomal abnormality
2015-10-30 : Encounter for Normal pregnancy
2014-01-14 : Outpatient Encounter
2013-08-22 : Encounter for Acute bronchitis (disorder)
--------------------------------------------------------------------------------
```

