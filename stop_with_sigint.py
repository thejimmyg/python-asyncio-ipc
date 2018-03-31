import sys
import signal


class RunAndStop:
    def __init__(self, cmd, cwd):
        self.cmd = cmd
        self.cwd = cwd

    async def start(self):
        print('Starting the process', *self.cmd, 'in', self.cwd)
        self.process = await asyncio.create_subprocess_exec(
            *self.cmd,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=sys.stdout,  # asyncio.subprocess.PIPE,
            stderr=sys.stderr,  # asyncio.subprocess.DEVNULL,
            cwd=self.cwd,
        )
        print('Started')
        assert self.process.returncode is None, 'Failed to start cmd: {} in {}. Retcode: {}'.format(self.cmd, self.cwd, self.process.returncode)
        print('Running', self.process.returncode)

    async def stop(self):
        if self.process.returncode is None:
            print('Sending SIGINT to process ...')
            self.process.send_signal(signal.SIGINT)
            print('done.')
            exit_status = await self.process.wait()
            if exit_status != 0:
                raise Exception('Failed to wait for process exit properly')
        return exit_status

if __name__ == '__main__':
    import asyncio
    import os

    async def main():
        process_manager = RunAndStop(cmd=[sys.executable, 'process_that_spits_out_lines.py'], cwd=os.getcwd())
        await process_manager.start()
        await asyncio.sleep(3)
        await process_manager.stop()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
