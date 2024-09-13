from abc import ABC, abstractmethod

import pandas as pd


class BaseWriter(ABC):
    def __init__(self, base_path):
        self.path = base_path
