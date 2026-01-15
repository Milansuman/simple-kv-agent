# netrach

## Install with pip

```bash
pip install git+https://github.com/Milansuman/netrach-agent.git
```

## Usage setup

Ensure the following environment variables are set:
```env
GROQ_API_KEY=
GITHUB_TOKEN=
NETRA_API_KEY=
NETRA_OTLP_ENDPOINT=
```
then run `netrach` to use the utility.

## Setup Instructions

Clone the repo and create a python venv
```bash
python3 -m venv .venv
source .venv/bin/activate
```
(If you're creating a venv with a different name, add it to the .gitignore)

Install the dependencies
```bash
pip install -r requirements.txt
```

set up the env based on .env.example and run!
```bash
python3 src/agent.py
```