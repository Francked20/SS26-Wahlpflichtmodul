import typing
from typing import Any, Callable, Literal

from pydantic import BaseModel
from pydantic.main import IncEx


class SolutionHolder(BaseModel):
    solution: typing.Union[str, int]

    @property
    def value(self) -> typing.Union[str, int]:
        return self.solution

    @property
    def type(self) -> type:
        return type(self.solution)

    @classmethod
    def create(cls, solution):
        return cls(solution=solution)


class Correct(SolutionHolder):
    pass


class Incorrect(SolutionHolder):
    pass


class TaskHint(BaseModel):
    hint_index: int
    hint: str
    multiplier: float = 1.0

    def __gt__(self, other: "TaskHint"):
        return self.multiplier > other.multiplier

    @classmethod
    def create(cls, hint_index, hint, multiplier=1.0):
        return TaskHint(hint_index=hint_index, hint=hint, multiplier=multiplier)
