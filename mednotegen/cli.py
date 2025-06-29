import argparse
from .generator import NoteGenerator

def main():
    parser = argparse.ArgumentParser(description="Generate fake doctor notes or patient reports as PDFs.")
    parser.add_argument('--type', choices=['doctor_note', 'patient_report'], help='Type of note/report to generate')
    parser.add_argument('--count', type=int, help='Number of reports to generate')
    parser.add_argument('--output', type=str, help='Output directory for PDFs')
    parser.add_argument('--use-llm', action='store_true', help='Use LLM to generate note/report content (requires OpenAI API key)')
    parser.add_argument('--config', type=str, help='Path to YAML config file')
    args = parser.parse_args()

    # If config is provided, load config and override args
    if args.config:
        from .generator import NoteGenerator
        import yaml
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
        note_type = config.get('note_type', 'patient_report')
        count = config.get('count', 1)
        output = config.get('output_dir', 'output')
        use_llm = config.get('use_llm', False)
        generator = NoteGenerator(note_type, use_llm=use_llm)
    else:
        note_type = args.type if args.type else 'patient_report'
        count = args.count if args.count else 1
        output = args.output if args.output else 'output'
        use_llm = args.use_llm
        generator = NoteGenerator(note_type, use_llm=use_llm)

    # Attempt to detect data source for reporting
    data_source = 'Unknown'
    if use_llm:
        data_source = 'LLM'
    else:
        try:
            from .synthea_integration import OUTPUT_CSV_DIR
            import os
            patients_csv = os.path.join(OUTPUT_CSV_DIR, 'patients.csv')
            meds_csv = os.path.join(OUTPUT_CSV_DIR, 'medications.csv')
            if os.path.exists(patients_csv) and os.path.exists(meds_csv):
                data_source = 'Synthea CSV'
            else:
                data_source = 'Faker'
        except Exception:
            data_source = 'Faker'
    generator.generate_notes(count, output)
    print(f"Generated {count} {note_type.replace('_', ' ')}(s) in {output}/ using {data_source}.")

if __name__ == "__main__":
    main()
