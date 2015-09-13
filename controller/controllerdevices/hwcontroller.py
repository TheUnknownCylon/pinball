

class HWController:

    def sync(self):
        """
        Syncs the hardware with the current software state.
        1. Output devices will get new instructions.
        2. The state of the input devices is read, and new events are triggered
           if there were changes.
        """
        raise NotImlemented()

    def activate(self, pin):
        raise NotImlemented()

    def deactivate(self, pin):
        raise NotImlemented()

    def toggle(self, pin):
        raise NotImlemented()
