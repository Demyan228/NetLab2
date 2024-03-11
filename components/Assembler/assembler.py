from event_system import EventSystem as es
from components.backend.PyTorchBackend import PyTorchBackend
from common import log


class Assembler:
    _is_running = True
    _backend = PyTorchBackend

    @staticmethod
    async def create_model(layers):
        model_file_path = await Assembler._backend.create_model(layers)
        return model_file_path


    @staticmethod
    @es.subscribe("ASSEMBLE_MODEL_EVENT")
    async def run(assemble_data):
        model_file_path = await Assembler.create_model(assemble_data["layers"])
        if Assembler._is_running:
            await es.ainvoke('TRAIN_START_EVENT', {"model_file_path": model_file_path})

    @staticmethod
    @es.subscribe("APP_QUIT_EVENT")
    async def quit_handler(event_data):
        Assembler._is_running = False
        log('ASSEMBLER QUIT')
