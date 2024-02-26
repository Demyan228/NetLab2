from event_system import EventSystem as es
from common import log
import asyncio
class Assembler:
    _is_running = True
    @staticmethod
    async def create_model(model_params) -> str:
        log("асемблинг начат")
        await asyncio.sleep(2)
        log("асеблинг заверешен")
        return f"Norm model with params {model_params[0]} {model_params[1]} {model_params[2]}"


    @staticmethod
    @es.subscribe("ASSEMBLE_MODEL_EVENT")
    async def run(assemble_data):
        model = await Assembler.create_model(assemble_data["model_params"])
        if Assembler._is_running:
            await es.ainvoke('TRAIN_START_EVENT', {"model": model})

    @staticmethod
    @es.subscribe("APP_QUIT_EVENT")
    async def quit_handler(event_data):
        Assembler._is_running = False