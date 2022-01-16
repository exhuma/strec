from typing import Iterable


class Colors:
    DATA = {
        "blue": "<blue>",
        "red": "<red>",
        "yellow": "<yellow>",
        "cyan": "<cyan>",
        "bold magenta": "<bold magenta>",
        "reset": "<reset>",
        "default": "<reset>",
        "unchanged": "<unchanged>",
    }

    @staticmethod
    def get(name: str) -> str:
        return Colors.DATA.get(name, "")

    @staticmethod
    def keys() -> Iterable[str]:
        return Colors.DATA.keys()
