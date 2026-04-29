import asyncio
import os


async def tail_log_file(log_file: str):
    yield b": connected\n\n"

    loop = asyncio.get_event_loop()

    with open(log_file, "r", encoding="utf-8") as f:
        f.seek(0, 2)
        while True:
            line = await loop.run_in_executor(None, f.readline)
            if line:
                yield f"data: {line.rstrip()}\n\n".encode("utf-8")
            else:
                # Re-open if file was rotated (size reset = new file)
                try:
                    if os.path.getsize(log_file) < f.tell():
                        f.close()
                        f = open(log_file, "r", encoding="utf-8")
                except OSError:
                    pass
                await asyncio.sleep(0.3)