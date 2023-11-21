from abc import ABC, abstractmethod


class IM(ABC):
    @abstractmethod
    def get_nickname(self):
        pass

    @abstractmethod
    def send_message(self, receiver, message):
        pass
