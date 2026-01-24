# GryphonAI

## Overview
GryphonAI extends the [MP Gryphon](https://gitlab.nps.edu/monterey-phoenix/user-interfaces/gryphon) model checker by integrating Large Language Models (LLMs). This integration assists in discerning potential emergent behaviors within Monterey Phoenix (MP) models and provides reasonable justifications for these findings. Additionally, it helps in fleshing out models with real-world implementations, assumptions, and abstractions.

### About MP Gryphon
Gryphon provides a Python GUI user interface for accessing the Monterey Phoenix trace-generator. Gryphon is available for Windows, Mac, and Linux. On Linux systems, Gryphon runs stand-alone without requiring access to the Gryphon server.

* [Gryphon Wiki](https://gitlab.nps.edu/monterey-phoenix/user-interfaces/gryphon/-/wikis/home)
* [Installing MP Gryphon](https://gitlab.nps.edu/monterey-phoenix/user-interfaces/gryphon/-/wikis/Installing-MP-Gryphon)

## Features
- **Emergent Behavior Analysis**: Hooks into the MP generation process to identify and explain unexpected or "weird" machine behaviors using LLMs.
- **Model Refinement**: Assists in refining MP codes by suggesting improvements, real-world constraints, and abstractions.
- **Model Management**: Fetch and select available LLM models for analysis.

## Project Structure
- `src/`: Source code for the Gryphon extension and MP files.
  - `python/llm_interface.py`: Core interface for communicating with LLM providers.
- `test_llm.py`: Unit tests for the LLM interface.
- `install_mp.bash`: Script to install the base MP Gryphon dependencies.

## Installation

### Prerequisites
- Python 3.x
- Access to an LLM provider API (e.g., OpenAI, local LLM).

### Setup
1.  **Install MP Gryphon Dependencies**:
    Run the provided installation script to set up the environment.
    ```bash
    ./src/install_mp.bash
    ```

2.  **Configuration**:
    Ensure your LLM API keys and settings are configured. (Refer to `src/python/llm_interface.py` or your settings manager configuration).

## Usage

### LLM Interface
The `LLMInterface` class provides the main entry point for AI interactions.

```python
import sys
# Ensure src/python is in your path
sys.path.append("src/python")

from llm_interface import LLMInterface
# Initialize with your settings manager
llm = LLMInterface(settings_manager)

# Refine a model
suggestion = llm.refine_model("ROOT A: a;")
print(suggestion["content"])

# Analyze emergent behavior
analysis = llm.analyze_emergent_behavior({"trace": [...]})
print(analysis["content"])
```

## Testing
Run the included unit tests to verify the LLM integration:
```bash
python test_llm.py
```
