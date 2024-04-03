import asyncio
from event_system import EventSystem as es, EventTypes
from components import Assembler, Trainer, GUI

class App:

    def __init__(self):
        self.gui = GUI()
        self.trainer = Trainer()
        self.assembler = Assembler()

    async def initialize(self):
        await es.ainvoke(EventTypes.START_APP)
        await es.run()

    def run(self):
        asyncio.run(self.initialize())


if __name__ == '__main__':
    app = App()
    app.run()
