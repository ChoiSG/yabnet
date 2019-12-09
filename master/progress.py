import asyncio
import sys
import time
import itertools

global progress

progress = True



def get_progress():
    global progress
    return progress

async def define_progress():
    global progress
    print("progress started")
    await asyncio.sleep(2)
    progress = False
    print("progress ended")


async def run_spinner(msg):
    spinner = itertools.cycle(['-', '/', '|', '\\'])
    sys.stdout.write("{0} ".format(msg))
    while(get_progress()):
        sys.stdout.write("{0}".format(next(spinner)))
        sys.stdout.flush()
        time.sleep(0.2)
        sys.stdout.write('\b')
        await asyncio.sleep(1)


async def main():
    msg = "start logic"
    await asyncio.gather(run_spinner(msg), define_progress())


loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
finally:
    loop.close()