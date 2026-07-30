__all__ = ["EventConfig", "User", "RunningChallenge", "Challenge", "CollectedData",
           "OnRegisterUser", "OnResetUserPW", "OnPreRegisterUser"]

import os
import re
import logging

from datetime import datetime
from typing import Annotated, List, Union, Coroutine, Optional, Literal, Dict

from beanie import Document, Indexed, Link, operators
from fastapi import HTTPException
from pydantic import Field, BaseModel, field_validator

from random import randrange

#solution_obj = str | List[str]
solution_obj = Union[
    str,               # eine Lösung
    List[str],         # mehrere Lösungen
    List[List[str]]    # randomisiert + mehrere Lösungen
]

def has_solved_all_tasks(challenges, day):
    user_day_challenges = [challenge for challenge in challenges if challenge.day_id == day]

    if not user_day_challenges:
        return False

    all_solved = all(challenge.solved for challenge in user_day_challenges)

    return all_solved

def extract_word_from_flag(flag, word_index):
    content = re.search(r'{(.*?)}', flag).group(1)
    words = content.split('_')
    return words[word_index - 1]

def assemble_master_flag(slave_flags, master_format, flag_prefix):
    master_content = re.search(r'{(.*?)}', master_format).group(1)
    instructions = master_content.split('_')

    required_words = []
    for instruction in instructions:
        task_number, word_index = map(int, instruction.split(':'))
        slave_flag = slave_flags[task_number - 1]
        required_words.append(extract_word_from_flag(slave_flag, word_index))

    master_flag = f"{flag_prefix}{{{'_'.join(required_words)}}}"
    return master_flag


class EventConfig(Document):
    event_enable_status: bool = False
    event_registration_status: bool = False
    event_preregister_mode: bool = False
    event_enable_badges: bool = False
    event_badges: List[Dict[str, str]] = []
    event_teamevent_mode: bool = False
    event_teamevent_has_leaders: bool = False
    event_teams: List[str] = [""]
    event_team_colors: List[str] = [""]
    event_show_answers: bool = False
    event_allow_task_reset: bool = False
    event_enable_test_mode: bool = False
    event_enable_player_levels: bool = False
    event_rank_names: List[str] = [""] 
    event_rank_thresholds: List[int] = []
    event_points_per_level: int = 500
    event_confetti_mode: bool = False
    event_toast_mode: bool = False
    event_stats_show_finish_time: bool = False
    event_stats_show_day: bool = False
    event_stats_show_task: bool = False
    event_stats_show_points: bool = False
    event_stats_show_tries: bool = False
    event_stats_show_hints: bool = False
    event_stats_show_resets: bool = False
    event_stats_show_first_blood: bool = False
    event_scoreboard_show_tug_of_war: bool = True
    event_scoreboard_show_further_progress_bars: bool = True
    event_scoreboard_show_scoreboards: bool = True
    event_scoreboard_show_player_with_points_only: bool = False
    event_scoreboard_show_position: bool = True
    event_scoreboard_show_name: bool = True
    event_scoreboard_show_email: bool = False
    event_scoreboard_show_points: bool = True
    event_scoreboard_show_solved: bool = True
    event_scoreboard_show_badges: bool = False
    event_scoreboard_show_first_blood: bool = True

    class Settings:
        name = "event_config"

    @classmethod
    async def enable_event(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_enable_status = True
            await event_config.save()
        else:
            await cls(event_enable_status=True).insert()

    @classmethod
    async def disable_event(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_enable_status = False
            await event_config.save()
        else:
            await cls(event_enable_status=False).insert()

    @classmethod
    async def enable_event_registration(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_registration_status = True
            await event_config.save()
        else:
            await cls(event_registration_status=True).insert()

    @classmethod
    async def disable_event_registration(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_registration_status = False
            await event_config.save()
        else:
            await cls(event_registration_status=False).insert()

    @classmethod
    async def enable_preregister_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_preregister_mode = True
            await event_config.save()
        else:
            await cls(event_preregister_mode=True).insert()

    @classmethod
    async def disable_preregister_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_preregister_mode = False
            await event_config.save()
        else:
            await cls(event_preregister_mode=False).insert()

    @classmethod
    async def enable_badges_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_enable_badges = True
            await event_config.save()
        else:
            await cls(event_enable_badges=True).insert()

    @classmethod
    async def disable_badges_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_enable_badges = False
            await event_config.save()
        else:
            await cls(event_enable_badges=False).insert()

    @classmethod
    async def set_event_badges_list(cls, badges: List[Dict[str, str]]):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_badges = badges
            await event_config.save()
        else:
            await cls(event_badges=badges).insert()

    # --- NEU: Player-Levels & Ränge ---
    @classmethod
    async def enable_player_levels_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_enable_player_levels = True
            await event_config.save()
        else:
            await cls(event_enable_player_levels=True).insert()

    @classmethod
    async def disable_player_levels_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_enable_player_levels = False
            await event_config.save()
        else:
            await cls(event_enable_player_levels=False).insert()


    @classmethod
    async def set_event_rank_config(
        cls,
        rank_names: List[str],
        rank_thresholds: List[int],
        points_per_level: int,
    ):
        # --- Validierung ---
        if len(rank_names) < 1:
            raise ValueError("rank_names must contain at least one rank.")

        # Fall 1: thresholds explizit angegeben
        if len(rank_thresholds) > 0:
            if len(rank_thresholds) != len(rank_names) - 1:
                raise ValueError("rank_thresholds must have length len(rank_names) - 1.")
            if any(t <= 0 for t in rank_thresholds):
                raise ValueError("All thresholds must be positive integers.")
            if sorted(rank_thresholds) != list(rank_thresholds):
                raise ValueError("rank_thresholds must be strictly ascending.")
        else:
            # Fall 2: thresholds leer → automatisch linear berechnen
            if points_per_level <= 0:
                raise ValueError("points_per_level must be positive.")
            rank_thresholds = [points_per_level * i for i in range(1, len(rank_names))]

        if points_per_level <= 0:
            raise ValueError("points_per_level must be positive.")

        # --- Speichern ---
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_rank_names = rank_names
            event_config.event_rank_thresholds = rank_thresholds
            event_config.event_points_per_level = int(points_per_level)
            await event_config.save()
        else:
            await cls(
                event_rank_names=rank_names,
                event_rank_thresholds=rank_thresholds,
                event_points_per_level=int(points_per_level),
            ).insert()

    @classmethod
    async def enable_confetti_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_confetti_mode = True
            await event_config.save()
        else:
            await cls(event_confetti_mode=True).insert()

    @classmethod
    async def disable_confetti_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_confetti_mode = False
            await event_config.save()
        else:
            await cls(event_confetti_mode=False).insert()

    @classmethod
    async def enable_toast_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_toast_mode = True
            await event_config.save()
        else:
            await cls(event_toast_mode=True).insert()

    @classmethod
    async def disable_toast_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_toast_mode = False
            await event_config.save()
        else:
            await cls(event_toast_mode=False).insert()

    @classmethod
    async def set_event_stats_options(
        cls,
        finish_time: bool,
        day: bool,
        task: bool,
        points: bool,
        tries: bool,
        hints: bool,
        resets: bool,
        first_blood: bool,
    ):
        event_config = await cls.find_one({})
        if not event_config:
            event_config = cls()
        event_config.event_stats_show_finish_time = finish_time
        event_config.event_stats_show_day = day
        event_config.event_stats_show_task = task
        event_config.event_stats_show_points = points
        event_config.event_stats_show_tries = tries
        event_config.event_stats_show_hints = hints
        event_config.event_stats_show_resets = resets
        event_config.event_stats_show_first_blood = first_blood
        await event_config.save()

    @classmethod
    async def get_event_stats_options(cls) -> dict:
        event_config = await cls.find_one({})
        if not event_config:
            return {}
        return {
            "finish_time": event_config.event_stats_show_finish_time,
            "day": event_config.event_stats_show_day,
            "task": event_config.event_stats_show_task,
            "points": event_config.event_stats_show_points,
            "tries": event_config.event_stats_show_tries,
            "hints": event_config.event_stats_show_hints,
            "resets": event_config.event_stats_show_resets,
            "first_blood": event_config.event_stats_show_first_blood,
        }

    @classmethod
    async def set_event_scoreboard_options(
        cls,
        tug_of_war: bool,
        further_progress_bars: bool,
        scoreboards: bool,
        player_with_points_only: bool,
        position: bool,
        name: bool,
        email: bool,
        points: bool,
        solved: bool,
        badges: bool,
        first_blood: bool,
    ):
        event_config = await cls.find_one({})
        if not event_config:
            event_config = cls()

        event_config.event_scoreboard_show_tug_of_war = tug_of_war
        event_config.event_scoreboard_show_further_progress_bars = further_progress_bars
        event_config.event_scoreboard_show_scoreboards = scoreboards
        event_config.event_scoreboard_show_player_with_points_only = player_with_points_only
        event_config.event_scoreboard_show_position = position
        event_config.event_scoreboard_show_name = name
        event_config.event_scoreboard_show_email = email
        event_config.event_scoreboard_show_points = points
        event_config.event_scoreboard_show_solved = solved
        event_config.event_scoreboard_show_badges = badges
        event_config.event_scoreboard_show_first_blood = first_blood
        await event_config.save()

    @classmethod
    async def get_event_scoreboard_options(cls) -> dict:
        event_config = await cls.find_one({})
        if not event_config:
            return {}
        return {
            "tug_of_war": event_config.event_scoreboard_show_tug_of_war,
            "further_progress_bars": event_config.event_scoreboard_show_further_progress_bars,
            "scoreboards": event_config.event_scoreboard_show_scoreboards,
            "player_with_points_only": event_config.event_scoreboard_show_player_with_points_only,
            "position": event_config.event_scoreboard_show_position,
            "name": event_config.event_scoreboard_show_name,
            "email": event_config.event_scoreboard_show_email,
            "points": event_config.event_scoreboard_show_points,
            "solved": event_config.event_scoreboard_show_solved,
            "badges": event_config.event_scoreboard_show_badges,
            "first_blood": event_config.event_scoreboard_show_first_blood,
        }

    @classmethod
    async def enable_teamevent_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_teamevent_mode = True
            await event_config.save()
        else:
            await cls(event_teamevent_mode=True).insert()

    @classmethod
    async def disable_teamevent_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_teamevent_mode = False
            await event_config.save()
        else:
            await cls(event_teamevent_mode=False).insert()

    @classmethod
    async def enable_teamevent_leader_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_teamevent_has_leaders = True
            await event_config.save()
        else:
            await cls(event_teamevent_has_leaders=True).insert()

    @classmethod
    async def disable_teamevent_leader_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_teamevent_has_leaders = False
            await event_config.save()
        else:
            await cls(event_teamevent_has_leaders=False).insert()

    @classmethod
    async def set_event_teams_list(cls, teams: List[str]):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_teams = teams
            await event_config.save()
        else:
            await cls(event_teams=teams).insert()

    @classmethod
    async def set_event_team_colors_list(cls, team_colors: List[str]):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_team_colors = team_colors
            await event_config.save()
        else:
            await cls(event_team_colors=team_colors).insert()

    @classmethod
    async def enable_show_answers_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_show_answers = True
            await event_config.save()
        else:
            await cls(event_show_answers=True).insert()

    @classmethod
    async def disable_show_answers_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_show_answers = False
            await event_config.save()
        else:
            await cls(event_show_answers=False).insert()

    @classmethod
    async def enable_allow_task_reset_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_allow_task_reset = True
            await event_config.save()
        else:
            await cls(allow_task_reset=True).insert()

    @classmethod
    async def disable_allow_task_reset_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_allow_task_reset = False
            await event_config.save()
        else:
            await cls(allow_task_reset=False).insert()

    @classmethod
    async def enable_test_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_enable_test_mode = True
            await event_config.save()
        else:
            await cls(event_enable_test_mode=True).insert()

    @classmethod
    async def disable_test_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            event_config.event_enable_test_mode = False
            await event_config.save()
        else:
            await cls(event_enable_test_mode=False).insert()

    @classmethod
    async def get_event_status(cls):
        event_config = await cls.find_one({})
        if event_config:
            return event_config.event_enable_status
        return False

    @classmethod
    async def get_event_registration_status(cls):
        event_config = await cls.find_one({})
        if event_config:
            return event_config.event_registration_status
        return False

    @classmethod
    async def get_event_preregister_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            return event_config.event_preregister_mode
        return False

    @classmethod
    async def get_event_badges_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            return event_config.event_enable_badges
        return False

    @classmethod
    async def get_event_badges_list(cls) -> List[Dict[str,str]]:
        event_config = await cls.find_one({})
        if event_config:
            return event_config.event_badges
        return []

    # --- NEU: Player-Levels & Ränge ---
    @classmethod
    async def get_player_levels_mode(cls) -> bool:
        event_config = await cls.find_one({})
        if event_config:
            return bool(event_config.event_enable_player_levels)
        return False

    @classmethod
    async def get_event_rank_config(cls):
        event_config = await cls.find_one({})
        if event_config:
            return {
                "rank_names": event_config.event_rank_names,
                "rank_thresholds": event_config.event_rank_thresholds,
                "points_per_level": int(event_config.event_points_per_level),
            }
        return {
            "rank_names": [""],
            "rank_thresholds": [],
            "points_per_level": 0,
        }

    @classmethod
    async def get_confetti_mode(cls) -> bool:
        event_config = await cls.find_one({})
        if event_config:
            return bool(event_config.event_confetti_mode)
        return False

    @classmethod
    async def get_toast_mode(cls) -> bool:
        event_config = await cls.find_one({})
        if event_config:
            return bool(event_config.event_toast_mode)
        return False

    @classmethod
    async def get_event_teamevent_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            return event_config.event_teamevent_mode
        return False

    @classmethod
    async def get_event_teamevent_leader_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            return event_config.event_teamevent_has_leaders
        return False

    @classmethod
    async def get_event_teams_list(cls):
        event_config = await cls.find_one({})
        if event_config:
            return event_config.event_teams
        return [""]

    @classmethod
    async def get_event_team_colors_list(cls):
        event_config = await cls.find_one({})
        if event_config:
            return event_config.event_team_colors
        return [""]

    @classmethod
    async def get_event_show_answers_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            return event_config.event_show_answers
        return False

    @classmethod
    async def get_event_allow_task_reset_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            return event_config.event_allow_task_reset
        return False

    @classmethod
    async def get_event_enable_test_mode(cls):
        event_config = await cls.find_one({})
        if event_config:
            return event_config.event_enable_test_mode
        return False


class OnRegisterUser(Document):
    email: str
    token: Annotated[str, Indexed(unique=True)]
    timeout: datetime

    class Settings:
        name = "registration_pending"


class OnPreRegisterUser(Document):
    email: str

    class Settings:
        name = "pre_registration"


class OnResetUserPW(Document):
    email: str
    token: Annotated[str, Indexed(unique=True)]
    timeout: datetime

    class Settings:
        name = "reset_pw_pending"


class UserStats(BaseModel):
    points: int = 0
    challenges_solved: int = 0
    streak: int = 0
    first_solves: int = 0
    badges: List[Dict[str, str]] = []

class User(Document):
    # id: UUID = Field(default_factory=uuid4)
    username: Annotated[str, Indexed(unique=True)]
    username_display: str

    email: str
    pw_hash: str

    avatar_index: str

    team: str = ""
    team_leader: bool = False
    team_color: str = ""

    stats: UserStats = UserStats()

    class Settings:
        name = "users"


class TaskHint(BaseModel):
    hint_index: int
    hint: str
    multiplier: float


class Challenge(Document):
    day_id: int
    task_id: int
    day_description: Optional[str] = None
    task_description: Optional[str] = None
    vm_name: Optional[str] = None
    flag_type: Optional[str] = None
    dynamic_check: Optional[Literal[
        "dh_factors", "dh_server_secret", "dh_master_secret", "dh_flag",
        "export_factor256", "export_factor512", "export_master_secret", "export_flag"
    ]] = None
    points: int
    error_cost: int = 1
    allow_reset: bool
    allow_random_order: bool
    master_task: bool
    first_solved: Optional[Link[User]] = None
    question: List[str]
    question_further: List[str]
    placeholder_text: List[str]
    download_text: List[str]
    download_path: List[str]
    link_text: List[str]
    link_path: List[str]
    options: list[str] | list[list[str]]
    answers: list[dict] | list[list[dict]]
    solutions: solution_obj
    task_type: Literal["input", "select", "multiple", "regex"]
    hints: list[TaskHint] = []
    sha256_checksum: str

    # RANDOM SINGLE/MULTIPLE CHOICE
    # options: Union[List[str], List[List[str]]] = []

    class Settings:
        name = "challenges"
        indexes = ["day_id", "task_id"]

    @classmethod
    async def get_tasks_solved(cls, username: str) -> Dict[str, bool]:
        challenges = [c for c in await RunningChallenge.get_all(username.lower()) if
                      c.username == username.lower()]
        chs = await cls.all().to_list()
        days = sorted(set(chal.day_id for chal in chs))

        tasks_solved = {}
        for day in days:
            day_challenges = [chal for chal in chs if chal.day_id == day]
            for chal in day_challenges:
                task_key = f"day_{day:02d}_task_{chal.task_id:02d}"
                running_challenge = next(
                    (rc for rc in challenges if rc.day_id == day and rc.task_id == chal.task_id),
                    None)
                tasks_solved[task_key] = running_challenge.solved if running_challenge else False

        return tasks_solved

    @classmethod
    async def get_day_tasks_solved(cls, username: str, day: int) -> Dict[str, bool]:
        username = username.lower()

        challenges = [c for c in await RunningChallenge.get_all(username) if
                      c.username == username and c.day_id == day]

        chs = [chal for chal in await cls.all().to_list() if chal.day_id == day]

        tasks_solved = {}

        for chal in chs:
            task_key = f"day_{day:02d}_task_{chal.task_id:02d}"
            running_challenge = next((rc for rc in challenges if rc.task_id == chal.task_id), None)
            tasks_solved[task_key] = running_challenge.solved if running_challenge else False

        return tasks_solved

    @classmethod
    async def get_task_points(cls, username: str) -> Dict[str, int]:
        challenges = [c for c in await RunningChallenge.get_all(username.lower()) if
                      c.username == username.lower()]
        chs = await cls.all().to_list()
        days = sorted(set(chal.day_id for chal in chs))

        task_points = {}
        for day in days:
            day_challenges = [chal for chal in chs if chal.day_id == day]
            max_points = sum(chal.points for chal in day_challenges)

            user_day_challenges = [c for c in challenges if c.day_id == day]
            earned_points = sum(c.points_earned or 0 for c in user_day_challenges)

            task_points[f"day_{day:02d}_max_points"] = max_points
            task_points[f"day_{day:02d}_points_earned"] = earned_points

        return task_points

    @classmethod
    async def reset_day(cls, username: str, day: int) -> Dict[str, bool]:
        challenges = await cls.find(cls.day_id == day).to_list()

        if not challenges:
            return {"day_reset": False}

        user_challenges = await RunningChallenge.find(
            RunningChallenge.username == username,
            RunningChallenge.day_id == day
        ).to_list()

        solved_tasks = {
            (uc.day_id, uc.task_id)
            for uc in user_challenges
            if uc.solved
        }

        for ch in challenges:
            if (ch.day_id, ch.task_id) in solved_tasks:
                await ch.delete_answer(username)

        return {"day_reset": True}

    @classmethod
    async def get_challenge(cls, day: int, task: int) -> "Challenge":
        ch = await cls.find_one(
            cls.day_id == day,
            cls.task_id == task,
            fetch_links=True
        )
        if ch is None:
            raise HTTPException(status_code=404, detail="Challenge nicht gefunden")
        return ch

    async def request_random_index(self, username: str, random_selection: bool) -> int:
        challenge = await RunningChallenge.find_one(
            RunningChallenge.username == username,
            RunningChallenge.challenge.id == self.id,
        ) or RunningChallenge(
            username=username,
            challenge=self,
            day_id=self.day_id,
            task_id=self.task_id,
            resets=0,
            random_index=0,
            points_to_get=self.points,
        )
        logging.info("Requesting random index")

        if challenge.solved:
            return challenge.random_index

        if challenge.random_index:
            return challenge.random_index

        if random_selection:
            logging.info(f"Solutions range: {self.solutions=}")
            challenge.random_index = randrange(len(self.solutions))
        else:
            challenge.random_index = 0

        await challenge.save()

        return challenge.random_index

    async def request_hint(self, username: str) -> bool:
        challenge: "RunningChallenge" = await RunningChallenge.find_one(
            RunningChallenge.username == username,
            RunningChallenge.challenge.id == self.id,
        ) or RunningChallenge(
            username=username,
            challenge=self,
            day_id=self.day_id,
            task_id=self.task_id,
            resets=0,
            random_index=0,
            points_to_get=self.points,
        )

        if challenge.solved:
            return True

        # check hint available
        # ToDo: possibly incorrect with randomization -> check distinct by indices
        if challenge.hints_gotten < len(self.hints):
            challenge.factor = self.hints[challenge.hints_gotten].multiplier
            challenge.points_to_get = min(int(self.points * challenge.factor), challenge.points_to_get)

            challenge.hints_gotten += 1
            await challenge.save()
            return True

        return False

    async def update_badges_if_eligible(self, username: str) -> None:
        enable_badges = await EventConfig.get_event_badges_mode()
        if not enable_badges:
            return

        challenges = [c for c in await RunningChallenge.get_all(username.lower()) if
                      c.username == username.lower()]
        chs = await Challenge.all().to_list()
        days = sorted(set(chal.day_id for chal in chs))

        solved_all_tasks_array = [has_solved_all_tasks(challenges, day) for day in days]
        emoji_badges = await EventConfig.get_event_badges_list()

        user_badges: list[dict] = []
        for entry, badge_def in zip(solved_all_tasks_array, emoji_badges):
            if entry:
                user_badges.append(badge_def)

        await User.find_one(User.username == username).update(operators.Set({
            User.stats.badges: user_badges,
        }))

    async def delete_answer(self, username: str) -> bool:
        challenge = await RunningChallenge.find_one(
            RunningChallenge.username == username,
            RunningChallenge.challenge.id == self.id,
            fetch_links=True
        ) or RunningChallenge(
            username=username,
            challenge=self,
            day_id=self.day_id,
            task_id=self.task_id,
            resets=0,
            random_index=0,
            points_to_get=self.points,
        )

        #        if ~challenge.solved:
        #            return True

        user = await User.find_one(User.username == username)
        operation = {
            User.stats.points           : -challenge.points_earned,
            User.stats.challenges_solved: -1,
        }

        await user.inc(operation)

        await User.find_one(User.username == username).update(operators.Set({
            User.stats.streak: 0,
        }))

        challenge.solved = False
        challenge.points_earned = 0
        challenge.hints_gotten = 0
        challenge.factor = 1
        challenge.finish_time = None
        challenge.points_to_get = self.points
        challenge.resets += 1

        if (challenge.challenge.allow_random_order):
            if (len(challenge.challenge.solutions) > 1):
                # avoid to assign the same random challenge twice
                new_random_index = randrange(len(challenge.challenge.solutions))
                while (challenge.random_index == new_random_index):
                    new_random_index = randrange(len(challenge.challenge.solutions))
                challenge.random_index = new_random_index
            else:
                challenge.random_index = 0

        await challenge.save()

        await self.update_badges_if_eligible(user.username)
        user = await User.find_one(User.username == username)

        # Immediately broadcast the updated score
        from database.connection import MongoDB
        logging.info(f"Broadcasting score update for user: {user.username}")
        await MongoDB.instance.broadcast_score_update(user)

        return True

    async def check_answer(self, username: str, answer: str | int) -> bool:
        challenge = await RunningChallenge.find_one(
            RunningChallenge.username == username,
            RunningChallenge.challenge.id == self.id,
            fetch_links=True
        ) or RunningChallenge(
            username=username,
            challenge=self,
            day_id=self.day_id,
            task_id=self.task_id,
            resets=0,
            random_index=0,
            points_to_get=self.points,
        )

        if challenge.solved:
            return True

        try:
            if self.dynamic_check:
                if self.dynamic_check.startswith("export_"):
                    from utils.export_cipher_client import check_dynamic_answer
                else:
                    from utils.dh_export_client import check_dynamic_answer
                if not await check_dynamic_answer(self.dynamic_check, username, str(answer)):
                    raise ValueError()

            # RANDOM SINGLE/MULTIPLE CHOICE
            #            if self.solution_type == "multiple":
            elif self.task_type in ("multiple", "select", "input"):

                if (self.master_task):

                    # Get all user slave-challenge entries for the user
                    user_challenges = await RunningChallenge.find(
                        RunningChallenge.username == username,
                        RunningChallenge.day_id == self.day_id,
                        fetch_links=True
                    ).to_list()

                    master_format = self.solutions[0]

                    # Sort and filter only slave challenges (i.e., master_task == False)
                    sorted_user_challenges = sorted(
                        [rc for rc in user_challenges if not rc.challenge.master_task],
                        key=lambda rc: rc.task_id
                    )

                    slave_flags = []

                    for rc in sorted_user_challenges:
                        challenge_obj = rc.challenge
                        solutions = challenge_obj.solutions

                        if challenge_obj.allow_random_order:
                            challenge_index = rc.random_index
                        else:
                            challenge_index = rc.resets % len(solutions)

                        slave_flag = solutions[challenge_index]
                        slave_flags.append(slave_flag)

                    flag_prefix = master_format.split('{')[0]
                    master_solution = assemble_master_flag(slave_flags, master_format, flag_prefix)
                    if str(answer).lower() != master_solution:
                        if str(answer) != master_solution:
                            raise ValueError()

                else:
                    if (self.allow_random_order):
                        challenge_index = challenge.random_index
                    else:
                        challenge_index = challenge.resets % len(self.solutions)

                    valid_solutions = self.solutions[challenge_index]

                    # Falls nur eine Lösung existiert → in Liste umwandeln
                    if isinstance(valid_solutions, str):
                        valid_solutions = [valid_solutions]

                    # Vergleich (case-insensitive)
                    if str(answer).lower() not in [s.lower() for s in valid_solutions]:
                        raise ValueError()

#                    if str(answer).lower() != self.solutions[challenge_index]:
#                        if str(answer) != self.solutions[challenge_index]:
#                            raise ValueError()

            elif self.task_type == "regex":
                raise NotImplementedError("Regex not implemented yet")

            else:
                raise ValueError("Invalid solution type")

        except ValueError:
            challenge.tries += 1
            challenge.points_to_get = max(challenge.points_to_get - self.error_cost, 0)
            await User.find_one(User.username == username).update(operators.Set({
                User.stats.streak: 0,
            }))

            await challenge.save()
            return False

        # alt, Gefahr vor Race Condition
        #else:
        #    challenge.solved = True
        #    challenge.points_earned = challenge.points_to_get
        #    challenge.finish_time = datetime.now()

        #    user = await User.find_one(User.username == username)
        #    operation = {
        #        User.stats.points           : challenge.points_earned,
        #        User.stats.streak           : 1,
        #        User.stats.challenges_solved: 1,
        #    }

        #    # check first blood
        #    if self.first_solved is None and challenge.hints_gotten == 0:
        #        self.first_solved = user
        #        operation |= {
        #            User.stats.first_solves: 1,
        #            User.stats.points      : round(challenge.points_earned * 1.2)
        #        }
        #        await self.save()

        #    # set user's challenge to done
        #    await user.inc(operation)
        #    await challenge.save()

        #    await self.update_badges_if_eligible(user.username)
        #    user = await User.find_one(User.username == username)

        #    # Immediately broadcast the updated score
        #    from database.connection import MongoDB
        #    logging.info(f"Broadcasting score update for user: {user.username}")
        #    await MongoDB.instance.broadcast_score_update(user)

        #    return True

        # neu
        # TODO: Verhindert Race Condition (d.h. wenn zwei Spieler zeitgleich First Blood bekommen kann nur einer First Blood erhalten)
        else:
            challenge.solved = True
            challenge.points_earned = challenge.points_to_get
            challenge.finish_time = datetime.now()

            user = await User.find_one(User.username == username)
            
            # First Blood Check mit atomarem DB-Update um Race Condition zu verhindern
            is_first_blood = False
            # alt, kann trotzdem verwendet werden, falls fetch_links gesetzt ist
            #if self.first_solved is None and challenge.hints_gotten == 0:
            # TODO: alternative unten funktioniert auch ohne fetch_links in get_challenges
            # funktioniert auch dann, sollten sich Beanie Versionen ändern
            if not self.first_solved and challenge.hints_gotten == 0:
                # Atomares Update – nur einer kann first_solved setzen
                result = await Challenge.find_one(
                    Challenge.id == self.id,
                    Challenge.first_solved == None  # ← prüft nochmal in DB
                )
                if result is not None:
                    self.first_solved = user
                    await self.save()
                    is_first_blood = True
                    logging.info(f"First Blood für {username} auf Challenge {self.day_id}/{self.task_id}")

            operation = {
                User.stats.points: round(challenge.points_earned * 1.2) if is_first_blood else challenge.points_earned,
                User.stats.streak: 1,
                User.stats.challenges_solved: 1,
            }

            if is_first_blood:
                operation[User.stats.first_solves] = 1

            # set user's challenge to done
            await user.inc(operation)
            await challenge.save()

            await self.update_badges_if_eligible(user.username)
            user = await User.find_one(User.username == username)

            # Immediately broadcast the updated score
            from database.connection import MongoDB
            logging.info(f"Broadcasting score update for user: {user.username}")
            await MongoDB.instance.broadcast_score_update(user)

            return True


class RunningChallenge(Document):
    # username: Annotated[Link[User], Indexed(unique=True)]
    username: Annotated[str, Indexed(unique=False)]
    challenge: Link[Challenge]

    day_id: int
    task_id: int
    points_to_get: int

    random_index: int

    tries: int = 0
    resets: int = 0
    factor: float = 1
    solved: bool = False

    points_earned: Optional[int] = None
    finish_time: Optional[datetime] = None

    hints_gotten: int = 0

    class Settings:
        name = "user_challenges"

    @staticmethod
    def get_all(username: str) -> Coroutine[None, None, List["RunningChallenge"]]:
        return (
            RunningChallenge.find_all(
                RunningChallenge.username == username.lower(),
                fetch_links=True
            )
            .sort("+challenge.day_id", "+challenge.task_id")
            .skip(0)
            .to_list()
        )


class CollectedData(Document):
    class Settings:
        name = "collected_data"
