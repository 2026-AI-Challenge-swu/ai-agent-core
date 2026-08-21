import traceback

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Send

from src.ai_agent_core.graph.state import AgentState, WorkerState

from src.ai_agent_core.graph.nodes.decomposer import DecomposerNode
from src.ai_agent_core.graph.nodes.planner import PlannerNode
from src.ai_agent_core.graph.nodes.tool_call import ToolCallNode
from src.ai_agent_core.graph.nodes.synthesizer import SynthesizerNode
from src.ai_agent_core.graph.nodes.quality_check import QualityCheckNode
from src.ai_agent_core.graph.nodes.generate_answer import GenerateAnswerNode


class AgentGraphBuilder:

    def __init__(self, app_state):
        self.logger = app_state.logger

        # Nodes
        self.decomposer = DecomposerNode(app_state)
        self.planner = PlannerNode(app_state)
        self.tool_call = ToolCallNode(app_state)
        self.generate_answer = GenerateAnswerNode(app_state)
        self.quality_check = QualityCheckNode(app_state)
        self.synthesizer = SynthesizerNode(app_state)

        self.checkpointer = MemorySaver()

        # Worker graph
        self.worker = self._build_worker_graph()

        # Main graph
        self.agent = self._build_graph()

    # =========================================================
    # Initial State
    # =========================================================

    def _set_initial_state(
        self,
        query: str,
        session_id: str,
    ) -> AgentState:

        return AgentState(
            query=query,
            session_id=session_id,
            sub_queries=[],
            worker_results=[],
            quality_score=0.0,
            quality_feedback="",
            final_answer="",
        )

    # =========================================================
    # Error Logging
    # =========================================================

    def _with_error_logging(self, node_name, func):

        def wrapper(state):

            try:
                self.logger.info(
                    f"[START] {node_name}"
                )

                result = func(state)

                self.logger.info(
                    f"[END] {node_name}"
                )

                return result

            except Exception:

                self.logger.exception(
                    f"[ERROR] Node '{node_name}' failed"
                )

                self.logger.error(
                    traceback.format_exc()
                )

                raise

        return wrapper

    # =========================================================
    # Worker Graph
    # =========================================================

    def _build_worker_graph(self):

        workflow = StateGraph(WorkerState)

        workflow.add_node(
            "planner",
            self._with_error_logging(
                "planner",
                self.planner,
            ),
        )

        workflow.add_node(
            "tool_call",
            self._with_error_logging(
                "tool_call",
                self.tool_call,
            ),
        )

        workflow.add_node(
            "generate_answer",
            self._with_error_logging(
                "generate_answer",
                self.generate_answer,
            ),
        )

        # planner
        workflow.set_entry_point("planner")

        # planner → tool
        workflow.add_edge(
            "planner",
            "tool_call",
        )

        # tool → answer
        workflow.add_edge(
            "tool_call",
            "generate_answer",
        )

        # answer → END
        workflow.add_edge(
            "generate_answer",
            END,
        )

        return workflow.compile()

    # =========================================================
    # Fan-out
    # =========================================================

    def _fanout_workers(
        self,
        state: AgentState,
    ):

        sub_queries = state.get(
            "sub_queries",
            [],
        )

        self.logger.info(
            f"[FANOUT] {len(sub_queries)} workers"
        )

        return [
            Send(
                "worker",
                {
                    "sub_query": item["sub_query"],
                    "intent": item["intent"],
                    "sub_query_id": item["sub_query_id"],
                    "worker_results": [],
                },
            )
            for item in sub_queries
        ]

    # =========================================================
    # Quality Routing
    # =========================================================

    def _route_quality(
        self,
        state: AgentState,
    ) -> str:

        score = state.get(
            "quality_score",
            0.0,
        )

        feedback = state.get(
            "quality_feedback",
            "",
        )

        if score >= 0.8:
            return "synthesizer"

        if (
            "근거" in feedback
            or "정보 부족" in feedback
        ):
            return "retry_workers"

        return "retry_workers"

    # =========================================================
    # Retry Fan-out
    # =========================================================

    def _retry_workers(
        self,
        state: AgentState,
    ):

        sub_queries = state.get(
            "sub_queries",
            [],
        )

        self.logger.info(
            f"[RETRY] {len(sub_queries)} workers"
        )

        return [
            Send(
                "worker",
                {
                    "sub_query": item["sub_query"],
                    "sub_query_id": item["sub_query_id"],
                },
            )
            for item in sub_queries
        ]

    # =========================================================
    # Main Graph
    # =========================================================

    def _build_graph(self):

        workflow = StateGraph(AgentState)

        # -----------------------------------------------------
        # Nodes
        # -----------------------------------------------------

        workflow.add_node(
            "decomposer",
            self._with_error_logging(
                "decomposer",
                self.decomposer,
            ),
        )

        workflow.add_node(
            "worker",
            self.worker,
        )

        workflow.add_node(
            "quality_check",
            self._with_error_logging(
                "quality_check",
                self.quality_check,
            ),
        )

        workflow.add_node(
            "synthesizer",
            self._with_error_logging(
                "synthesizer",
                self.synthesizer,
            ),
        )

        # -----------------------------------------------------
        # Entry
        # -----------------------------------------------------

        workflow.set_entry_point(
            "decomposer"
        )

        # -----------------------------------------------------
        # Decomposer → Parallel Workers
        # -----------------------------------------------------

        workflow.add_conditional_edges(
            "decomposer",
            self._fanout_workers,
        )

        # -----------------------------------------------------
        # Worker → Quality Check
        # -----------------------------------------------------

        workflow.add_edge(
            "worker",
            "quality_check",
        )

        # -----------------------------------------------------
        # Quality Check → ...
        # -----------------------------------------------------

        workflow.add_conditional_edges(
            "quality_check",
            self._route_quality,
            {
                "synthesizer": "synthesizer",
                "retry_workers": "worker",
            },
        )

        # -----------------------------------------------------
        # Synthesizer → END
        # -----------------------------------------------------

        workflow.add_edge(
            "synthesizer",
            END,
        )

        return workflow.compile(
            checkpointer=self.checkpointer,
        )

    # =========================================================
    # Public
    # =========================================================

    def run(
        self,
        query: str,
        session_id: str,
    ) -> dict:

        initial_state = self._set_initial_state(
            query=query,
            session_id=session_id,
        )

        config = {
            "configurable": {
                "thread_id": session_id,
            }
        }

        return self.agent.invoke(
            input=initial_state,
            config=config,
        )