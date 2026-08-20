import traceback
from functools import partial
from langgraph.graph import StateGraph, END, Graph
from langgraph.checkpoint.memory import MemorySaver
from src.ai_agent_core.schemas.state import AgentState


class AgentGraphBuilder:
    def __init__(self, app_state):
        self.logger = app_state.logger
        self.llm = app_state.llm

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