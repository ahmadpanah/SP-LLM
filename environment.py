# environment.py
import numpy as np
from config import PARAMS

class Vehicle:
    def __init__(self, vehicle_id, speed_mps, position_m):
        self.id = vehicle_id
        self.speed_mps = speed_mps
        self.position_m = position_m
        self.tasks = []

class Task:
    def __init__(self, task_id, vehicle_id, size_bytes, creation_time):
        self.id = task_id
        self.vehicle_id = vehicle_id
        self.size_bytes = size_bytes
        self.creation_time = creation_time
        self.completion_time = -1
        self.deadline = creation_time + (PARAMS['task_deadline_ms'] / 1000.0)

class VECEnvironment:
    def __init__(self, num_vehicles, dynamic_speed=False):
        self.num_vehicles = num_vehicles
        self.dynamic_speed = dynamic_speed
        self.time_slot = 0
        self.task_id_counter = 0

        self.vehicles = self._create_vehicles()
        self.server_queues = {k: [] for k in range(self.num_vehicles)} # One queue per vehicle for simplicity
        
        self.metrics = {
            'completed_tasks': [],
            'total_energy_j': 0,
        }

    def _create_vehicles(self):
        vehicles = []
        for i in range(self.num_vehicles):
            speed_kmh = np.random.uniform(*PARAMS['vehicle_speed_kmh'])
            speed_mps = speed_kmh * 1000 / 3600
            position_m = np.random.uniform(0, PARAMS['road_length_km'] * 1000)
            vehicles.append(Vehicle(i, speed_mps, position_m))
        return vehicles

    def _update_vehicle_positions(self):
        for v in self.vehicles:
            if self.dynamic_speed and np.random.rand() < 0.2: # 20% chance to change speed
                speed_kmh = np.random.uniform(*PARAMS['vehicle_speed_kmh'])
                v.speed_mps = speed_kmh * 1000 / 3600
            v.position_m = (v.position_m + v.speed_mps) % (PARAMS['road_length_km'] * 1000)

    def _generate_tasks(self):
        for v in self.vehicles:
            if np.random.rand() < 0.7: # 70% chance to generate a task
                task_size = np.random.uniform(*PARAMS['task_size_bytes'])
                task = Task(self.task_id_counter, v.id, task_size, self.time_slot)
                v.tasks.append(task)
                self.task_id_counter += 1

    def get_channel_gain(self, vehicle):
        # Simplified path loss model
        distance_m = abs(vehicle.position_m - (PARAMS['road_length_km'] * 1000 / 2))
        if distance_m == 0: distance_m = 1
        path_loss = 128.1 + 37.6 * np.log10(distance_m / 1000) # in dB
        return 10**(-path_loss / 10)

    def get_state(self):
        state = {
            'time_slot': self.time_slot,
            'vehicles': [
                {
                    'id': v.id,
                    'position_m': v.position_m,
                    'speed_mps': v.speed_mps,
                    'task_load_bytes': sum(t.size_bytes for t in v.tasks),
                    'channel_gain': self.get_channel_gain(v),
                } for v in self.vehicles
            ],
            'server_queue_lengths': {k: len(q) for k, q in self.server_queues.items()}
        }
        return state

    def step(self, actions):
        """
        Actions is a dict: {'w': offloading_ratios, 'a': allocation_ratios}
        ratios are lists of lists/dicts matching vehicles and tasks.
        For simplicity, we use a single ratio per vehicle.
        """
        self._update_vehicle_positions()
        self._generate_tasks()

        w_ratios = actions['w'] # [w_v0, w_v1, ...]
        a_ratios = actions['a'] # [a_v0, a_v1, ...]

        total_energy_this_step = 0
        
        # 1. Process local and offloaded tasks
        for i, v in enumerate(self.vehicles):
            tasks_to_process = v.tasks[:]
            v.tasks = []
            
            for task in tasks_to_process:
                offload_decision = np.random.rand() < w_ratios[i]
                
                if not offload_decision: # Process locally
                    cycles_needed = task.size_bytes * PARAMS['cpu_cycles_per_byte_mhz'] * 1e6
                    proc_time = cycles_needed / (PARAMS['vehicle_cpu_freq_ghz'] * 1e9)
                    # Simplified energy: E = k * f^2 * t
                    energy = 1e-26 * (PARAMS['vehicle_cpu_freq_ghz'] * 1e9)**2 * proc_time
                    total_energy_this_step += energy
                    task.completion_time = self.time_slot + proc_time
                    self.metrics['completed_tasks'].append(task)
                else: # Offload to server
                    channel_gain = self.get_channel_gain(v)
                    rate_bps = PARAMS['network_bandwidth_mhz'] * 1e6 * np.log2(1 + (PARAMS['vehicle_tx_power_watts'] * channel_gain) / PARAMS['channel_noise_watts'])
                    tx_time = task.size_bytes * 8 / rate_bps
                    energy = PARAMS['vehicle_tx_power_watts'] * tx_time
                    total_energy_this_step += energy
                    # Task arrives at server after tx_time, we simplify by adding to queue now
                    self.server_queues[v.id].append(task)
        
        # 2. Process tasks from server queue
        total_server_alloc = sum(a_ratios)
        if total_server_alloc > 1.0: # Normalize if agent gives invalid action
            a_ratios = [r / total_server_alloc for r in a_ratios]

        for i, v in enumerate(self.vehicles):
            if self.server_queues[v.id]:
                server_cpu_for_v = a_ratios[i] * PARAMS['vec_server_cpu_freq_ghz'] * 1e9
                if server_cpu_for_v > 0:
                    task = self.server_queues[v.id].pop(0)
                    cycles_needed = task.size_bytes * PARAMS['cpu_cycles_per_byte_mhz'] * 1e6
                    proc_time = cycles_needed / server_cpu_for_v
                    # Simplified server energy
                    energy = 1e-24 * (server_cpu_for_v)**2 * proc_time
                    total_energy_this_step += energy
                    task.completion_time = self.time_slot + proc_time
                    self.metrics['completed_tasks'].append(task)
        
        self.metrics['total_energy_j'] += total_energy_this_step
        self.time_slot += 1

        return self.get_state()