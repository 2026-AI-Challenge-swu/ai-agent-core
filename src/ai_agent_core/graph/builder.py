import traceback
from functools import partial

from langgraph.graph import StateGraph, END, Graph
from langgraph.checkpoint.memory import MemorySaver

from src.ai_agent_core.graph.state import AgentState

from src.ai_agent_core.graph.nodes.planner import PlannerNode
from src.ai_agent_core.graph.nodes.tool_call import ToolCallNode
from src.ai_agent_core.graph.nodes.synthesizer import SynthesizerNode
from src.ai_agent_core.graph.nodes.quality_check import QualityCheckNode
from src.ai_agent_core.graph.nodes.generate_answer import GenerateAnswerNode


class AgentGraphBuilder:
    def __init__(self, app_state):
        self.logger = app_state.logger

        self.planner = PlannerNode(app_state)
        self.tool_call = ToolCallNode(app_state)
        self.generate_answer = GenerateAnswerNode(app_state)
        self.quality_check = QualityCheckNode(app_state)
        self.synthesizer = SynthesizerNode(app_state)

        self.checkpointer = MemorySaver()
        self.agent = self._build_graph()


    def set_initial_state(self, query: str, session_id: str) -> AgentState:
        return AgentState(
            query=query,
            session_id=session_id,
        )


    def _with_error_logging(self, node_name, func):
        def wrapper(state):
            try:
                self.logger.info(f"[START] {node_name}")
                result = func(state)
                self.logger.info(f"[END] {node_name}")
                return result

            except Exception as e:
                self.logger.exception(f"[ERROR] Node '{node_name}' failed")
                self.logger.error(traceback.format_exc())
                raise

        return wrapper


    def _build_graph(self) -> Graph:
        workflow = StateGraph(AgentState)


        return workflow.compile(
            checkpointer=self.checkpointer,
        )


    def run(self, query: str, session_id: str) -> dict:
        initial_state = self.set_initial_state(query, session_id)
        config = {
            "configurable": {
                "thread_id": session_id,
            }
        }

        return self.agent.invoke(
            initial_state=initial_state,
            config=config
            )