from setuptools import setup, find_packages

setup(
    name="mednotegen",
    version="0.1.0",
    description="Generate fake doctor notes and patient reports as PDFs.",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "faker",
        "fpdf"
    ],
    entry_points={
        'console_scripts': [
            'mednotegen=mednotegen.cli:main',
        ],
    },
)
