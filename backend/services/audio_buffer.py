"""
Audio Buffer Service - Isolated audio handling for interview sessions.
"""

import time
from typing import List, Optional


class AudioBuffer:
    """
    Thread-safe audio buffer for collecting audio chunks during interview.
    
    Usage:
        buffer = AudioBuffer()
        buffer.add(audio_bytes)
        audio_data = buffer.bytes()
        buffer.clear()
    """

    def __init__(self, max_size_bytes: int = 20000000):
        """
        Initialize audio buffer.
        
        Args:
            max_size_bytes: Maximum buffer size in bytes (default 20MB)
        """
        self._chunks: List[bytes] = []
        self._total_bytes: int = 0
        self._max_size_bytes = max_size_bytes
        self._first_chunk_time: Optional[float] = None
        self._last_chunk_time: Optional[float] = None

    def add(self, chunk: bytes) -> bool:
        """
        Add an audio chunk to the buffer.
        
        Args:
            chunk: Raw audio bytes
            
        Returns:
            True if chunk was added, False if would exceed max size
        """
        if self._total_bytes + len(chunk) > self._max_size_bytes:
            return False
            
        self._chunks.append(chunk)
        self._total_bytes += len(chunk)
        
        now = time.time()
        if self._first_chunk_time is None:
            self._first_chunk_time = now
        self._last_chunk_time = now
        
        return True

    def bytes(self) -> bytes:
        """
        Get all buffered audio as single bytes object.
        
        Returns:
            Combined audio bytes
        """
        return b"".join(self._chunks)

    def clear(self) -> None:
        """Clear all buffered audio."""
        self._chunks.clear()
        self._total_bytes = 0
        self._first_chunk_time = None
        self._last_chunk_time = None

    @property
    def size_bytes(self) -> int:
        """Get current buffer size in bytes."""
        return self._total_bytes

    @property
    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        return self._total_bytes == 0

    @property
    def chunk_count(self) -> int:
        """Get number of chunks in buffer."""
        return len(self._chunks)

    @property
    def duration_seconds(self) -> float:
        """Get duration of buffered audio in seconds."""
        if self._first_chunk_time is None or self._last_chunk_time is None:
            return 0.0
        return max(0.0, self._last_chunk_time - self._first_chunk_time)

    def __len__(self) -> int:
        """Get total bytes in buffer."""
        return self._total_bytes

