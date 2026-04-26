import pickle
import sys
import os
from enum import Enum
from typing import List, Optional, Dict

# Mock the InterviewPhase and InterviewState since we want to test them in isolation 
# or just import them if the path is set up correctly.
# For simplicity, I'll define the minimal versions here to verify the __getstate__ logic.

class InterviewPhase(Enum):
    CONNECTING = "CONNECTING"
    QUESTION = "QUESTION"

class InterviewState:
    def __init__(self):
        self._phase = InterviewPhase.CONNECTING
        self._on_phase_change_callbacks = []
        self.some_data = "hello"

    def subscribe(self, callback):
        self._on_phase_change_callbacks.append(callback)

    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove un-serializable callbacks before pickling
        state["_on_phase_change_callbacks"] = []
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        if "_on_phase_change_callbacks" not in self.__dict__:
            self._on_phase_change_callbacks = []

def test_callback(phase):
    print(f"Phase changed to {phase}")

def verify():
    state = InterviewState()
    
    # This is a local function (closure), which is normally NOT picklable
    def local_callback(p):
        print(f"Local: {p}")
        
    state.subscribe(local_callback)
    state.subscribe(test_callback)
    
    print(f"Callbacks before pickling: {len(state._on_phase_change_callbacks)}")
    
    try:
        data = pickle.dumps(state)
        print("Pickling successful!")
    except Exception as e:
        print(f"Pickling failed: {e}")
        return

    try:
        new_state = pickle.loads(data)
        print("Unpickling successful!")
        print(f"Callbacks after unpickling: {len(new_state._on_phase_change_callbacks)}")
        print(f"Data preserved: {new_state.some_data}")
        assert len(new_state._on_phase_change_callbacks) == 0
        assert new_state.some_data == "hello"
    except Exception as e:
        print(f"Unpickling failed: {e}")

if __name__ == "__main__":
    verify()
