"""
TiTrATE Engine
==============

Time-Triggered Action with Temporal Expectations.
Manages action execution with temporal constraints and deadlines.
"""

from dataclasses import dataclass
from typing import Callable, Any, Optional, Dict
from enum import Enum
import time
import logging
import asyncio

logger = logging.getLogger(__name__)

class ExecutionStatus(Enum):
 """Status of action execution"""
 SUCCESS = "success"
 TIMEOUT = "timeout"
 FAILED = "failed"
 ABORTED = "aborted"

@dataclass
class TemporalConstraint:
 """Temporal constraint definition"""
 max_time: float # Maximum execution time (seconds)
 deadline: Optional[float] = None # Absolute deadline timestamp
 min_time: Optional[float] = None # Minimum execution time
 periodic: bool = False # Periodic execution
 period: Optional[float] = None # Period for periodic execution

@dataclass
class TiTrATEResult:
 """Result of TiTrATE execution"""
 status: ExecutionStatus
 result: Any
 execution_time: float
 constraint_met: bool
 metadata: Dict[str, Any]

class TiTrATEEngine:
 """
 Time-Triggered Action with Temporal Expectations Engine.

 Manages execution of actions with strict temporal constraints,
 ensuring deadlines are met and timing violations are detected.
 """

 def __init__(
 self,
 max_time: float = 5.0,
 enable_timeout: bool = True,
 enable_logging: bool = True
 ):
 """
 Initialize TiTrATE engine.

 Args:
 max_time: Default maximum execution time (seconds)
 enable_timeout: Enable timeout enforcement
 enable_logging: Enable execution logging
 """
 self.max_time = max_time
 self.enable_timeout = enable_timeout
 self.enable_logging = enable_logging

 self.execution_history = []

 logger.info(f"TiTrATEEngine initialized with max_time={max_time}s")

 def execute(
 self,
 action: Callable,
 constraint: Optional[TemporalConstraint] = None,
 *args,
 **kwargs
 ) -> TiTrATEResult:
 """
 Execute action with temporal constraint.

 Args:
 action: Callable to execute
 constraint: Temporal constraint (uses default if None)
 *args, **kwargs: Arguments for action

 Returns:
 TiTrATEResult with execution status and timing
 """
 # Use default constraint if not provided
 if constraint is None:
 constraint = TemporalConstraint(max_time=self.max_time)

 start_time = time.time()
 status = ExecutionStatus.SUCCESS
 result = None
 constraint_met = True

 try:
 if self.enable_timeout:
 # Execute with timeout
 result = self._execute_with_timeout(
 action, constraint.max_time, *args, **kwargs
 )
 else:
 # Execute without timeout
 result = action(*args, **kwargs)

 except TimeoutError:
 status = ExecutionStatus.TIMEOUT
 constraint_met = False
 logger.warning(
 f"Action execution timed out after {constraint.max_time}s"
 )

 except Exception as e:
 status = ExecutionStatus.FAILED
 constraint_met = False
 logger.error(f"Action execution failed: {e}")

 execution_time = time.time() - start_time

 # Check constraint satisfaction
 if constraint.deadline and time.time() > constraint.deadline:
 constraint_met = False
 status = ExecutionStatus.TIMEOUT

 if constraint.min_time and execution_time < constraint.min_time:
 constraint_met = False

 titrate_result = TiTrATEResult(
 status=status,
 result=result,
 execution_time=execution_time,
 constraint_met=constraint_met,
 metadata={
 "max_time": constraint.max_time,
 "deadline": constraint.deadline,
 "timestamp": start_time,
 }
 )

 self.execution_history.append(titrate_result)

 if self.enable_logging:
 logger.info(
 f"TiTrATE execution: status={status.value}, "
 f"time={execution_time:.3f}s, constraint_met={constraint_met}"
 )

 return titrate_result

 def _execute_with_timeout(
 self,
 action: Callable,
 timeout: float,
 *args,
 **kwargs
 ) -> Any:
 """Execute action with timeout enforcement"""
 import signal

 def timeout_handler(signum, frame):
 raise TimeoutError(f"Execution exceeded {timeout}s")

 # Set up timeout handler (Unix-like systems)
 try:
 old_handler = signal.signal(signal.SIGALRM, timeout_handler)
 signal.setitimer(signal.ITIMER_REAL, timeout)

 try:
 result = action(*args, **kwargs)
 finally:
 signal.setitimer(signal.ITIMER_REAL, 0)
 signal.signal(signal.SIGALRM, old_handler)

 return result

 except AttributeError:
 # Windows doesn't support SIGALRM, use threading
 import threading

 result = [None]
 exception = [None]

 def wrapper():
 try:
 result[0] = action(*args, **kwargs)
 except Exception as e:
 exception[0] = e

 thread = threading.Thread(target=wrapper)
 thread.daemon = True
 thread.start()
 thread.join(timeout)

 if thread.is_alive():
 raise TimeoutError(f"Execution exceeded {timeout}s")

 if exception[0]:
 raise exception[0]

 return result[0]

 async def execute_async(
 self,
 action: Callable,
 constraint: Optional[TemporalConstraint] = None,
 *args,
 **kwargs
 ) -> TiTrATEResult:
 """Async version of execute"""
 if constraint is None:
 constraint = TemporalConstraint(max_time=self.max_time)

 start_time = time.time()
 status = ExecutionStatus.SUCCESS
 result = None
 constraint_met = True

 try:
 result = await asyncio.wait_for(
 action(*args, **kwargs),
 timeout=constraint.max_time
 )

 except asyncio.TimeoutError:
 status = ExecutionStatus.TIMEOUT
 constraint_met = False

 except Exception as e:
 status = ExecutionStatus.FAILED
 constraint_met = False
 logger.error(f"Async action failed: {e}")

 execution_time = time.time() - start_time

 return TiTrATEResult(
 status=status,
 result=result,
 execution_time=execution_time,
 constraint_met=constraint_met,
 metadata={"max_time": constraint.max_time}
 )

 def get_statistics(self) -> Dict[str, Any]:
 """Get execution statistics"""
 if not self.execution_history:
 return {}

 successful = sum(
 1 for r in self.execution_history
 if r.status == ExecutionStatus.SUCCESS
 )

 times = [r.execution_time for r in self.execution_history]

 return {
 "total_executions": len(self.execution_history),
 "successful": successful,
 "success_rate": successful / len(self.execution_history),
 "avg_time": sum(times) / len(times),
 "max_time": max(times),
 "min_time": min(times),
 }
