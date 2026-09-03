import time


# BaseHTTPMiddleware는 응답 본문을 감싸서 처리하는 방식이라 EventSourceResponse(SSE) 같은
# 스트리밍 응답과 호환성 문제가 있음(응답이 실제로 스트리밍되지 못하고 빈 채로 끊김 —
# starlette/fastapi에 잘 알려진 이슈). 순수 ASGI 미들웨어로 구현해 스트리밍 응답을 건드리지 않고
# ASGI 메시지만 관찰해서 로깅함.
class RequestLogMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()
        status_holder = {"status": None}

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_holder["status"] = message["status"]
            await send(message)

        await self.app(scope, receive, send_wrapper)

        elapsed = time.perf_counter() - start
        logger = scope["app"].state.logger
        logger.info(
            f"{scope['method']} {scope['path']} -> {status_holder['status']} ({elapsed:.3f}s)"
        )
