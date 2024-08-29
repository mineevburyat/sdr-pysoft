import asyncio

async def hackrf_sweep():
    proc = await asyncio.create_subprocess_exec('hackrf_sweep',
                                                stdout=asyncio.subprocess.PIPE)
    data = await proc.stdout.readline()
    line = data.decode("utf-8").rstrip()
    await proc.wait()
    return line