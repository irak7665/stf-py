# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod


class IM(ABC):
    @abstractmethod
    def start_whatsapp(self):
        pass

    @abstractmethod
    def input_message_click_send(self, receiver, message):
        pass
