# mock_llm.py
import numpy as np

def query_llm_orchestrator(state, pdt_forecasts=None, semantic_goal="BALANCE"):
    """
    This function simulates an LLM call. It produces structured output based on
    the provided state, forecasts, and semantic goal.
    """
    num_vehicles = len(state['vehicles'])
    
    # Base decisions on current state
    w_ratios = [] # Offloading ratios
    a_ratios = [] # Allocation ratios

    # --- LLM Reasoning Simulation ---
    # Good channel = higher chance of offloading
    channel_gains = [v['channel_gain'] for v in state['vehicles']]
    avg_gain = np.mean(channel_gains) if channel_gains else 0
    
    for v in state['vehicles']:
        # Base offloading on channel quality
        if v['channel_gain'] > avg_gain:
            w_ratios.append(np.random.uniform(0.6, 0.9))
        else:
            w_ratios.append(np.random.uniform(0.1, 0.4))

    # Base allocation on server queue length
    queue_lengths = list(state['server_queue_lengths'].values())
    total_queue = sum(queue_lengths)
    if total_queue > 0:
        a_ratios = [q / total_queue for q in queue_lengths]
    else:
        a_ratios = [1.0 / num_vehicles] * num_vehicles

    # --- Apply Proactive Adjustment (if pDT forecasts are available) ---
    if pdt_forecasts:
        # Example: if a vehicle's task load is predicted to be high, increase its server allocation
        predicted_loads = [f['vehicles'][i]['predicted_task_load_bytes'] for i, f in enumerate(pdt_forecasts) if f['vehicles']]
        if predicted_loads:
            # This is a highly simplified logic
            pass # In a real scenario, you'd have more complex adjustments here.

    # --- Apply Semantic Goal Adjustment ---
    if semantic_goal == "SAVE_ENERGY":
        # Reduce offloading to keep server idle, reduce server allocation
        w_ratios = [r * 0.3 for r in w_ratios]
        a_ratios = [r * 0.3 for r in a_ratios]
    elif semantic_goal == "LOW_LATENCY":
        # Maximize offloading and server allocation
        w_ratios = [min(1.0, r * 1.5) for r in w_ratios]
        a_ratios = [min(1.0, r * 1.5) for r in a_ratios]
        total_a = sum(a_ratios)
        if total_a > 0:
            a_ratios = [r / total_a for r in a_ratios]

    return {'w': w_ratios, 'a': a_ratios}