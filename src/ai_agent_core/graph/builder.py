import traceback
from functools import partial

from langgraph.graph import StateGraph, END, Graph
from langgraph.checkpoint.memory import MemorySaver

from src.ai_agent_core.graph.state import AgentState

from src.ai_agent_core.graph.nodes.decomposer import DecomposerNode
from src.ai_agent_core.graph.nodes.planner import PlannerNode
from src.ai_agent_core.graph.nodes.tool_call import ToolCallNode
from src.ai_agent_core.graph.nodes.synthesizer import SynthesizerNode
from src.ai_agent_core.graph.nodes.quality_check import QualityCheckNode
from src.ai_agent_core.graph.nodes.generate_answer import GenerateAnswerNode


class AgentGraphBuilder:
    def __init__(self, app_state):
        self.logger = app_state.logger

        # 노드 클래스 초기화
        self.decomposer = DecomposerNode(app_state)
        self.planner = PlannerNode(app_state)
        self.tool_call = ToolCallNode(app_state)
        self.generate_answer = GenerateAnswerNode(app_state)
        self.quality_check = QualityCheckNode(app_state)
        self.synthesizer = SynthesizerNode(app_state)

        self.checkpointer = MemorySaver()
        self.agent = self._build_graph()


    def _set_initial_state(self, query: str, session_id: str) -> AgentState:
        """
        AgentState 초기화 함수
        """
        return AgentState(
            query=query,
            session_id=session_id,
        )


    def _route_quality(self, state: AgentState) -> str:
        """
        답변 평가 분기 함수
        """

        score = state["quality_score"]
        feedback = state["quality_feedback"]

        if score >= 0.8:
            return "final"

        if "근거" in feedback or "정보 부족" in feedback:
            return "retry_plan"

        return "retry_answer"


    def _with_error_logging(self, node_name, func):
        """
        노드 진행상황 확인 + 에러 확인용 로그 래퍼 
        """
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
        """
        LangGraph 빌드(주요 함수는 /node 에서 정의)
        """
        workflow = StateGraph(AgentState)

        workflow.add_node(
            "decomposer",
            self._with_error_logging(
                "decomposer",
                self.decomposer,
            ),
        )
        
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


        workflow.set_entry_point("decomposer")
        workflow.add_edge("decomposer","planner")
        workflow.add_edge("planner","tool_call")
        workflow.add_edge("tool_call","generate_answer")
        workflow.add_edge("generate_answer","quality_check")
        workflow.add_edge("quality_check","synthesizer")
        workflow.add_edge("synthesizer", END)


        workflow.add_conditional_edges(
            "quality_check",
            self._route_quality,
            {
                "final": "final_response",
                "retry_plan": "planner",
                "retry_answer": "generate_answer",
            },
        )


        return workflow.compile(
            checkpointer=self.checkpointer,
        )


    # public method
    def run(self, query: str, session_id: str) -> dict:
        initial_state = self._set_initial_state(query, session_id)
        config = {
            "configurable": {
                "thread_id": session_id,
            }
        }

        return self.agent.invoke(
            initial_state=initial_state,
            config=config
            )