"""TiTrATE execution engine for TRI-X."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_MAX_EXECUTION_SECONDS = 5.0
DEFAULT_EXECUTION_TIMEOUT_TRIGGER = "timeout"
DEFAULT_TIMESTAMP_KEY = "timestamp"


class ExecutionStatus(Enum):
    """Status of action execution."""

    SUCCESS = "success"
    TIMEOUT = "timeout"
    FAILED = "failed"
    ABORTED = "aborted"


@dataclass
class TemporalConstraint:
    """Temporal constraint definition."""

    max_time: float = DEFAULT_MAX_EXECUTION_SECONDS
    deadline: Optional[float] = None
    min_time: Optional[float] = None
    periodic: bool = False
    period: Optional[float] = None


@dataclass
class TiTrATEResult:
    """Result of TiTrATE execution."""

    status: ExecutionStatus
    result: Any
    execution_time: float
    constraint_met: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


class TiTrATEEngine:
    """Execute actions under temporal constraints."""

    def __init__(
        self,
        max_time: float = DEFAULT_MAX_EXECUTION_SECONDS,
        enable_timeout: bool = True,
        enable_logging: bool = True,
    ):
        self.max_time = max_time
        self.enable_timeout = enable_timeout
        self.enable_logging = enable_logging
        self.execution_history: List[TiTrATEResult] = []
        logger.info("TiTrATEEngine initialized with max_time=%ss", max_time)

    def execute(
        self,
        action: Callable[..., Any],
        constraint: Optional[TemporalConstraint] = None,
        *args: Any,
        **kwargs: Any,
    ) -> TiTrATEResult:
        """Execute an action with an optional temporal constraint."""
        active_constraint = constraint or TemporalConstraint(max_time=self.max_time)
        start_time = time.time()
        execution_status = ExecutionStatus.SUCCESS
        action_result: Any = None
        constraint_met = True

        try:
            if self.enable_timeout:
                action_result = self._execute_with_timeout(
                    action,
                    active_constraint.max_time,
                    *args,
                    **kwargs,
                )
            else:
                action_result = action(*args, **kwargs)
        except TimeoutError:
            execution_status = ExecutionStatus.TIMEOUT
            constraint_met = False
            logger.warning("Action execution timed out after %ss", active_constraint.max_time)
        except Exception as exc:  # pragma: no cover - defensive path
            execution_status = ExecutionStatus.FAILED
            constraint_met = False
            logger.error("Action execution failed: %s", exc)

        execution_time = time.time() - start_time
        current_time = time.time()

        if active_constraint.deadline is not None and current_time > active_constraint.deadline:
            execution_status = ExecutionStatus.TIMEOUT
            constraint_met = False

        if active_constraint.min_time is not None and execution_time < active_constraint.min_time:
            constraint_met = False

        titrate_result = TiTrATEResult(
            status=execution_status,
            result=action_result,
            execution_time=execution_time,
            constraint_met=constraint_met,
            metadata={
                "max_time": active_constraint.max_time,
                "deadline": active_constraint.deadline,
                DEFAULT_TIMESTAMP_KEY: start_time,
            },
        )
        self.execution_history.append(titrate_result)

        if self.enable_logging:
            logger.info(
                "TiTrATE execution: status=%s time=%.3fs constraint_met=%s",
                execution_status.value,
                execution_time,
                constraint_met,
            )

        return titrate_result

    def _execute_with_timeout(
        self,
        action: Callable[..., Any],
        timeout_seconds: float,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute a callable with timeout enforcement."""
        import threading

        result_container: List[Any] = [None]
        exception_container: List[Optional[BaseException]] = [None]

        def wrapped_action() -> None:
            try:
                result_container[0] = action(*args, **kwargs)
            except BaseException as exc:  # pragma: no cover - defensive path
                exception_container[0] = exc

        worker_thread = threading.Thread(target=wrapped_action, daemon=True)
        worker_thread.start()
        worker_thread.join(timeout_seconds)

        if worker_thread.is_alive():
            raise TimeoutError(f"Execution exceeded {timeout_seconds}s")

        if exception_container[0] is not None:
            raise exception_container[0]

        return result_container[0]

    async def execute_async(
        self,
        action: Callable[..., Any],
        constraint: Optional[TemporalConstraint] = None,
        *args: Any,
        **kwargs: Any,
    ) -> TiTrATEResult:
        """Asynchronous version of :meth:`execute`."""
        active_constraint = constraint or TemporalConstraint(max_time=self.max_time)
        start_time = time.time()
        execution_status = ExecutionStatus.SUCCESS
        action_result: Any = None
        constraint_met = True

        try:
            action_result = await asyncio.wait_for(
                action(*args, **kwargs),
                timeout=active_constraint.max_time,
            )
        except asyncio.TimeoutError:
            execution_status = ExecutionStatus.TIMEOUT
            constraint_met = False
        except Exception as exc:  # pragma: no cover - defensive path
            execution_status = ExecutionStatus.FAILED
            constraint_met = False
            logger.error("Async action failed: %s", exc)

        execution_time = time.time() - start_time
        return TiTrATEResult(
            status=execution_status,
            result=action_result,
            execution_time=execution_time,
            constraint_met=constraint_met,
            metadata={"max_time": active_constraint.max_time},
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Return aggregate execution statistics."""
        if not self.execution_history:
            return {}

        successful_executions = sum(
            1
            for execution_result in self.execution_history
            if execution_result.status == ExecutionStatus.SUCCESS
        )
        execution_times = [
            execution_result.execution_time for execution_result in self.execution_history
        ]

        return {
            "total_executions": len(self.execution_history),
            "successful_executions": successful_executions,
            "success_rate": successful_executions / len(self.execution_history),
            "mean_execution_time": sum(execution_times) / len(execution_times),
            "max_execution_time": max(execution_times),
            "min_execution_time": min(execution_times),
        }
