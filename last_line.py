import asyncio
import sys
import os
import signal


class ProcessManager:
    def __init__(self, cmd=None, cwd=None):
        if cmd is None:
            cmd = [sys.executable, '-u', 'process_that_spits_out_lines.py']
        self.cmd = cmd
        if cwd is None:
            self.cwd = os.getcwd()
        self.running = [True]
        self.cur = None

    async def start(self):
        print('Starting ...')
        self.process = await asyncio.create_subprocess_exec(
            *self.cmd,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=sys.stderr, # asyncio.subprocess.DEVNULL,
            cwd=self.cwd
        )
        while self.running[0]:
            print('Waiting for data from process')
            data = await self.process.stdout.readline()
            if not data:
                print('No data, sleeping')
                await asyncio.sleep(1)
            self.cur = data.decode('utf8').strip()
            print(f'Got "{self.cur}"')

        print('Finished running start ...')

    async def current_location(self):
        print('Got request for location ...')
        count = 0
        while self.cur is None:
            print('Waiting for first line ...')
            count += 1
            await asyncio.sleep(1)
            if count == 10:
                return None
        print('Returning current value ...')
        return self.cur

    async def stop(self):
        print('Stopping ...')
        self.running[0] = False
        if self.process.returncode is None:
            print('Sending SIGINT to process ...')
            self.process.send_signal(signal.SIGINT)
            print('done.')
        await asyncio.sleep(1)
        if self.process.returncode is None:
            print('Terminating ...')
            self.process.terminate()
            print('done.')
        else:
            print('Return code from subprocess:', self.process.returncode)
            return self.process.returncode

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    async def main():
        process_manager = ProcessManager(cmd=None)
        started = loop.create_task(process_manager.start())
        print('FINAL VALUE:', await process_manager.current_location())
        await process_manager.stop()
        # Wait for started to finish
        await started

    loop.run_until_complete(main())
    loop.close()
