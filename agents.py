# agents.py
import numpy as np
# Import the real LLM orchestrator instead of the mock one
from real_llm import query_gpt4_orchestrator

class BaseAgent:
    def __init__(self, env, pdt=None):
        self.env = env
        self.pdt = pdt
        self.num_vehicles = env.num_vehicles

    def act(self, state, semantic_goal="BALANCE"):
        raise NotImplementedError

class SP_LLM_Agent(BaseAgent):
    def act(self, state, semantic_goal="BALANCE"):
        forecasts = self.pdt.forecast()
        # Call the real GPT-4 API with predictive data
        return query_gpt4_orchestrator(state, pdt_forecasts=forecasts, semantic_goal=semantic_goal)

class LLM_DT_Agent(BaseAgent):
    def act(self, state, semantic_goal="BALANCE"):
        # Call the real GPT-4 API without predictive data (reactive)
        # We pass the default semantic goal as it does not adapt
        return query_gpt4_orchestrator(state, pdt_forecasts=None, semantic_goal="BALANCE")

class S_MARL_Agent(BaseAgent):
    def act(self, state, semantic_goal="BALANCE"):
        # Behavior remains the same for this baseline
        num_vehicles = len(state['vehicles'])
        w_ratios = [np.random.uniform(0.3, 0.7) for _ in range(num_vehicles)]
        a_ratios = np.random.rand(num_vehicles)
        a_ratios /= np.sum(a_ratios)
        return {'w': w_ratios, 'a': list(a_ratios)}

class GreedyAgent(BaseAgent):
    def act(self, state, semantic_goal="BALANCE"):
        # Behavior remains the same for this baseline
        num_vehicles = len(state['vehicles'])
        channel_gains = [v['channel_gain'] for v in state['vehicles']]
        best_vehicle_idx = np.argmax(channel_gains) if channel_gains else 0
        
        w_ratios = [0.1] * num_vehicles
        if w_ratios:
             w_ratios[best_vehicle_idx] = 0.9
        
        a_ratios = [1.0 / num_vehicles] * num_vehicles if num_vehicles > 0 else []
        
        return {'w': w_ratios, 'a': a_ratios}