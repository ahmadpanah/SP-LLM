# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Securely load the API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# All simulation parameters in one place for easy modification.
PARAMS = {
    'network_bandwidth_mhz': 20,
    'vec_server_cpu_freq_ghz': 400,
    'vehicle_cpu_freq_ghz': 5,
    'vehicle_tx_power_mw': 200,
    'channel_noise_dbm': -110,
    'num_vehicles_range': [10, 20, 30],
    'vehicle_speed_kmh': (60, 100),
    'task_size_bytes': (1000, 1500),
    'cpu_cycles_per_byte_mhz': 0.25,
    'pdt_prediction_horizon': 5,  # H=5 time slots
    'simulation_time_slots': 100,
    'task_deadline_ms': 200,
    'road_length_km': 2,
    # Derived parameters
    'channel_noise_watts': 10**(-110 / 10) / 1000,
    'vehicle_tx_power_watts': 200 / 1000,
}