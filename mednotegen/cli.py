import argparse
from .generator import NoteGenerator

def main():
    parser = argparse.ArgumentParser(description="Generate fake doctor notes or patient reports as PDFs.")
    parser.add_argument('--type', choices=['doctor_note', 'patient_report'], required=True, help='Type of note/report to generate')
    parser.add_argument('--count', type=int, default=1, help='Number of reports to generate')
    parser.add_argument('--output', type=str, default='output', help='Output directory for PDFs')
    parser.add_argument('--use-llm', action='store_true', help='Use LLM to generate note/report content (requires OpenAI API key)')
    args = parser.parse_args()

    generator = NoteGenerator(args.type, use_llm=args.use_llm)
    # Attempt to detect data source for reporting
    data_source = 'Unknown'
    if args.use_llm:
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
    generator.generate_notes(args.count, args.output)
    print(f"Generated {args.count} {args.type.replace('_', ' ')}(s) in {args.output}/ using {data_source}.")

if __name__ == "__main__":
    main()
