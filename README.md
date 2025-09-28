# Text2Reaction

Intelligent extraction of experimental procedures from scientific articles (PDF/HTML/TXT) to structured JSON format using the **Mistral AI** API. Modern web interface with result visualization.

## Features

- **Automatic extraction** of experimental sections
- **Modern web interface** for displaying reactions
- **JSON export** of extracted data
- **Multi-format support**: PDF, HTML, TXT
- **Upload via URL** or local file
- **Pydantic validation** for consistent data

## Quick Installation

```bash
# Clone the project
git clone <your-repo-url>
cd text2reaction

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configuration
cp env.example .env
# Edit .env and add your MISTRAL_API_KEY
export $(grep -v '^#' .env | xargs)
```

## Usage

### Web Interface
```bash
# Launch the application
make run
# or
python -m flask --app app.main run --debug

# Open http://127.0.0.1:5000
```

### Quick Test
Upload the sample file: `tests/samples/sample_procedure.txt`

## Extracted Data

Each extracted reaction contains:
- **Reactants and reagents** with quantities and equivalents
- **Reaction conditions** (temperature, time, atmosphere)
- **Workup** (purification steps)
- **Results** (yield, product name)
- **Additional notes**

## Architecture

```
app/
├── main.py          # Flask interface and routes
├── models.py        # Pydantic models for validation
├── extractor.py     # Mistral AI client
├── prompts.py       # Optimized prompts for extraction
├── readers.py       # PDF/HTML/TXT reading
└── section_finder.py # Experimental section detection
```
