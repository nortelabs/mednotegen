import argparse
from .generator import NoteGenerator

def main():
    import argparse
    from .generator import NoteGenerator
    parser = argparse.ArgumentParser(description="Generate fake doctor notes or patient reports as PDFs.")

    parser.add_argument('--count', type=int, help='Number of reports to generate')
    parser.add_argument('--output', type=str, help='Output directory for PDFs')
    parser.add_argument('--use-llm', action='store_true', help='Use LLM to generate note/report content (requires OpenAI API key)')
    parser.add_argument('--config', type=str, help='Path to YAML config file')
    parser.add_argument('--synthea-csv-dir', type=str, help='Path to Synthea output CSV directory (containing patients.csv, medications.csv, etc)')
    args = parser.parse_args()

    synthea_csv_dir = args.synthea_csv_dir
    # If config is provided, load config and override args
    if args.config:
        from .generator import NoteGenerator
        import yaml
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
        if 'synthea_csv_dir' in config:
            synthea_csv_dir = config['synthea_csv_dir']
        generator = NoteGenerator.from_config(args.config)
        count = config.get('count', args.count or 1)
        output = config.get('output_dir', args.output or 'output_dir')
        use_llm = generator.use_llm if hasattr(generator, 'use_llm') else args.use_llm
        # Patch in CLI override if provided
        if args.synthea_csv_dir:
            generator.synthea_csv_dir = args.synthea_csv_dir
            generator.template.synthea_csv_dir = args.synthea_csv_dir
    else:
        count = args.count or 1
        output = args.output or 'output_dir'
        use_llm = args.use_llm
        generator = NoteGenerator(use_llm=use_llm, synthea_csv_dir=synthea_csv_dir)

    # Attempt to detect data source for reporting
    data_source = 'Unknown'
    if use_llm:
        data_source = 'LLM'
    else:
        try:
            import os
            csv_dir = synthea_csv_dir or __import__('mednotegen.synthea_integration', fromlist=['OUTPUT_CSV_DIR']).OUTPUT_CSV_DIR
            patients_csv = os.path.join(csv_dir, 'patients.csv')
            meds_csv = os.path.join(csv_dir, 'medications.csv')
            if os.path.exists(patients_csv) and os.path.exists(meds_csv):
                data_source = f'Synthea CSV ({csv_dir})'
            else:
                data_source = 'Faker'
        except Exception:
            data_source = 'Faker'
    generator.generate_notes(count, output)
    print(f"Generated {count} patient report(s) in {output}/ using {data_source}.")

if __name__ == "__main__":
    main()
