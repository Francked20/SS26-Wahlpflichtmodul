# import abc
# import asyncio
# import json
# import math
# import random
# import typing
# from dataclasses import dataclass, field
# from urllib.parse import quote
#
# import reflex as rx
# from reflex import Component
# from web.auth_lib import AuthCookie, PageAuthState, BackendRequests
# from web.auth_lib import BackendRequests as Backend
# from web.logger import create_logger
# from web.site_engine.task_conf import PlayerCardState
# from web.sites.general.challenge import CondState
#
# # from fastapi.encoders import jsonable_encoder
#
# logger = create_logger("task-engine")
# logger.propagate = False
#
#
# class SolutionHolder(abc.ABC):
#     def __init__(self, solution: typing.Union[str, int]):
#         self._solution = solution
#         self._type = type(solution)
#
#     @property
#     def value(self) -> typing.Union[str, int]:
#         return self._solution
#
#     @property
#     def type(self) -> type:
#         return self._type
#
#
# class Correct(SolutionHolder):
#     pass
#
#
# class Incorrect(SolutionHolder):
#     pass
#
#
# class TaskHint:
#     def __init__(self, hint_index: int, hint: str, multiplier: float = 1.0):
#         self.hint_index = hint_index
#         self._hint = hint
#         self.multiplier = multiplier
#
#     def __gt__(self, other: "TaskHint"):
#         return self.multiplier > other.multiplier
#
#     def to_backend_dict(self):
#         return self.multiplier, self._hint, self.hint_index
#
#
# @dataclass
# class TaskData:
#     day: int
#     points: int
#     task_type: typing.Literal["input", "select", "multiple", "regex"]
#     solutions: typing.Union[typing.List[SolutionHolder], typing.List[typing.List[SolutionHolder]]]
#     question: typing.List[str]
#     download_text: typing.List[str]
#     download_path: typing.List[str]
#     question_further: typing.List[str]
#     placeholder_text: typing.List[str]
#     error_cost: int = 1
#     allow_reset: bool = False
#     allow_random_order: bool = False
#     allow_download: bool = False
#     allow_vscode: bool = False
#     injectible: bool = False
#     allow_kali: bool = False
#     master_task: bool = False
#     hints: typing.List[TaskHint] = field(default_factory=list)
#
#
# class MetaTask:
#     _all_registered: dict[int, dict[int, "MetaTask"]] = {}
#     _raw_answers: typing.Union[
#         typing.List[SolutionHolder], typing.List[typing.List[SolutionHolder]]]
#
#     def __init__(self, answers: typing.Union[list[SolutionHolder], list[list[SolutionHolder]]],
#                  task_type: str, data: TaskData):
#
#         if task_type == "input":
#             self.correct: list[str] = [str(s.value) for s in answers if isinstance(s, Correct)]
#         elif task_type == "select":
#             if isinstance(answers[0], list):
#                 self.correct: list[str] = [str(s.value) for group in answers for s in group if
#                                            isinstance(s, Correct)]
#             else:
#                 self.correct: list[str] = [str(s.value) for s in answers if isinstance(s, Correct)]
#         elif task_type == "multiple":
#             if isinstance(answers[0], list):
#                 self.correct: list[str] = [
#                     str(sum([isinstance(s, Correct) * pow(2, i) for i, s in enumerate(group)]))
#                     for group in answers
#                 ]
#             else:
#                 self.correct: list[str] = [str(sum(
#                     [isinstance(s, Correct) * pow(2, i) for i, s in enumerate(answers)]
#                 ))]
#         else:
#             raise ValueError(f"Unsuppogrted task type: {task_type}")
#
#         self._raw_answers = answers
#
#         self.task_type: str = task_type
#         self.day: int = data.day
#         self.task: typing.Optional[int] = None
#         self.error_cost: int = data.error_cost
#         self.allow_reset: bool = data.allow_reset
#         self.allow_random_order: bool = data.allow_random_order
#         self.allow_download: bool = data.allow_download
#         self.allow_vscode: bool = data.allow_vscode
#         self.injectible: bool = data.injectible
#         self.allow_kali: bool = data.allow_kali
#         self.master_task: bool = data.master_task
#         self.points = data.points
#         self.hints = data.hints
#         self.question = data.question
#         self.download_text = data.download_text
#         self.download_path = data.download_path
#         self.question_further = data.question_further
#         self.placeholder_text = data.placeholder_text
#
#     def register(self) -> int:
#         logger.error(f"Registering with {self.day}")
#
#         if self.day not in MetaTask._all_registered:
#             MetaTask._all_registered[self.day] = {}
#
#         index = len(MetaTask._all_registered[self.day])
#         self.task = index
#
#         # instance.day = self.day
#         # instance.task = self.task
#
#         logger.info(f"Registered task {index} on day {self.day} (type: {self.task_type})")
#         return index
#
#     @staticmethod
#     def iter() -> typing.Generator["MetaTask", None, None]:
#         for day in MetaTask._all_registered.values():
#             for task in day.values():
#                 yield task
#
#     def _to_backend_type(self):
#         if self.task_type in ["regex"]:
#             raise NotImplementedError()
#         elif self.task_type in ["input"]:
#             return "input"
#         elif self.task_type in ["select"]:
#             return "select"
#         elif self.task_type in ["multiple"]:
#             return "multiple"
#
#         else:
#             raise ValueError("Invalid task type")
#
#     def to_backend_dict(self) -> dict:
#         hints = sorted([x.to_backend_dict() for x in self.hints], key=lambda x: x[2], reverse=True)
#
#         if self.task_type in ["select", "multiple"]:
#             if isinstance(self.correct, list) and isinstance(self.correct[0], str) and hasattr(self,
#                                                                                                "question") and len(
#                     self.question) > 1:
#                 # Multi-question task
#                 options = [
#                     [str(s.value) for s in group]
#                     for group in self._raw_answers
#                 ]
#             else:
#                 # Single-question task
#                 options = [str(s.value) for s in self._raw_answers]
#         else:
#             options = []
#
#         return {
#             "day": self.day,
#             "task": self.task,
#             "points": self.points,
#             "error_cost": self.error_cost,
#             "allow_reset": self.allow_reset,
#             "allow_random_order": self.allow_random_order,
#             "allow_download": self.allow_download,
#             "allow_vscode": self.allow_vscode,
#             "injectible": self.injectible,
#             "allow_kali": self.allow_kali,
#             "master_task": self.master_task,
#             "question": self.question,
#             "question_further": self.question_further,
#             "placeholder_text": self.placeholder_text,
#             "download_text": self.download_text,
#             "download_path": self.download_path,
#             "solution": self.correct,
#             "solution_type": self._to_backend_type(),
#             "hints": hints,
#             "options": options
#         }
#
#
# class _TaskWidgetClass(BackendRequests, rx.ComponentState):
#     _task_type: typing.Literal["input", "select", "multiple", "regex"]
#     _answers: typing.List[SolutionHolder]
#     day: int = -1
#     task: int = -1
#     challenge_index: int = -1
#     points: int = 0
#
#     hint_costs: list[float] = [0.5, 0.3, 0.2, 0.1]
#     requested_hints: list[str] = []
#
#     username: str = "??"
#
#     question: str = ""
#     question_further: str = ""
#     placeholder_text: str = ""
#
#     download_text: str = ""
#     download_path: str = ""
#
#     resets: int = 0
#
#     max_points: int = -1
#     abs_points: int = -1
#     possible_points: int = -1
#
#     send_cooldown: bool = False
#     send_vscode_cooldown: bool = False
#     send_kali_cooldown: bool = False
#     answer_state: str | int = ""
#     solved_task: bool = False
#     has_attempted_solve: bool = False
#     is_first_blood = False
#     is_answerable = True
#
#     options: list[str] = []
#
#     solution: str = ""
#
#     @staticmethod
#     def build_hint(text: str, index: int) -> rx.Component:
#         return rx.callout.root(
#             rx.callout.icon(rx.icon("lightbulb"), margin_right="0.5rem"),
#             rx.callout.text(f"Hinweis {index + 1}: {text}"),
#             icon="info",
#             color_scheme="yellow",
#             width="100%",
#             # high_contrast=True,
#         )
#
#     @staticmethod
#     def build_info() -> rx.Component:
#         return rx.callout.root(
#             rx.callout.icon(rx.icon("info"), margin_right="0.5rem"),
#             rx.callout.text(f"Info: Nur der Team Leader kann Antworten einloggen"),
#             icon="info",
#             color_scheme="blue",
#             width="100%",
#             # high_contrast=True,
#         )
#
#     @rx.event()
#     async def hehehe(self):
#         logger.error(f"HEHEHE: {self.day}/{self.task}")
#
#     @rx.event()
#     async def load_state_uniform(self, force: bool = False, load_name: bool = False,
#                                  solved: bool = None, has_attempted: bool = None,
#                                  reset_answer_field: bool = False):
#         if reset_answer_field:
#             if type(self.answer_state) == str:
#                 self.answer_state = ""
#             else:
#                 self.answer_state = 0
#
#         if load_name or self.username == "??":
#             self.username: str = await self.get_var_value(AuthCookie.get_username)
#
#             # import sys
#
#             # logger.error(str(self.username))
#             # logger.error(str(type(self.username)))
#
#             # print(self.username, file=sys.stderr)
#             # print(type(self.username), file=sys.stderr)
#             # raise ValueError()
#
#             if self.username == "??":
#                 logger.warning("Username not set yet, cannot load state")
#                 return None
#
#         if self.username == "??":
#             return None
#         elif self.username == "":
#             # ToDo: check if this really works here
#             return PageAuthState.to_error_page()
#
#         safe_username = quote(self.username, safe="")
#
#         # ToDo: why are day and task ids always the last one loaded!?
#         logger.error(f"Loading state for {self.day}/{self.task}.")
#
#         token = await self.get_var_value(AuthCookie.auth_cookie)
#         response = await self.get(
#             f"/user/{safe_username}/challenges_dataset/{self.day}/{self.task}",
#             auth=token
#         )
#
#         if response.status_code == 401:
#             return PageAuthState.to_error_page()
#
#         elif response.status_code >= 300:
#             logger.error(f"An unexpected error occurred ({response.status_code}: {response.text})")
#             raise Exception(f"An unexpected error occurred ({response.status_code})")
#
#         data = response.json()
#
#         self.options = data["options"]
#         self.challenge_index = data["challenge_index"]
#
#         # logger.error(self.question)
#         self.question = data["question"]
#         # logger.error(self.question)
#
#         self.question_further = data["question_further"]
#         self.placeholder_text = data["placeholder_text"]
#
#         self.download_text = data["download_text"]
#         self.download_path = data["download_path"]
#
#         self.abs_points = data["abs_points"]
#         self.max_points = data["max_points"]
#         self.possible_points = data["possible_points"]
#         self.is_first_blood = data["first_blood"]
#         self.is_answerable = data["is_answerable"]
#
#         if solved is None:
#             self.solved_task = bool(data["solved"])
#         else:
#             self.solved_task = solved
#
#         if has_attempted is not None:
#             self.has_attempted_solve = has_attempted
#
#         self.hint_costs = data["hint_weights"]
#         self.requested_hints = data["hint_unlocked"]
#         self.resets = data["resets"]
#
#         self.solution = data["solution"]
#
#         if not self.is_answerable and not force:
#             return PlayerCardState.reset_day_ready(self.day)
#         return None
#
#     def _register_task(self, data: TaskData):
#         meta_task = MetaTask(self._answers, self._task_type, data)
#         index = meta_task.register()
#         self.__fields__["task"].default = index
#         return index
#
#     def set_checkbox(self, value: bool, position: int):
#         if value:
#             self.answer_state |= 1 << position
#         else:
#             self.answer_state &= ~(1 << position)
#
#     @rx.event(background=True)
#     async def button_cooldown(self):
#         async with self:
#             self.send_cooldown = True
#         await asyncio.sleep(3)
#         async with self:
#             self.send_cooldown = False
#
#     @rx.event(background=True)
#     async def vscode_button_cooldown(self):
#         async with self:
#             self.send_vscode_cooldown = True
#         await asyncio.sleep(7)
#         async with self:
#             self.send_vscode_cooldown = False
#
#     @rx.event(background=True)
#     async def kali_button_cooldown(self):
#         async with self:
#             self.send_kali_cooldown = True
#         await asyncio.sleep(7)
#         async with self:
#             self.send_kali_cooldown = False
#
#     async def reset_challenge(self):
#         logger.info(f"Resetting day {self.day} task {self.task} for {self.username}")
#
#         token = await self.get_var_value(AuthCookie.auth_cookie)
#         response = await self.post(
#             "/challenges/reset",
#             params={
#                 "day": self.day,
#                 "task": self.task,
#             },
#             auth=token,
#         )
#         if response.status_code == 401:
#             return PageAuthState.to_error_page()
#
#         if response.status_code >= 300:
#             raise Exception(f"An unexpected error occurred ({response.status_code})")
#
#         await self.load_state_uniform(force=True, solved=None, has_attempted=False,
#                                       reset_answer_field=True)
#
#         return PlayerCardState.reset_day_ready(self.day)
#
#     async def solve_challenge(self):
#         logger.info(f"Submitting answer for {self.username}")
#
#         token = await self.get_var_value(AuthCookie.auth_cookie)
#         response = await self.post(
#             "/challenges/solve",
#             params={
#                 "day": self.day,
#             "task": self.task,
#                 "solution": str(self.answer_state),
#             },
#             auth=token,
#         )
#         if response.status_code == 401:
#             return PageAuthState.to_error_page()
#
#         if response.status_code >= 300:
#             raise Exception(f"An unexpected error occurred ({response.status_code})")
#
#         result = response.json().get("answer_correct", False)
#
#         await self.load_state_uniform(force=True, solved=result, has_attempted=True)
#
#         return PlayerCardState.reset_day_ready(self.day)
#
#     async def request_hint(self):
#         logger.info(f"Requesting hint for {self.username}")
#
#         token = await self.get_var_value(AuthCookie.auth_cookie)
#         response = await self.post(
#             "/challenges/hint",
#             params={
#                 "day": self.day,
#                 "task": self.task,
#             },
#             auth=token,
#         )
#
#         if response.status_code == 401:
#             return PageAuthState.to_error_page()
#
#         if response.status_code >= 300:
#             logger.error(f"An unexpected error occurred ({response.status_code}: {response.text})")
#             raise Exception(f"An unexpected error occurred ({response.status_code})")
#
#         result = response.json().get("hint_unlocked", False)
#         if result:
#             await self.load_state_uniform(force=True)
#
#         return None
#
#     @classmethod
#     def get_component(cls, data: TaskData, *args, **kwargs):
#         import hashlib
#         from dataclasses import asdict
#         cls_hash = hashlib.sha256(
#             json.dumps(asdict(data), default=str, allow_nan=True).encode()).hexdigest()
#         logger.critical(f"CALLED with {cls_hash=} {data.day=}")
#
#         # logger.error(data.question)
#         if not (
#                 isinstance(data.solutions, list) and
#                 len(data.solutions) > 0 and
#                 (all(isinstance(t, SolutionHolder) for t in data.solutions) or all(
#                     isinstance(t, list) for t in data.solutions))
#         ):
#             raise ValueError("Invalid solution type")
#
#         # return rx.text(f"HERE: {data}")
#
#         if data.task_type == "input":
#             answer_field = rx.input(
#                 placeholder=cls.placeholder_text,
#                 type="text",
#                 value=cls.answer_state,
#                 on_change=cls.set_answer_state,
#                 disabled=cls.solved_task,
#                 size="3",
#                 width="100%",
#             )
#
#         elif data.task_type == "select":
#             answer_field = rx.radio(
#                 cls.options,
#                 on_change=cls.set_answer_state,
#                 disabled=cls.solved_task,
#                 size="3",
#             )
#
#         elif data.task_type == "multiple":
#             cls.__fields__["answer_state"].default = 0
#             answer_field = rx.vstack(
#                 rx.foreach(
#                     cls.options,
#                     lambda s, i: rx.checkbox(
#                         s,
#                         size="3",
#                         on_change=lambda val, idx=i: cls.set_checkbox(val, idx),
#                         disabled=cls.solved_task,
#                     )
#                 )
#             )
#
#         else:
#             raise ValueError("Invalid task type")
#
#         # import hashlib
#         # from dataclasses import asdict
#         # logger.error(f"dataclass: {hashlib.sha256(json.dumps(asdict(data), default=str, allow_nan=True).encode()).hexdigest()}")
#
#         cls._task_type = data.task_type
#         cls._answers = data.solutions
#         cls.__fields__["day"].default = data.day
#         cls.__fields__["points"].default = data.points
#         cls._allow_reset = data.allow_reset
#         cls._allow_download = data.allow_download
#         cls._allow_vscode = data.allow_vscode
#         cls._injectible = data.injectible
#         cls._allow_kali = data.allow_kali
#
#         cls._register_task(cls, data)  # noqa
#
#         # logger.error(f"Getting component of day {cls.day.to_string()}/{index}")
#
#         def answer_button():
#             def button_base(icon: str, text: str) -> rx.Component:
#                 return rx.button(
#                     rx.icon(icon),
#                     rx.text(text),
#                     size="3",
#                     color_scheme="blue",
#                     on_click=[
#                         cls.button_cooldown,
#                         cls.solve_challenge,
#                     ],
#                     disabled=cls.send_cooldown | cls.solved_task | (cls.answer_state == "") | (
#                                 cls.answer_state == 0),
#                 )
#
#             def vscode_button_base(icon: str, text: str) -> rx.Component:
#                 return rx.button(
#                     rx.icon(icon),
#                     rx.text(text),
#                     size="3",
#                     color_scheme="mint",
#                     on_click=[
#                         cls.vscode_button_cooldown,
#                         lambda: CondState.start_code_server(),
#                     ],
#                     disabled=cls.send_vscode_cooldown | cls.solved_task,
#                 )
#
#             def kali_button_base(icon: str, text: str) -> rx.Component:
#                 return rx.button(
#                     rx.icon(icon),
#                     rx.text(text),
#                     size="3",
#                     color_scheme="mint",
#                     on_click=[
#                         cls.kali_button_cooldown,
#                         lambda: CondState.start_kali_server(),
#                     ],
#                     disabled=cls.send_kali_cooldown | cls.solved_task,
#                 )
#
#             return rx.hstack(
#                 rx.cond(
#                     cls.solved_task,
#                     button_base("party-popper", "Gelöst!"),
#                     rx.cond(
#                         cls.send_cooldown,
#                         button_base("clock", "Cooldown"),
#                         button_base("send", "Überprüfen"),
#                     )
#                 ),
#                 rx.cond(
#                     (
#                             (
#                                 math.floor(
#                                     cls.possible_points <=
#                                     (
#                                             cls.abs_points *
#                                             cls.hint_costs[cls.requested_hints.length()]
#                                     )
#                                 )
#                             ) &
#                             (cls.possible_points > 0)
#                     ) |
#                     (
#                             (cls.possible_points == 0) &
#                             (cls.requested_hints.length() < cls.hint_costs.length())
#                     ),
#                     rx.button(
#                         rx.icon("lightbulb"),
#                         rx.text.strong("Gratis-Hinweis"),
#                         size="3",
#                         color_scheme="yellow",
#                         on_click=[cls.request_hint],
#                         disabled=cls.solved_task,
#                     ),
#                     rx.alert_dialog.root(
#                         rx.alert_dialog.trigger(
#                             rx.button(
#                                 rx.icon("lightbulb"),
#                                 rx.cond(
#                                     hints := cls.requested_hints.length() < cls.hint_costs.length(),
#                                     rx.text("Hinweis anfordern"),
#                                     rx.text("Keine Hinweise verfügbar"),
#                                 ),
#                                 size="3",
#                                 color_scheme="amber",
#                                 variant="soft",
#                                 disabled=cls.solved_task | ~hints,
#                             )
#                         ),
#                         rx.alert_dialog.content(
#                             rx.alert_dialog.title(
#                                 f"{cls.requested_hints.length() + 1}. Hinweis Anfordern?"),
#                             rx.alert_dialog.description(
#                                 rx.markdown(
#                                     "Der nächste Hinweis wird die maximale Punktzahl für diese Aufgabe auf nur "
#                                     f"**{math.floor(cls.abs_points * cls.hint_costs[cls.requested_hints.length()])} Punkte** "  # noqa
#                                     "begrenzen. Trotzdem fortfahren?"
#                                 ),
#                                 size="2",
#                             ),
#                             rx.flex(
#                                 rx.alert_dialog.cancel(
#                                     rx.button(
#                                         "Abbrechen",
#                                         size="2",
#                                         variant="soft",
#                                         color_scheme="gray",
#                                     )
#                                 ),
#                                 rx.alert_dialog.action(
#                                     rx.button(
#                                         rx.icon("lightbulb"),
#                                         rx.text.strong("Anfordern"),
#                                         size="2",
#                                         color_scheme="yellow",
#                                         on_click=[cls.request_hint],
#                                     )
#                                 ),
#                                 spacing="3",
#                                 margin_top="16px",
#                                 justify="end",
#                             ),
#                         ),
#                     ),
#                 ),
#
#                 rx.cond(
#                     cls._allow_reset | PlayerCardState.allow_task_reset,
#                     rx.cond(
#                         cls.solved_task,
#                         rx.alert_dialog.root(
#                             rx.alert_dialog.trigger(
#                                 rx.button(
#                                     rx.icon("rotate-ccw"),
#                                     rx.text("Reset"),
#                                     size="3",
#                                     color_scheme="red",
#                                     variant="soft",
#                                     disabled=~cls.solved_task,
#                                 )
#                             ),
#                             rx.alert_dialog.content(
#                                 rx.alert_dialog.title("Reset durchführen?"),
#                                 rx.alert_dialog.description(
#                                     rx.markdown(
#                                         "Der Reset wird den gelösten Task zurücksetzen. Fortfahren?"
#                                     ),
#                                     size="2",
#                                 ),
#                                 rx.flex(
#                                     rx.alert_dialog.cancel(
#                                         rx.button(
#                                             "Abbrechen",
#                                             size="2",
#                                             variant="soft",
#                                             color_scheme="gray",
#                                         )
#                                     ),
#                                     rx.alert_dialog.action(
#                                         rx.button(
#                                             rx.icon("rotate-ccw"),
#                                             rx.text.strong("Reset"),
#                                             size="2",
#                                             color_scheme="red",
#                                             on_click=[cls.reset_challenge],
#                                         )
#                                     ),
#                                     spacing="3",
#                                     margin_top="16px",
#                                     justify="end",
#                                 ),
#                             ),
#                         ),
#                         rx.button(
#                             rx.icon("rotate-ccw"),
#                             rx.text.strong("Reset"),
#                             size="3",
#                             color_scheme="red",
#                             disabled=True,
#                         ),
#                     ),
#                 ),
#                 rx.cond(
#                     cls._allow_vscode,
#                     rx.cond(
#                         ((CondState.code_server_running) & (~cls.send_vscode_cooldown)),
#                         rx.alert_dialog.root(
#                             rx.alert_dialog.trigger(
#                                 rx.button(
#                                     rx.icon("ban"),
#                                     rx.text("VSCode stoppen"),
#                                     size="3",
#                                     color_scheme="red",
#                                     variant="soft",
#                                 )
#                             ),
#                             rx.alert_dialog.content(
#                                 rx.alert_dialog.title("VSCode stoppen?"),
#                                 rx.alert_dialog.description(
#                                     rx.markdown(
#                                         "Dies wird den VSCode Container beenden. Fortfahren?"
#                                     ),
#                                     size="2",
#                                 ),
#                                 rx.flex(
#                                     rx.alert_dialog.cancel(
#                                         rx.button(
#                                             "Abbrechen",
#                                             size="2",
#                                             variant="soft",
#                                             color_scheme="gray",
#                                         )
#                                     ),
#                                     rx.alert_dialog.action(
#                                         rx.button(
#                                             rx.icon("ban"),
#                                             rx.text.strong("VSCode stoppen"),
#                                             size="2",
#                                             color_scheme="red",
#                                             on_click=lambda: CondState.stop_code_server(),
#                                         )
#                                     ),
#                                     spacing="3",
#                                     margin_top="16px",
#                                     justify="end",
#                                 ),
#                             ),
#                         ),
#                         rx.cond(
#                             cls.send_vscode_cooldown,
#                             vscode_button_base("clock", "VSCode startet"),
#                             vscode_button_base("files", "VSCode starten"),
#                         )
#                     ),
#                 ),
#
#                 rx.cond(
#                     cls._allow_kali,
#                     rx.cond(
#                         ((CondState.kali_server_running) & (~cls.send_kali_cooldown)),
#                         rx.alert_dialog.root(
#                             rx.alert_dialog.trigger(
#                                 rx.button(
#                                     rx.icon("ban"),
#                                     rx.text("Kali stoppen"),
#                                     size="3",
#                                     color_scheme="red",
#                                     variant="soft",
#                                 )
#                             ),
#                             rx.alert_dialog.content(
#                                 rx.alert_dialog.title("Kali stoppen?"),
#                                 rx.alert_dialog.description(
#                                     rx.markdown(
#                                         "Dies wird den Kali Container beenden. Fortfahren?"
#                                     ),
#                                     size="2",
#                                 ),
#                                 rx.flex(
#                                     rx.alert_dialog.cancel(
#                                         rx.button(
#                                             "Abbrechen",
#                                             size="2",
#                                             variant="soft",
#                                             color_scheme="gray",
#                                         )
#                                     ),
#                                     rx.alert_dialog.action(
#                                         rx.button(
#                                             rx.icon("ban"),
#                                             rx.text.strong("Kali stoppen"),
#                                             size="2",
#                                             color_scheme="red",
#                                             on_click=lambda: CondState.stop_kali_server(),
#                                         )
#                                     ),
#                                     spacing="3",
#                                     margin_top="16px",
#                                     justify="end",
#                                 ),
#                             ),
#                         ),
#                         rx.cond(
#                             cls.send_kali_cooldown,
#                             kali_button_base("clock", "Kali startet"),
#                             kali_button_base("swords", "Kali starten"),
#                         )
#
#                     ),
#                 ),
#
#             )
#
#         def refresh_button():
#             def button_base(icon: str, text: str) -> rx.Component:
#                 return rx.button(
#                     rx.icon(icon),
#                     rx.text(text),
#                     size="3",
#                     color_scheme="blue",
#                     on_click=[
#                         cls.button_cooldown,
#                         lambda: cls.load_state_uniform(False, True),
#                     ],
#                     disabled=cls.send_cooldown | cls.solved_task,
#                 )
#
#             def vscode_button_base(icon: str, text: str) -> rx.Component:
#                 return rx.button(
#                     rx.icon(icon),
#                     rx.text(text),
#                     size="3",
#                     color_scheme="mint",
#                     on_click=[
#                         cls.vscode_button_cooldown,
#                         lambda: CondState.start_code_server(),
#                     ],
#                     disabled=cls.send_vscode_cooldown | cls.solved_task,
#                 )
#
#             def kali_button_base(icon: str, text: str) -> rx.Component:
#                 return rx.button(
#                     rx.icon(icon),
#                     rx.text(text),
#                     size="3",
#                     color_scheme="mint",
#                     on_click=[
#                         cls.kali_button_cooldown,
#                         lambda: CondState.start_kali_server(),
#                     ],
#                     disabled=cls.send_kali_cooldown | cls.solved_task,
#                 )
#
#             return rx.hstack(
#                 rx.cond(
#                     cls.solved_task,
#                     button_base("party-popper", "Gelöst!"),
#                     rx.cond(
#                         cls.send_cooldown,
#                         button_base("clock", "Cooldown"),
#                         button_base("refresh-cw", "Refresh"),
#                     )
#                 ),
#
#                 rx.cond(
#                     cls._allow_vscode,
#                     rx.cond(
#                         ((CondState.code_server_running) & (~cls.send_vscode_cooldown)),
#                         rx.alert_dialog.root(
#                             rx.alert_dialog.trigger(
#                                 rx.button(
#                                     rx.icon("ban"),
#                                     rx.text("VSCode stoppen"),
#                                     size="3",
#                                     color_scheme="red",
#                                     variant="soft",
#                                 )
#                             ),
#                             rx.alert_dialog.content(
#                                 rx.alert_dialog.title("VSCode stoppen?"),
#                                 rx.alert_dialog.description(
#                                     rx.markdown(
#                                         "Dies wird den VSCode Container beenden. Fortfahren?"
#                                     ),
#                                     size="2",
#                                 ),
#                                 rx.flex(
#                                     rx.alert_dialog.cancel(
#                                         rx.button(
#                                             "Abbrechen",
#                                             size="2",
#                                             variant="soft",
#                                             color_scheme="gray",
#                                         )
#                                     ),
#                                     rx.alert_dialog.action(
#                                         rx.button(
#                                             rx.icon("ban"),
#                                             rx.text.strong("VSCode stoppen"),
#                                             size="2",
#                                             color_scheme="red",
#                                             on_click=lambda: CondState.stop_code_server(),
#                                         )
#                                     ),
#                                     spacing="3",
#                                     margin_top="16px",
#                                     justify="end",
#                                 ),
#                             ),
#                         ),
#                         rx.cond(
#                             cls.send_vscode_cooldown,
#                             vscode_button_base("clock", "VSCode startet"),
#                             vscode_button_base("files", "VSCode starten"),
#                         )
#                     ),
#                 ),
#
#                 rx.cond(
#                     cls._allow_kali,
#                     rx.cond(
#                         ((CondState.kali_server_running) & (~cls.send_kali_cooldown)),
#                         rx.alert_dialog.root(
#                             rx.alert_dialog.trigger(
#                                 rx.button(
#                                     rx.icon("ban"),
#                                     rx.text("Kali stoppen"),
#                                     size="3",
#                                     color_scheme="red",
#                                     variant="soft",
#                                 )
#                             ),
#                             rx.alert_dialog.content(
#                                 rx.alert_dialog.title("Kali stoppen?"),
#                                 rx.alert_dialog.description(
#                                     rx.markdown(
#                                         "Dies wird den Kali Container beenden. Fortfahren?"
#                                     ),
#                                     size="2",
#                                 ),
#                                 rx.flex(
#                                     rx.alert_dialog.cancel(
#                                         rx.button(
#                                             "Abbrechen",
#                                             size="2",
#                                             variant="soft",
#                                             color_scheme="gray",
#                                         )
#                                     ),
#                                     rx.alert_dialog.action(
#                                         rx.button(
#                                             rx.icon("ban"),
#                                             rx.text.strong("Kali stoppen"),
#                                             size="2",
#                                             color_scheme="red",
#                                             on_click=lambda: CondState.stop_kali_server(),
#                                         )
#                                     ),
#                                     spacing="3",
#                                     margin_top="16px",
#                                     justify="end",
#                                 ),
#                             ),
#                         ),
#                         rx.cond(
#                             cls.send_kali_cooldown,
#                             kali_button_base("clock", "Kali startet"),
#                             kali_button_base("swords", "Kali starten"),
#                         )
#
#                     ),
#                 ),
#
#             )
#
#         def answer_banner():
#             return rx.cond(
#                 cls.has_attempted_solve,
#                 rx.cond(
#                     cls.solved_task,
#                     rx.vstack(
#                         rx.callout(
#                             f"Richtige Antwort! {cls.possible_points} Punkte erhalten.",
#                             icon="check",
#                             color_scheme="green",
#                             width="100%",
#                             # high_contrast=True,
#                         ),
#                         rx.cond(PlayerCardState.show_answers,
#                                 rx.callout(
#                                     f"{cls.solution}",
#                                     icon="info",
#                                     color_scheme="blue",
#                                     width="100%",
#                                     # high_contrast=True,
#                                 ),
#                                 ),
#                     ),
#                     rx.callout(
#                         "Die Antwort ist falsch!",
#                         icon="triangle_alert",
#                         color_scheme="red",
#                         role="alert",
#                         width="100%",
#                         # high_contrast=True,
#                     ),
#                 ),
#                 rx.container()
#             )
#
#         def vscode_banner() -> rx.Component:
#             return rx.hstack(
#                 # Bisheriger VSCode-Link
#                 rx.cond(
#                     ((cls._allow_vscode) & (CondState.code_server_running) & (
#                         ~cls.send_vscode_cooldown)),
#                     rx.hstack(
#                         rx.link(
#                             rx.button(rx.icon(tag="link"), "VSCode"),
#                             href=CondState.code_server_domain,
#                             color_scheme="mint",
#                             is_external=True,
#                         ),
#
#                         rx.cond(
#                             (cls._injectible),
#                             rx.hstack(
#                                 #                                rx.button(
#                                 #                                    rx.icon(tag="play"),
#                                 #                                    "Lade Challenge Dateien",
#                                 #                                    color_scheme="blue",
#                                 #                                    on_click=[lambda: CondState.inject_challenge(cls.day,cls.task,cls.challenge_index)],
#                                 #                                ),
#                                 rx.button(
#                                     rx.icon(tag="play"),
#                                     "Lade Challenge Dateien",
#                                     color_scheme="sky",
#                                     on_click=[
#                                         lambda: CondState.inject_challenge_pvc(cls.day, cls.task,
#                                                                                cls.challenge_index)],
#                                 ),
#                             ),
#                         ),
#                     ),
#                 ),
#             )
#
#         def kali_banner() -> rx.Component:
#             return rx.cond(
#                 ((cls._allow_kali) & (CondState.kali_server_running) & (~cls.send_kali_cooldown)),
#                 rx.link(rx.button(rx.icon(tag="link"), "Kali"), href=CondState.kali_server_domain,
#                         color_scheme="mint", is_external=True, )
#             )
#
#         def first_blood_banner() -> rx.Component:
#             return rx.cond(
#                 cls.is_first_blood,
#                 rx.callout(
#                     "Firstblood! 🩸",
#                     icon="flame",
#                     color_scheme="red",
#                     width="100%",
#                     # high_contrast=True,
#                 )
#             )
#
#         return rx.vstack(
#             rx.flex(
#                 rx.heading(
#                     rx.markdown(cls.question),
#                     as_="h2",
#                     size="5",
#                     overflow="clip",
#                 ),
#                 rx.spacer(),
#                 rx.text(
#                     f"{cls.possible_points}/{cls.max_points} ✨",
#                     padding_left="1em",
#                 ),
#                 width="100%",
#             ),
#
#             rx.cond(
#                 cls._allow_download,
#                 rx.hstack(
#                     rx.button(cls.download_text, variant="ghost", size="2",
#                               on_click=rx.download(url=cls.download_path)),
#                     justify="between",
#                     width="100%",
#                 ),
#             ),
#
#             rx.markdown(cls.question_further, overflow="clip"),
#             answer_field,
#             rx.cond(cls.is_answerable, answer_button(), refresh_button()),
#             vscode_banner(),
#             kali_banner(),
#             answer_banner(),
#             first_blood_banner(),
#             rx.cond(~cls.is_answerable, rx.cond(~cls.solved_task, cls.build_info(), ), ),
#             rx.cond(~cls.solved_task, rx.foreach(cls.requested_hints, cls.build_hint)),
#             spacing="3",
#             width="100%",
#             border="2px solid #ffffff10",
#             border_radius="1em",
#             padding="1em",
#             margin_y="1em",
#             on_mount=[cls.load_state_uniform(False, True), cls.hehehe()],  # noqa
#         )
#
#
# #
# # def wrapper(*args, **kwargs):
# #     import random
# #
# #     name = f"DynamicTaskWidget_{random.randrange(1 << 30)}"
# #     attrs = {
# #         "__module__": TaskWidgetClass.__module__,  # make class appear to live in the real module
# #         "__qualname__": name,
# #     }
# #
# #     c = type(
# #         name,
# #         (TaskWidgetClass,),
# #         attrs
# #     )
# #
# #     # class g(TaskWidgetClass):
# #     #     pass
# #
# #     return c.create(*args, **kwargs)
#
# # TaskWidget: typing.Callable[[TaskData], rx.Component] = wrapper
# TaskWidget: typing.Callable[[TaskData], rx.Component] = TaskWidgetClass.create
