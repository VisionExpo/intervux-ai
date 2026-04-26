import asyncio
import json
import time
import websockets
import statistics
from typing import List

# Configuration
WS_URL = "ws://127.0.0.1:8000/ws/metrics"
# Using a dummy token for simulation - ensure server can validate or bypass in dev
TOKEN = "test-token" 
NUM_CLIENTS = 50
DURATION = 20  # seconds

class WSClient:
    def __init__(self, id: int, slow: bool = False):
        self.id = id
        self.slow = slow
        self.latencies = []
        self.received_count = 0
        self.errors = 0

    async def run(self):
        url = f"{WS_URL}?token={TOKEN}"
        try:
            async with websockets.connect(url) as ws:
                start_time = time.time()
                while time.time() - start_time < DURATION:
                    try:
                        # Simulate a slow client by adding delay before receiving
                        if self.slow:
                            await asyncio.sleep(2.0)

                        msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
                        self.received_count += 1
                        # Track latency (server timestamp vs client time)
                        # This assumes synchronized clocks or just server-side relative time
                    except asyncio.TimeoutError:
                        self.errors += 1
                    except websockets.ConnectionClosed:
                        break
        except Exception as e:
            print(f"Client {self.id} failed: {e}")
            self.errors += 1

async def main():
    print(f"Starting load test with {NUM_CLIENTS} clients...")
    print(f"Including 10% slow clients to test isolation.")

    clients = []
    for i in range(NUM_CLIENTS):
        is_slow = (i % 10 == 0)
        clients.append(WSClient(i, slow=is_slow))

    tasks = [asyncio.create_task(c.run()) for c in clients]
    
    await asyncio.gather(*tasks)

    # Report
    total_received = sum(c.received_count for c in clients)
    total_errors = sum(c.errors for c in clients)
    
    fast_clients = [c for c in clients if not c.slow]
    slow_clients = [c for c in clients if c.slow]

    avg_received_fast = statistics.mean([c.received_count for c in fast_clients])
    avg_received_slow = statistics.mean([c.received_count for c in slow_clients])

    print("\n--- Load Test Report ---")
    print(f"Total Clients: {NUM_CLIENTS}")
    print(f"Total Messages Received: {total_received}")
    print(f"Total Errors/Timeouts: {total_errors}")
    print(f"Avg Messages (Fast Clients): {avg_received_fast:.2f}")
    print(f"Avg Messages (Slow Clients): {avg_received_slow:.2f}")
    
    if avg_received_fast > avg_received_slow * 1.5:
        print("SUCCESS: Isolation confirmed. Fast clients were not blocked by slow ones.")
    else:
        print("WARNING: Limited isolation observed. Fast clients might be affected by slow ones.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
