from config import debug


def log(*args, **kwargs):
    if debug:
        print(*args, **kwargs, flush=True)
