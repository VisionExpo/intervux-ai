import asyncio
import os
from typing import Optional

from backend.utils.metrics import metrics
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class RuntimeMonitor:
    def __init__(self, interview_socket):
        self.interview_socket = interview_socket
        self.interval_s = float(os.getenv("RUNTIME_MONITOR_INTERVAL_S", "5"))
        self.stt_spike_threshold_s = float(os.getenv("STT_SPIKE_THRESHOLD_S", "4.0"))
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        self._running = False
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None

    async def _run(self):
        while self._running:
            try:
                self._record_socket_stats()
                self._record_stt_stats()
                self._record_gpu_stats()
            except Exception:
                metrics.record_error()
                logger.exception("Runtime monitor loop error")
            await asyncio.sleep(self.interval_s)

    def _record_socket_stats(self):
        stats = self.interview_socket.runtime_stats()
        metrics.record_gauge("active_sessions", stats["active_sessions"])
        metrics.record_gauge("queue_depth", stats["queue_depth"])
        metrics.record_gauge("max_concurrent_sessions", stats["max_concurrent_sessions"])

    def _record_stt_stats(self):
        recent_stt = metrics.recent_latency("phase_stt", 0.0)
        metrics.record_gauge("stt_last_latency_s", recent_stt)
        if recent_stt >= self.stt_spike_threshold_s:
            metrics.increment_counter("stt_latency_spikes")

    @staticmethod
    def _record_gpu_stats():
        try:
            import torch

            if not torch.cuda.is_available():
                metrics.record_gauge("gpu_memory_allocated_mb", 0.0)
                metrics.record_gauge("gpu_memory_reserved_mb", 0.0)
                return

            allocated = torch.cuda.memory_allocated(0) / (1024 * 1024)
            reserved = torch.cuda.memory_reserved(0) / (1024 * 1024)
            metrics.record_gauge("gpu_memory_allocated_mb", round(allocated, 2))
            metrics.record_gauge("gpu_memory_reserved_mb", round(reserved, 2))
        except Exception:
            metrics.record_gauge("gpu_memory_allocated_mb", 0.0)
            metrics.record_gauge("gpu_memory_reserved_mb", 0.0)
