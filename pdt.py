# pdt.py
import numpy as np
from config import PARAMS

class PredictiveDigitalTwin:
    def __init__(self, environment):
        self.env = environment

    def forecast(self):
        """
        Simulates forecasting by projecting current state forward with some noise.
        A real implementation would use a trained model (e.g., LSTM).
        """
        current_state = self.env.get_state()
        forecasts = []
        
        for h in range(1, PARAMS['pdt_prediction_horizon'] + 1):
            future_state_h = {'time_slot': current_state['time_slot'] + h, 'vehicles': []}
            for v_state in current_state['vehicles']:
                # Predict position
                future_pos = (v_state['position_m'] + v_state['speed_mps'] * h) % (PARAMS['road_length_km'] * 1000)
                
                # Predict task load with some noise
                noise = np.random.normal(1.0, 0.2)
                future_task_load = v_state['task_load_bytes'] * noise * (0.9**h) # Assume load decreases
                
                future_state_h['vehicles'].append({
                    'id': v_state['id'],
                    'predicted_position_m': future_pos,
                    'predicted_task_load_bytes': max(0, future_task_load)
                })
            forecasts.append(future_state_h)
            
        return forecasts