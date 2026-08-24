import traceback
from typing import AsyncGenerator, Dict, Any

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
        userProfile: any,
        portfolio: any,
        retirementPlan: any,
        metrics: any,
        mode: str
    ) -> AgentState:
        """
        graph invoke 전 state 초기화
        """

        return AgentState(
            query=query,
            session_id=session_id,
            mode=mode,
            sub_queries=[],
            worker_results=[],
            quality_score=0.0,
            quality_feedback="",
            final_answer="",
            userProfile=userProfile,
            portfolio=portfolio,
            retirementPlan=retirementPlan,
            metrics=metrics,
        )

    # =========================================================
    # Error Logging
    # =========================================================

    def _with_error_logging(self, node_name, func):
        """
        어떤 노드 작업 진행중인지, 어디에서 에러 났는지 확인
        """
        async def wrapper(state):

            try:
                self.logger.info(
                    f"[START] {node_name}"
                )

                result = await func(state)

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
        """
        서브 graph(병렬 처리용) 빌드
        노드 엣지 연결
        """
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
        """
        decomposer -> 서브 graph 연결고리
        (서브 graph용 state init하는 부분)
        """
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
                    "sub_mode": state["mode"],
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
        """
        퀄리티 확인 분기 루트
        """
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
    # Main Graph
    # =========================================================

    def _build_graph(self):
        """
        메인 graph 빌드
        노드 엣지 연결
        """
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

    async def run(
        self,
        query: str = "",
        session_id: str = "",
        userProfile: any = None,
        portfolio: any = None,
        retirementPlan: any = None,
        metrics: any = None,
        mode: str = "chat"
    ) -> dict:

        initial_state = self._set_initial_state(
            query=query,
            session_id=session_id,
            userProfile=userProfile,
            portfolio=portfolio,
            retirementPlan=retirementPlan,
            metrics=metrics,
            mode=mode,
        )

        config = {
            "configurable": {
                "thread_id": session_id,
            }
        }

        return await self.agent.ainvoke(
            input=initial_state,
            config=config,
        )


    async def stream_run(
        self,
        query: str,
        session_id: str,
        mode: str = "chat",
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        SSE 전송을 위한 비동기 제너레이터
        LangGraph 노드 진입/종료 이벤트를 감지하여 yield 수행
        """
        initial_state = self._set_initial_state(
            query=query,
            session_id=session_id,
            mode=mode,
        )

        config = {
            "configurable": {
                "thread_id": session_id,
            }
        }

        # 감지 및 메시지를 지정할 노드 목록
        target_nodes = {
            "decomposer": "질문 분석 및 작업 분할 중입니다.",
            "planner": "하위 작업 계획 수립 중입니다.",
            "tool_call": "외부 도구/검색을 수행하고 있습니다.",
            "generate_answer": "하위 답변을 생성하는 중입니다.",
            "quality_check": "결과물 품질을 검증하고 있습니다.",
            "synthesizer": "최종 답변을 종합 작성하고 있습니다."
        }

        try:
            # LangGraph의 event stream 추출 (v2 이벤트 API 적용)
            async for event in self.agent.astream_events(
                input=initial_state,
                config=config,
                version="v2"
            ):
                event_type = event.get("event")
                node_name = event.get("name")

                # 노드/체인 시작 시점 이벤트 처리
                if event_type == "on_chain_start" and node_name in target_nodes:
                    yield {
                        "event": "node_enter",
                        "node": node_name,
                        "session_id": session_id,
                        "message": target_nodes[node_name]
                    }

                # 노드/체인 종료 시점 이벤트 처리 (필요시 사용)
                elif event_type == "on_chain_end" and node_name in target_nodes:
                    yield {
                        "event": "node_exit",
                        "node": node_name,
                        "session_id": session_id,
                        "message": f"[{node_name}] 단계 완료"
                    }

            # 전체 Graph 정상 완료 후 final state 조회 및 반환
            final_state = await self.agent.aget_state(config)
            yield {
                "event": "final_result",
                "session_id": session_id,
                "response": final_state.values.get("final_answer", "")
            }

        except Exception as e:
            self.logger.error(f"[STREAM ERROR] {traceback.format_exc()}")
            yield {
                "event": "error",
                "session_id": session_id,
                "message": f"처리 중 오류가 발생했습니다: {str(e)}"
            }