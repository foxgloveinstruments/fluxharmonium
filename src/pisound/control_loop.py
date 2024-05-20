import asyncio

class ControlLoop:
    def __init__(self, parent, _frequency=200):
        self.parent = parent
        self.frequency = _frequency
        self.controls = []
        self.control_tasks = []
        self.event_loop = asyncio.get_event_loop()

    async def run(self):
        self.parent._logger.debug(f'running event loop')
        for control in self.controls:
            task = asyncio.create_task(control)
            self.control_tasks.append(task)
            asyncio.ensure_future(task)
        await asyncio.gather(*(c for c in self.control_tasks)) 

    def stop(self):
        self.event_loop.stop()
        self.parent._logger.debug(f'stopped event loop')

    def freq_to_ms(self, freq):
        return 1000/freq

    def freq_to_sec(self, freq):
        return 1000/1000/freq

    def add_control(self, control):
        self.controls.append(control)

    def output_control(self, value):
        print(value)

    async def update(self):
        for control in self.controls:
            control_value = next(control)
            self.output_control(control_value)
        # Is this the most accurate timing for coroutines ?
        await asyncio.sleep(self.freq_to_sec(self.frequency))
