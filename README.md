# ai-agent-core
Agent 실행 및 오케스트레이션

> `.env` 파일이 없으면 실행이 불가합니다. 

# 로컬 실행 방법
### 1. ai-* 레포 전체 클론 후 각 레포 프로젝트 루트 디렉토리에서 아래 코드 실행
```
uv sync
```
### 2. ai-agent-core 실행
```
uv run python -m src.ai_agent_core.main
```
# API
## 구현 완료
### POST `/api/v1/chat/default`
> 일반적인 채팅 api이며 바로 답이 나옵니다(답하는 과정이 스트리밍으로 나오지 않습니다)
> ```
> @request
> {
>   "session_id": str, # 보고서 아이디
>   "query": str
> }
> ```
### POST `/api/v1/chat/sse`
> SSE 채팅 api이며 답하는 과정이 스트리밍으로 반환됩니다.
> ```
> @request
> {
>   "session_id": str, # 보고서 아이디
>   "query": str
> }
> ```
## 구현 예정
### POST `/api/v1/report`
> 리포트에 필요한 내용을 생성합니다.
> ```
> @request
> {
>    "userProfile": {
>    "totalScore": int,
>    "type": str,
>    "grade": int,
>    "nickname": str,
>    "officialName": str,
>    "description": str,
>    "portfolio": [
>      {
>        "category": str,
>        "weightPercent": int
>      },
>      {
>        "category": str,
>        "weightPercent": int
>      },
>      {
>        "category": str,
>        "weightPercent": int
>      },
>      {
>        "category": str,
>        "weightPercent": int
>      }
>    ],
>    "retirementPlan": {
>      "monthlyContribution": int,
>      "currentAge": int,
>      "targetAge": int,
>      "expectedReturnRate": int,
>      "totalContribution": int,
>      "expectedProfit": int,
>      "taxBenefit": int,
>      "expectedAssetAtRetirement": int
>    },
>    "metrics": {
>      "annualTaxBenefit": int,
>      "assetAt65": int,
>      "assetIncreaseAfter20Years": int,
>       "cumulativeTaxBenefit": int
>     }
>   }
> }
> ```
