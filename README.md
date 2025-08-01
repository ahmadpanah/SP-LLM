# Semantic-Aware Proactive LLM Orchestration (SP-LLM) Simulator (with REAL GPT-4 Integration)

This project provides a full-featured Python simulation of the framework proposed in the paper "Semantic-Aware LLM Orchestration for Proactive Resource Management in Predictive Digital Twin Vehicular Networks."

## WARNING: Cost and Performance

-   **API Costs**: Every decision made by the `SP-LLM` and `LLM-DT` agents will make a real API call to OpenAI. This will incur costs on your OpenAI account. Be mindful of the number of simulation steps you run.
-   **Performance Speed**: Real API calls are much slower than local functions. The simulation will take significantly longer to run than a mocked version.

## How to Run

### 1. Prerequisites

You need Python 3.9+ and the following packages:

```bash
pip install numpy pandas tabulate openai python-dotenv
```

### 2. Set Up Your OpenAI API Key

Your API key must be kept secret. We will use an environment file to manage it securely.

a.  Create a new file named `.env` in the root of the project directory (`sp-llm/`).

b.  Add your API key to this file like so:

    ```
    OPENAI_API_KEY="sk-YourSecretAPIKeyGoesHere"
    ```

c.  The `config.py` script is set up to automatically load this key. The `.env` file is ignored by version control systems by default, keeping your key safe.

### 3. Running the Simulation

To run the entire experimental evaluation, simply execute the main script from the project root directory:

```bash
python main.py
```

The script will first check if your API key is loaded. If it is, the simulation will begin, making real calls to GPT-4. It will then print the results in formatted tables directly to your console.

## Project Structure

```
sp-llm/
├── main.py                 # Main simulator entry point
├── environment.py          # The core simulation environment
├── agents.py               # Logic for all agents (now calls real_llm.py)
├── pdt.py                  # The simulated Predictive Digital Twin
├── real_llm.py             # NEW: Handles real API calls to GPT-4
├── config.py               # Loads API key and simulation parameters
├── results_handler.py      # Helper to collect and display results
├── README.md               # This file
└── .env                    # YOUR SECRET FILE: Contains your API key
```