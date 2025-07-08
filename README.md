# mednotegen

This project uses [Synthea™](https://github.com/synthetichealth/synthea) to generate realistic synthetic patient data for  medical notes. 

---

## Usage

```python
from mednotegen.generator import NoteGenerator

gen = NoteGenerator.from_config("config.yaml")
gen.generate_notes(10, "output_dir")

# Or specify Synthea CSV directory directly:
gen = NoteGenerator(synthea_csv_dir="/path/to/synthea/output/csv")
gen.generate_notes(10, "output_dir")
```

## Using a Custom Synthea Directory with config.yaml

You can specify the Synthea CSV directory directly in your config file. Add the following line to your `config.yaml`:

Example `config.yaml`:
```yaml
count: 10
output_dir: output_dir
synthea_csv_dir: /path/to/synthea/output/csv
```

Then generate notes using:

```python
from mednotegen.generator import NoteGenerator

gen = NoteGenerator.from_config("config.yaml")
gen.generate_notes(10, "output_dir")
```


## ⚠️ Synthea Dependency Required

This project requires [Synthea™](https://github.com/synthetichealth/synthea), an open-source synthetic patient generator, as an **external dependency**. You must clone and build Synthea yourself before using `mednotegen`.

**To set up Synthea:**

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

---

## Configuration (`config.yaml`)

You can customize patient generation and report output using a `config.yaml` file. Example options:

```yaml
count: 10                    # Number of reports to generate
output_dir: output_dir       # Output directory for PDFs
use_llm: false               # Use LLM for report generation
synthea_csv_dir: /path/to/synthea/output/csv   # Path to Synthea-generated CSV files
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

---

### Troubleshooting: 
#### Synthea Data Location

If you see errors about missing `patients.csv`, `medications.csv`, or `conditions.csv`, make sure you have generated Synthea data and that the path you provide (via `synthea_csv_dir`, CLI, or config) points to the correct directory containing those files.

If you installed `mednotegen` via pip, the default location is inside the package directory. For custom or system-wide Synthea runs, always specify the output CSV directory explicitly.

- **No CSV files generated:**
  - Make sure you edited the correct `synthea.properties` and used the `-c` flag when running Synthea.
  - Ensure `exporter.csv.export = true` is set and not overridden elsewhere in the file.
- **FileNotFoundError for CSVs:**
  - Confirm the CSV files exist in the path specified by `synthea_csv_dir` or in the expected package location.
- **ValueError: No patients found matching the specified filters:**
  - Check your age/gender filters in `config.yaml`. Try relaxing them if you have too few patients.


### Configure Synthea to Export CSVs

Edit `src/main/resources/synthea.properties` in your Synthea directory:

```
exporter.csv.export = true
```

(Ensure any `exporter.csv.export = false` lines are removed or commented out.)

### Generate Patient Data with Synthea

From your Synthea directory, clean any old output and generate new data:

```
rm -rf output/
java -jar synthea-with-dependencies.jar -c src/main/resources/synthea.properties -p 1000
```

- The `-p 1000` flag generates 1000 patients.
- After running, check for CSV files in `output/csv/`.


### Attribution

See `README_SYNTHEA_NOTICE.md` and `LICENSE-APACHE-2.0` for license and attribution requirements.
