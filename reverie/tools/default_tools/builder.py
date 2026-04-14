from __future__ import annotations

from ...memory import MemoryManager
from ..registry import ToolBinding, ToolRegistry
from .command import build_command_bindings
from .file_io import build_file_io_bindings
from .memory import build_memory_bindings
from .search import build_search_bindings
from .sleep import build_sleep_bindings


def build_builtin_bindings(memory_manager: MemoryManager) -> list[ToolBinding]:
    bindings: list[ToolBinding] = []
    bindings.extend(build_file_io_bindings())
    bindings.extend(build_search_bindings())
    bindings.extend(build_command_bindings())
    bindings.extend(build_sleep_bindings())
    bindings.extend(build_memory_bindings(memory_manager))
    return bindings


def register_builtin_tools(registry: ToolRegistry, memory_manager: MemoryManager) -> ToolRegistry:
    registry.register_many(build_builtin_bindings(memory_manager))
    return registry
