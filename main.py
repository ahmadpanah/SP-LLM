# main.py
from environment import VECEnvironment
from agents import SP_LLM_Agent, LLM_DT_Agent, S_MARL_Agent, GreedyAgent
from pdt import PredictiveDigitalTwin
from config import PARAMS
from results_handler import ResultsHandler

def run_simulation(env, agent, semantic_goal="BALANCE"):
    state = env.get_state()
    for _ in range(PARAMS['simulation_time_slots']):
        actions = agent.act(state, semantic_goal)
        state = env.step(actions)
    return env.metrics

def run_scenario_1(results_handler):
    agent_classes = {
        "SP-LLM": SP_LLM_Agent,
        "LLM-DT": LLM_DT_Agent,
        "S-MARL": S_MARL_Agent,
        "GO": GreedyAgent,
    }
    for n_vehicles in PARAMS['num_vehicles_range']:
        for agent_name, AgentClass in agent_classes.items():
            env = VECEnvironment(num_vehicles=n_vehicles)
            pdt = PredictiveDigitalTwin(env)
            agent = AgentClass(env, pdt=pdt)
            run_simulation(env, agent)
            
            metrics = results_handler.calculate_metrics(env)
            params = {'num_vehicles': n_vehicles}
            results_handler.record('scenario_1', agent_name, params, metrics)

def run_scenario_2(results_handler):
    n_vehicles = 20 # Fixed number for this scenario
    agent_classes = {"SP-LLM": SP_LLM_Agent, "LLM-DT": LLM_DT_Agent}
    
    for agent_name, AgentClass in agent_classes.items():
        env = VECEnvironment(num_vehicles=n_vehicles, dynamic_speed=True)
        pdt = PredictiveDigitalTwin(env)
        agent = AgentClass(env, pdt=pdt)
        
        peak_violation = 0
        for t in range(PARAMS['simulation_time_slots']):
            actions = agent.act(env.get_state())
            env.step(actions)
            # Simplified peak calculation
            if t > 10 and len(env.metrics['completed_tasks']) > 0:
                violations_last_10 = sum(1 for task in env.metrics['completed_tasks'][-10:] if (task.completion_time - task.creation_time) > (PARAMS['task_deadline_ms']/1000.0))
                rate = violations_last_10 / 10 * 100
                if rate > peak_violation:
                    peak_violation = rate
        
        metrics = results_handler.calculate_metrics(env)
        metrics['peak_violation_rate'] = peak_violation
        params = {'num_vehicles': n_vehicles}
        results_handler.record('scenario_2', agent_name, params, metrics)

def run_scenario_3(results_handler):
    n_vehicles = 20
    agent_classes = {"SP-LLM": SP_LLM_Agent, "LLM-DT": LLM_DT_Agent, "S-MARL": S_MARL_Agent}
    
    for agent_name, AgentClass in agent_classes.items():
        # Phase 1
        env1 = VECEnvironment(num_vehicles=n_vehicles)
        pdt1 = PredictiveDigitalTwin(env1)
        agent1 = AgentClass(env1, pdt=pdt1)
        for _ in range(PARAMS['simulation_time_slots'] // 2):
            actions = agent1.act(env1.get_state(), semantic_goal="BALANCE")
            env1.step(actions)
        metrics1 = results_handler.calculate_metrics(env1)
        results_handler.record('scenario_3', agent_name, {'phase': 1}, metrics1)

        # Phase 2
        env2 = VECEnvironment(num_vehicles=n_vehicles)
        pdt2 = PredictiveDigitalTwin(env2)
        agent2 = AgentClass(env2, pdt=pdt2)
        for _ in range(PARAMS['simulation_time_slots'] // 2):
            # SP-LLM adapts, others don't
            goal = "SAVE_ENERGY" if agent_name == "SP-LLM" else "BALANCE"
            actions = agent2.act(env2.get_state(), semantic_goal=goal)
            env2.step(actions)
        metrics2 = results_handler.calculate_metrics(env2)
        results_handler.record('scenario_3', agent_name, {'phase': 2}, metrics2)

if __name__ == "__main__":
    results = ResultsHandler()
    
    run_scenario_1(results)
    results.print_scenario_1()
    
    run_scenario_2(results)
    results.print_scenario_2()
    
    run_scenario_3(results)
    results.print_scenario_3()