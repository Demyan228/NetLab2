from event_system import EventSystem as es
from common import log
import asyncio
class Assembler:
    _is_running = True
    @staticmethod
    async def create_model(layers) -> str:
        log("асемблинг начат")
        await asyncio.sleep(2)
        log("асеблинг заверешен")
        return f"Norm model with params" + '\n'.join([str(i) for i in layers])


    @staticmethod
    @es.subscribe("ASSEMBLE_MODEL_EVENT")
    async def run(assemble_data):
        model = await Assembler.create_model(assemble_data["layers"])
        if Assembler._is_running:
            await es.ainvoke('TRAIN_START_EVENT', {"model": model})

    @staticmethod
    @es.subscribe("APP_QUIT_EVENT")
    async def quit_handler(event_data):
        Assembler._is_running = False
        log('ASSEMBLER QUIT')
