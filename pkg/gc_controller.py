"""
Garbage Collector control routines.
"""

import gc

__all__ = ['GCController']


class FreezerContextManager:
    """
    Automatically unfreeze GC.
    """

    def __init__(self, gc_controller):
        self._gcc = gc_controller

    def __enter__(self):
        pass

    def __exit__(self):
        self._gcc.unfreeze()


class GCController:
    """
    Garbage Collector controller.
    """

    def __init__(self):
        if 'freeze' in dir(gc):
            self._freeze = gc.freeze
            self._unfreeze = gc.unfreeze
        else:
            self._freeze = lambda: 0
            self._unfreeze = lambda: 0

    def freeze(self):
        self._freeze()

        return FreezerContextManager(self)

    def unfreeze(self):
        self._unfreeze()

    @staticmethod
    def collect():
        gc.collect()

    def __exit__(self):
        gc.collect()
