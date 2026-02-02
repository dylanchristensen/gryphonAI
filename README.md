# Gryphon AI

Enhanced version of [Gryphon](https://gitlab.nps.edu/monterey-phoenix/user-interfaces/gryphon) with LLM-powered AI capabilities built-in.

## Quick Start

1. **Clone this repository:**
   ```bash
   git clone <your-repo-url>
   cd gryphonAI
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API key:**
   
   Copy `config.json.example` to `config.json` and add your API key:
   ```bash
   cp config.json.example config.json
   # Edit config.json with your API key
   ```
   
   Or set environment variables:
   ```bash
   export LLM_API_KEY="your-api-key-here"
   export LLM_MODEL="openai/gpt-oss-120b"
   export LLM_BASE_URL="https://openrouter.ai/api/v1"
   ```

4. **Run:**
   ```bash
   python run_gryphon.py
   ```
   
   Or on Windows:
   ```bash
   run_gryphon.bat
   ```

That's it! Gryphon will start with AI features enabled.

## Features

- **Refine Models**: Get AI suggestions to improve MP models, making them more realistic and complete
- **Analyze Traces**: Identify potential emergent behaviors in generated event traces

## Usage

Once running, use the **AI** menu in Gryphon:
- **AI > Refine Model with AI** - Get suggestions for your MP code
- **AI > Analyze Trace with AI** - Analyze generated traces for emergent behavior

## Project Structure

- `gryphon_source/`: Gryphon source with AI integration already applied
  - `python/`: Main Gryphon Python code
  - `python/preloaded-examples/`: Example MP models and snippets (bundled with Gryphon)
- `gryphon_ai/`: AI extension code
- `config.json`: Your LLM configuration (create from `config.json.example`)

## Configuration

The extension looks for `config.json` in:
- Current directory
- `~/.gryphon_ai/config.json`
- Environment variables (override file settings)

## Requirements

- Python 3.8+
- PySide6 (installed via requirements.txt)

## How It Works

Gryphon is included with AI integration already applied. The `gryphon_ai` plugin automatically:
- Integrates with Gryphon's GUI manager
- Adds the AI menu
- Captures trace data automatically

All done automatically - just run it!

## License

[Include Gryphon's license - check gryphon_source/COPYING.md]

## Credits

- Based on [Gryphon](https://gitlab.nps.edu/monterey-phoenix/user-interfaces/gryphon) by Monterey Phoenix
- AI extension developed by [Your Name/Team]
