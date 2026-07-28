import typing
from hashlib import sha256
import json

from pydantic import BaseModel, model_validator
from website.engine.tasks.helpers import Correct, SolutionHolder, TaskHint


class TaskData(BaseModel):
    day: int
    day_id: typing.Optional[int] = None

    task_type: typing.Literal["input", "select", "multiple", "regex"]
    master_task: bool = False

    points: int
    error_cost: int = 1

    question: typing.List[str]
    question_further: typing.List[str]
    placeholder_text: typing.List[str]

    hints: typing.List[TaskHint] = []
    answers: typing.Union[typing.List[SolutionHolder], typing.List[typing.List[SolutionHolder]]]

    # solutions: list[typing.Union[str, int]] = []
    solutions: typing.Union[list[str], list[list[str]]] = []

    options: list[str] | list[list[str]] = []

    download_text: typing.List[str]
    download_path: typing.List[str]

    link_text: typing.List[str]
    link_path: typing.List[str]

    day_description: str = ""
    task_description: str = ""

    injectible: bool = False
    allow_kali: bool = False
    allow_reset: bool = False
    allow_random_order: bool = False
    allow_download: bool = False
    allow_link: bool = False
    allow_vscode: bool = False
    allow_hints: bool = True
    allow_cyber_range: bool = False

    vm_name: typing.Optional[str] = None
    flag_type: typing.Optional[str] = None
    dynamic_check: typing.Optional[typing.Literal[
        "dh_factors", "dh_server_secret", "dh_master_secret", "dh_flag",
        "export_factor256", "export_factor512", "export_master_secret", "export_flag"
    ]] = None

    additional_urls: list[tuple[str, str]] = []

    @model_validator(mode="after")
    def sync_day(self):
        if self.day_id is None:
            assert isinstance(self.day, int)
            self.day_id = self.day
        return self

    # this is a temporary solution, run outside model validator!
    @model_validator(mode="after")
    def generate_solutions(self):
        task_type = self.task_type.lower()
        options = self.answers

        # set solutions
        if task_type in ["input"]:

            # Fall: answers = [SolutionHolder, ...]
            # → randomisiert mit genau einer Antwort pro Randomisierung
            if options and not isinstance(options[0], list):
                self.solutions = [
                    str(s.value) for s in options if isinstance(s, Correct)
                ]

            # Fall: answers = [[SolutionHolder, ...], ...]
            # → nicht randomisiert mit mehreren Antworten
            #   oder randomisiert mit mehreren Antworten pro Randomisierung
            else:
                self.solutions = [
                    [str(s.value) for s in group if isinstance(s, Correct)]
                    for group in options
                ]

        elif task_type in ["select"]:

            def recursive_unnest(obj, cast=None):
                if isinstance(obj, list):
                    yield from (x for o in obj for x in recursive_unnest(o, cast=cast))
                elif isinstance(obj, Correct):
                    yield cast(obj.value) if cast is not None else obj.value

            self.solutions = list(recursive_unnest(options, cast=str))

        elif task_type in ["multiple"]:
            if self.allow_random_order:
                self.solutions = [
                    "".join("1" if isinstance(s, Correct) else "0" for s in g) for g in options
                ]
            else:
                self.solutions = ["".join("1" if isinstance(s, Correct) else "0" for s in options)]

        else:
            raise ValueError(f"Unsupported task type: {task_type}")

        # print(f"SOLUTIONS of {self.day_id}/{self.question} in {self.task_type}: {self.solutions}")

        # set options
        if task_type in ["select", "multiple"]:
            if self.allow_random_order and len(self.question) > 1:
                self.options = [[str(s.value) for s in g] for g in self.answers]
            else:
                self.options = [str(s.value) for s in self.answers]

        return self

    @model_validator(mode="after")
    def sort_hints(self):
        # set correct ordering of things -> relevant within the api!
        self.hints = sorted(self.hints, key=lambda h: h.hint_index)
        self.hints = sorted(self.hints, key=lambda h: h.multiplier, reverse=True)
        return self

    def __repr__(self):
        return f"<Task day={self.day_id}) -> {self.question}>"


class TaskWidgetState(BaseModel):
    current_points: typing.Optional[int] = None
    maximum_points: int = 0

    question: str = "!!question!!"
    question_further: str = "!!question_further!!"
    placeholder_text: str = "!!placeholder!!"
    options: list[str] = []

    hints_point_cap: list[int] = []
    hints_unlocked: list[str] = []

    download_path: str = ""
    download_text: str = ""

    link_text: str = ""
    link_path: str = ""

    solved: bool = False
    first_blood: bool = False
    is_answerable: bool = True

    solution: str = ""


class TaskWidgetConfiguration(BaseModel):
    day_id: int
    task_id: int
    task_type: typing.Literal["input", "select", "multiple", "regex"]

    allow_hints: bool
    allow_vscode: bool

    injectible: bool
    allow_kali: bool
    allow_reset: bool
    allow_download: bool
    allow_link: bool
    allow_cyber_range: bool

    # additional_urls: list[tuple[str, str]]


class BackendRegister(TaskData, TaskWidgetConfiguration):
    """This class overwrites TaskWidgetConfiguration and TaskHint serialization."""

    sha256_checksum: str = None

    @model_validator(mode="after")
    def generate_solutions(self):
        return self

    # @computed_field
    @model_validator(mode="after")
    def set_checksum(self):
        fields = list(BackendRegister.model_fields.keys())
        data = {k: v for k, v in self if k in fields if k != "sha256_checksum"}

        obj = json.dumps(data, sort_keys=True, default=str)
        self.sha256_checksum = sha256(obj.encode()).hexdigest()

        return self
