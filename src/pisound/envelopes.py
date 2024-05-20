import asyncio

class Envelopes():
    def __init__(self, parent, frequency, envelope_values):
        self.parent = parent
        self.envelopes = []
        self.frequency = frequency
        self.envelope_values = envelope_values

    def add_envelope(self, envelope):
        self.envelopes.append(envelope)
        # self.envelope_values.append(0)
    
    def freq_to_sec(self, freq):
        return 1000/1000/freq

    async def run(self):
        while True:
            # self.parent._logger.debug('env cycle')
            for envelope in enumerate(self.envelopes):
                env_val = next(envelope[1])
                # print(f'updating envelope {envelope[0]} {env_val}')
                self.envelope_values[envelope[0]] = env_val
            await asyncio.sleep(self.freq_to_sec(self.frequency))