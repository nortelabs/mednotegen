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
    generator.generate_notes(args.count, args.output)
    src = 'LLM' if args.use_llm else 'Faker/templates'
    print(f"Generated {args.count} {args.type.replace('_', ' ')}(s) in {args.output}/ using {src}.")

if __name__ == "__main__":
    main()
