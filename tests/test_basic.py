import os
import pytest

# Basic import test
def test_import_mednotegen():
    import mednotegen

# Test NoteGenerator instantiation from config (no Synthea required)
def test_note_generator_instantiation():
    from mednotegen.generator import NoteGenerator
    gen = NoteGenerator()
    assert gen is not None

# Test CLI entry point loads (does not run CLI)
def test_cli_entrypoint_exists():
    from mednotegen import cli
    assert hasattr(cli, 'main')

# Optionally: Test config loading (with a minimal config)
def test_note_generator_from_config(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_content = """
count: 1
output_dir: test_output
gender: any
min_age: 0
max_age: 120
use_llm: false
    """
    config_path.write_text(config_content)
    from mednotegen.generator import NoteGenerator
    gen = NoteGenerator.from_config(str(config_path))
    assert gen is not None
    assert gen.gender == 'any' or gen.gender is None
    assert gen.min_age == 0 or gen.min_age is None
    assert gen.max_age == 120 or gen.max_age is None

# Smoke test: CLI can be invoked (does not actually generate notes)
def test_cli_invocation(monkeypatch):
    from mednotegen import cli
    called = {}
    def fake_generate_notes(*args, **kwargs):
        called['yes'] = True
    monkeypatch.setattr("mednotegen.generator.NoteGenerator.generate_notes", fake_generate_notes)
    monkeypatch.setattr("sys.argv", ["mednotegen", "--count", "1", "--output", "test_output"])
    cli.main()
    assert called.get('yes')
