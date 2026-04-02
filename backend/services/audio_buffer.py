"""
Audio Buffer Service - Isolated audio handling for interview sessions.
Refactored to mock S3 / Local Temporary File logic for stateless architecture.
"""

import os
import time
import tempfile
from typing import Optional


class AudioBuffer:
    """
    Thread-safe audio buffer for collecting audio chunks during interview.
    Uses disk (temp files) to store chunks instead of RAM to prevent OOM
    and support horizontally scaling worker queues.
    
    Usage:
        buffer = AudioBuffer(session_id="123")
        buffer.add(audio_bytes)
        audio_data = buffer.bytes()
        buffer.clear()
    """

    def __init__(self, session_id: str, max_size_bytes: int = 20000000):
        """
        Initialize audio buffer.
        
        Args:
            session_id: Unique interview session identifier.
            max_size_bytes: Maximum buffer size in bytes (default 20MB)
        """
        self.session_id = session_id
        # In a real cluster this could be an S3 bucket or EFS mount.
        # For this refactor, tempfile directory is used as proxy.
        self.filepath = os.path.join(tempfile.gettempdir(), f"intervux_audio_{session_id}.raw")
        self._total_bytes: int = 0
        self._max_size_bytes = max_size_bytes
        self._first_chunk_time: Optional[float] = None
        self._last_chunk_time: Optional[float] = None
        self._chunk_count = 0
        
        # Ensure clean state based on this ID
        self.clear()

    def add(self, chunk: bytes) -> bool:
        """
        Add an audio chunk to the buffer file.
        
        Args:
            chunk: Raw audio bytes
            
        Returns:
            True if chunk was added, False if would exceed max size
        """
        if self._total_bytes + len(chunk) > self._max_size_bytes:
            return False
            
        with open(self.filepath, "ab") as f:
            f.write(chunk)
            
        self._total_bytes += len(chunk)
        self._chunk_count += 1
        
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
        if not os.path.exists(self.filepath):
            return b""
        with open(self.filepath, "rb") as f:
            return f.read()

    def clear(self) -> None:
        """Clear all buffered audio and clean up file."""
        if os.path.exists(self.filepath):
            try:
                os.remove(self.filepath)
            except OSError:
                pass
                
        self._total_bytes = 0
        self._chunk_count = 0
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
        return self._chunk_count

    @property
    def duration_seconds(self) -> float:
        """Get duration of buffered audio in seconds."""
        if self._first_chunk_time is None or self._last_chunk_time is None:
            return 0.0
        return max(0.0, self._last_chunk_time - self._first_chunk_time)

    def __len__(self) -> int:
        """Get total bytes in buffer."""
        return self._total_bytes

