import _asyncio

class ControlLoop:
    def __init__(self, _frequency=200):
        self.frequency = _frequency
        self.controls = []
        self.event_loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(self.event_loop)

    def run(self):
        asyncio.run(self._run_tasks())

    async def _run_tasks(self):
        await asyncio.gather(c for c in self.controls)

    def stop(self):
        pass

    def freq_to_ms(self, freq):
        return 1000/freq

    def freq_to_sec(self, freq):
        return 1000/1000/freq

    def add_control(self, control):
        self.controls.append(asyncio.create_task(control))

    def output_control(self, value):
        print(value)

    async def update(self):
        for control in self.controls:
            control_value = next(control)
            self.output_control(control_value)
        # Is this the most accurate timing for coroutines ?
        await asyncio.sleep(self.freq_to_sec(self.frequency))
