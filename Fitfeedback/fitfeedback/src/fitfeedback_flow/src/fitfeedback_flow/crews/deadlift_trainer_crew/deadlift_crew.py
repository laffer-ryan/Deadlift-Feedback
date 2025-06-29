from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List, ClassVar, Optional
from pydantic import Field  
# from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from crewai.knowledge.source.crew_docling_source import CrewDoclingSource
from crewai.knowledge.source.csv_knowledge_source import CSVKnowledgeSource
from crewai.knowledge.source.excel_knowledge_source import ExcelKnowledgeSource

import os
from dotenv import load_dotenv
load_dotenv()





# ================================================================================

@CrewBase
class DeadliftTrainerCrew():
    """Deadlift Trainer Crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'


    TEST_SOURCE_FILE_TYPE: ClassVar[str] = 'md'

    @agent
    def deadlift_setup_trainer(self) -> Agent:
        return Agent(
            config=self.agents_config["deadlift_setup_trainer"],  # type: ignore[index]
            knowledge_sources=[
                CrewDoclingSource(
                    file_paths=get_sources('SOURCE_PATH', self.TEST_SOURCE_FILE_TYPE, 'setup'),
                )
            ],
            memory=False
        )

    @agent
    def deadlift_pull_trainer(self) -> Agent:

        return Agent(
            config=self.agents_config["deadlift_pull_trainer"],  # type: ignore[index]
            knowledge_sources=[
                CrewDoclingSource(
                    file_paths=get_sources('SOURCE_PATH', self.TEST_SOURCE_FILE_TYPE, 'pull'),
                )
            ],
            memory=False
        )

    @agent
    def orchestration_deadlift_physical_trainer(self) -> Agent:
        return Agent(
            config=self.agents_config["orchestration_deadlift_physical_trainer"],  # type: ignore[index]
            knowledge_sources=[
                CrewDoclingSource(
                    file_paths=get_sources('SOURCE_PATH', self.TEST_SOURCE_FILE_TYPE, 'processed'),
                ),
            ],
            memory=False
        )

    @task
    def task_setup_phase_side_view(self) -> Task:
        return Task(
            config=self.tasks_config["task_setup_phase_side_view"],  # type: ignore[index]
        )

    @task
    def task_setup_phase_front_view(self) -> Task:
        return Task(
            config=self.tasks_config["task_setup_phase_front_view"],  # type: ignore[index]
        )

    @task
    def task_pull_phase_side_view(self) -> Task:
        return Task(
            config=self.tasks_config["task_pull_phase_side_view"],  # type: ignore[index]
        )

    @task
    def task_pull_phase_front_view(self) -> Task:
        return Task(
            config=self.tasks_config["task_pull_phase_front_view"],  # type: ignore[index]
        )

    @task
    def task_orchestration_report(self) -> Task:
        return Task(
            config=self.tasks_config["task_orchestration_report"],  # type: ignore[index]
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the Deadlift Trainer Crew"""

        metric_txt_files = get_sources('SOURCE_PATH', '.txt', 'metrics_side')


        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            knowledge_sources=[
                TextFileKnowledgeSource(
                    file_paths=metric_txt_files
                )
            ],
            verbose=True,
            memory=False
        )
    
    def get_tasks_for_view(self, view: str) -> List[Task]:
        """
        Returns the appropriate setup and pull tasks for the given view ('left' or 'front').
        """
        if view == "left":
            return [
                self.task_setup_phase_side_view(),
                self.task_pull_phase_side_view(),
                self.task_orchestration_report(),
            ]
        elif view == "front":
            return [
                self.task_setup_phase_front_view(),
                self.task_pull_phase_front_view(),
                self.task_orchestration_report(),
            ]
        elif view == "right":
            return [
                self.task_setup_phase_side_view(),
                self.task_pull_phase_side_view(),
                self.task_orchestration_report(),
            ]
        else:
            raise ValueError(f"Unknown view: {view}")


# ========================================================================================================

def get_sources(cls, file_type, stage=None) -> List[str]:
    """
    Retrieves file paths from the environment variable specified by `cls` that match the given `file_type` and `stage`.
    """
    env_path = os.getenv(cls)
    if not env_path:
        return []
    files = os.listdir(env_path)
    # Remove quotes if present in env_path
    env_path = env_path.strip("'").strip('"')
    # Build file list based on stage
    if stage == 'setup':
        paths = [file for file in files if file.endswith(file_type) and 'setup' in file]
    elif stage == 'pull':
        paths = [file for file in files if file.endswith(file_type) and 'pull' in file]
    elif stage == 'metrics_front':
        paths = [file for file in files if file.endswith(file_type) and file.endswith('.txt') and 'front' in file]
    elif stage == 'metrics_side':
        paths = [file for file in files if file.endswith(file_type) and file.endswith('.txt') and 'side' in file]
    elif stage == 'processed':
        paths = [file for file in files if file.endswith(file_type) and file.startswith('processed')]
    else:
        paths = [file for file in files if file.endswith(file_type)]
    if paths:
        print(f'Adding Path {paths}')
    return paths