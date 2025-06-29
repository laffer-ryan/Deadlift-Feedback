#!/usr/bin/env python

from fitfeedback_flow.src.fitfeedback_flow.crews.deadlift_trainer_crew.deadlift_crew import DeadliftTrainerCrew
from crewai import Crew, Process
import asyncio
    

def run_deadlift_flow(inputs: dict, video_name: str = None):
    crew_obj = DeadliftTrainerCrew()
    data_structure_type = crew_obj.TEST_SOURCE_FILE_TYPE
    view = inputs.get("view_direction").lower()
    # inputs['topic'] = 'deadlift'
    tasks = crew_obj.get_tasks_for_view(view)


    # --- Stage 1: Run Setup & Pull Tasks ---
    crew1 = Crew(
        agents=[
            crew_obj.deadlift_setup_trainer(),
        ],
        tasks=[tasks[0]],  # setup + pull
        process=Process.sequential, 
        verbose=True,
        output_log_file=f'LLM_logs/{video_name}_A1_{data_structure_type}'
    )
    
    crew2 = Crew(
        agents=[
            crew_obj.deadlift_pull_trainer()
        ],
        tasks=[tasks[1]],  # extension
        process=Process.sequential,  # or parallel in future
        verbose=True,
        output_log_file=f'LLM_logs/{video_name}_A2_{data_structure_type}'
    )
    # Run A1 and A2 crews sequentially
    async def kickoff_a1_a2():
        return await asyncio.gather(
            asyncio.to_thread(crew1.kickoff, inputs=inputs),
            asyncio.to_thread(crew2.kickoff, inputs=inputs)
        )
    crew1_result, crew2_result = asyncio.run(kickoff_a1_a2())
    setup_output = crew1_result.raw
    pull_output = crew2_result.raw

    # --- Stage 2: Run Orchestration Task ---
    inputs["combined_phase_summary"] = f"Setup:\n{setup_output}\n\nPull:\n{pull_output}"

    crew3 = Crew(
        agents=[crew_obj.orchestration_deadlift_physical_trainer()],
        tasks=[tasks[2]],  # orchestration
        process=Process.sequential,
        verbose=True,
        output_log_file=f'LLM_logs/{video_name}_A3_{data_structure_type}'
    )

    result3 = crew3.kickoff(inputs=inputs)
    # Reset knowledge memory for all agents in crew1, crew2, and crew3
    for crew in [crew1, crew2, crew3]:
        for agent_instance in crew.agents:
            memory_system = getattr(agent_instance, "knowledge", None)
            print(memory_system)

    return result3.raw