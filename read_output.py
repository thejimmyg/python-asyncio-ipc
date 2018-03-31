import sys


class RunUntilEnd:
    def __init__(self, cmd, cwd):
        self.cmd = cmd
        self.cwd = cwd

    async def run(self):
        print('Starting the process', *self.cmd, 'in', self.cwd)
        self.process = await asyncio.create_subprocess_exec(
            *self.cmd,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=sys.stderr,  # asyncio.subprocess.DEVNULL,
            cwd=self.cwd,
        )
        print('Started')
        assert self.process.returncode is None, 'Failed to start cmd: {} in {}. Retcode: {}'.format(self.cmd, self.cwd, self.process.returncode)
        print('Running', self.process.returncode)
        (out, _) = await self.process.communicate()
        exit_status = await self.process.wait()
        if exit_status != 0:
            raise Exception('Failed to run process properly')
        print('All done', out)
        return out


if __name__ == '__main__':
    import asyncio
    import os

    async def main():
        process_manager = RunUntilEnd(cmd=[sys.executable, 'process_that_spits_out_for_lines.py'], cwd=os.getcwd())
        print('RESULT:', await process_manager.run())

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
