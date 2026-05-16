import asyncio
import concurrent.futures

async def main():
    print(f"asyncio.CancelledError: {asyncio.CancelledError}")
    print(f"concurrent.futures.CancelledError: {concurrent.futures.CancelledError}")
    print(f"Is same? {asyncio.CancelledError is concurrent.futures.CancelledError}")
    
    # Check inheritance
    print(f"asyncio.CancelledError is BaseException? {issubclass(asyncio.CancelledError, BaseException)}")
    print(f"asyncio.CancelledError is Exception? {issubclass(asyncio.CancelledError, Exception)}")
    print(f"concurrent.futures.CancelledError is BaseException? {issubclass(concurrent.futures.CancelledError, BaseException)}")
    print(f"concurrent.futures.CancelledError is Exception? {issubclass(concurrent.futures.CancelledError, Exception)}")
    
    import anyio
    anyio_exc = anyio.get_cancelled_exc_class()
    print(f"anyio cancelled exception: {anyio_exc}")
    print(f"Is anyio same as asyncio? {anyio_exc is asyncio.CancelledError}")
    print(f"Is anyio same as concurrent.futures? {anyio_exc is concurrent.futures.CancelledError}")

if __name__ == "__main__":
    asyncio.run(main())
