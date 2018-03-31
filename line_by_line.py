import sys


class RunUntilEndLineByLine:
    def __init__(self, cmd, cwd):
        self.cmd = cmd
        self.cwd = cwd

    async def run(self, input_data):
        print('Starting the process', *self.cmd, 'in', self.cwd)
        self.process = await asyncio.create_subprocess_exec(
            *self.cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=sys.stderr,  # asyncio.subprocess.DEVNULL,
            cwd=self.cwd,
        )
        assert self.process.returncode is None, 'Failed to start cmd: {} in {}. Retcode: {}'.format(self.cmd, self.cwd, self.process.returncode)
        self.process.stdin.write(input_data)
        await self.process.stdin.drain()
        self.process.stdin.close()
        while True:
            print('Waiting for line from process')
            data = await self.process.stdout.readline()
            if data:
                print(data.strip())
            else:
                print('Finished')
                break

        exit_status = await self.process.wait()
        if exit_status != 0:
            raise Exception('Failed to run process properly')

if __name__ == '__main__':
    import asyncio
    import os


    async def main():
        runner = RunUntilEndLineByLine([sys.executable, 'backwards.py'], os.getcwd())
        await runner.run(b'one\ntwo\nthree\n')


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

