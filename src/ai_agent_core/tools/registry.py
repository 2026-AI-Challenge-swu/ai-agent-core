# src/ai_agent_core/registry.py
class ToolRegistry:
    """
    레지스트리 인스턴스
    tool 동적 생성할 수도 있으니까 만들어봄
    """
    def __init__(self):
        self._tools = {}

    def register(self, name: str = None):
        """도구를 등록하는 데코레이터"""
        def decorator(func):
            tool_name = name or func.__name__
            self._tools[tool_name] = func
            return func
        return decorator

    def get(self, name: str):
        return self._tools.get(name)

    def list_tools(self):
        return list(self._tools.keys())

# 레지스트리 인스턴스 생성
tool_registry = ToolRegistry()