# real_llm.py
import json
import numpy as np
from openai import OpenAI
from config import OPENAI_API_KEY

# Initialize the OpenAI client
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None

def generate_system_prompt():
    return """
    You are an expert network orchestrator for a Vehicular Edge Computing (VEC) system.
    Your goal is to make optimal decisions for task offloading and resource allocation based on the provided network state.

    You will be given:
    1.  A "Strategic Goal" (e.g., save energy, lower latency).
    2.  The "Current State" of the network (vehicle data, queue backlogs).
    3.  Optional "Predictive State" forecasts from a Digital Twin.

    You MUST respond with ONLY a JSON object in the following format:
    {"w": [w_v0, w_v1, ...], "a": [a_v0, a_v1, ...]}

    - "w" is a list of offloading ratios (float between 0.0 and 1.0) for each vehicle.
    - "a" is a list of server CPU allocation ratios (float between 0.0 and 1.0) for each vehicle's queue. The sum of "a" should be 1.0.

    Do not include any other text, explanations, or markdown formatting in your response. Only the JSON object.
    """

def generate_user_prompt(state, pdt_forecasts, semantic_goal):
    # Serialize the state and forecasts into a readable string format
    state_str = json.dumps(state, indent=2)
    forecast_str = "Not available."
    if pdt_forecasts:
        forecast_str = json.dumps(pdt_forecasts, indent=2)

    prompt = f"""
    Strategic Goal: "{semantic_goal}"

    Current State:
    {state_str}

    Predictive State (Forecasts for next H steps):
    {forecast_str}

    Based on all the information provided, determine the optimal offloading ratios (w) and resource allocation ratios (a).
    Remember to respond with only the JSON object.
    """
    return prompt

def get_default_action(num_vehicles):
    """A safe fallback action in case of API or parsing failure."""
    return {
        'w': [0.5] * num_vehicles,
        'a': [1.0 / num_vehicles] * num_vehicles
    }

def query_gpt4_orchestrator(state, pdt_forecasts=None, semantic_goal="BALANCE"):
    if not client:
        print("ERROR: OpenAI API key not configured. Using default action.")
        return get_default_action(len(state['vehicles']))

    system_prompt = generate_system_prompt()
    user_prompt = generate_user_prompt(state, pdt_forecasts, semantic_goal)
    num_vehicles = len(state['vehicles'])

    try:
        print(f"Querying GPT-4 for {semantic_goal}...")
        completion = client.chat.completions.create(
            model="gpt-4-turbo",  # Or "gpt-4" if you prefer
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2, # Lower temperature for more deterministic outputs
        )
        response_content = completion.choices.message.content
        
        # Parse the JSON response
        action = json.loads(response_content)

        # Validate the response structure
        if 'w' in action and 'a' in action and len(action['w']) == num_vehicles and len(action['a']) == num_vehicles:
            # Normalize allocation ratios to ensure they sum to 1
            total_a = sum(action['a'])
            if total_a > 0:
                action['a'] = [val / total_a for val in action['a']]
            else:
                 action['a'] = [1.0 / num_vehicles] * num_vehicles
            print("GPT-4 responded successfully.")
            return action
        else:
            print("ERROR: GPT-4 response has invalid format. Using default action.")
            return get_default_action(num_vehicles)

    except Exception as e:
        print(f"ERROR: An exception occurred during GPT-4 API call: {e}")
        print("Using default fallback action.")
        return get_default_action(num_vehicles)