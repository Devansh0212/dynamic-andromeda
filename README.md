# Dynamic Andromeda

Dynamic Andromeda is a Python-based macroeconomic investment-research pipeline. It ingests public economic data, classifies the current growth/inflation regime, retrieves relevant investment principles, and generates a concise, principle-based investment memo.

> This project is for research and educational use only. It does not provide investment advice.

## What it does

1. Fetches real GDP and CPI series from FRED.
2. Measures year-over-year change and momentum in growth and inflation.
3. Classifies the environment into one of four regimes:
   - Goldilocks — growth rising, inflation falling
   - Reflation/Boom — growth rising, inflation rising
   - Stagflation — growth falling, inflation rising
   - Deflation/Bust — growth falling, inflation falling
4. Retrieves relevant investing principles from the local knowledge layer.
5. Uses a local Ollama model to produce a short investment memo.

## Requirements

- Python 3.9+
- [Ollama](https://ollama.com/) running locally (optional; the project returns a fallback memo when unavailable)
- An Ollama model available locally, such as `llama3`

## Setup

```bash
git clone https://github.com/Devansh0212/dynamic-andromeda.git
cd dynamic-andromeda

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

To enable AI-generated memos, start Ollama and pull the default model:

```bash
ollama serve
ollama pull llama3
```

Set `OLLAMA_BASE_URL` only if Ollama is not running at `http://localhost:11434`.

## Run

```bash
python main.py
```

Optionally evaluate the model at a specific historical date:

```bash
python main.py --date 2024-01-01
```

## Project structure

```text
main.py                  # Orchestrates the end-to-end research pipeline
engine/
  data_ingestors.py      # Economic-data ingestion
  regime_classifier.py   # Growth/inflation regime classification
knowledge/
  retriever.py           # Principle retrieval
insight/
  memo_generator.py      # Ollama-backed memo generation
requirements.txt         # Python dependencies
```

## Output

The program prints:

- the detected economic regime and supporting growth/inflation metrics;
- the number of principles retrieved; and
- a short investment memo explaining the economic mechanism, historical context, and a general portfolio bias.

## Disclaimer

Markets are uncertain. Validate all inputs and conduct independent research before making financial decisions.
