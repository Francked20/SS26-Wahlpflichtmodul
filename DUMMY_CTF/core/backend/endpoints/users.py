import os
import httpx
import asyncio
import json
import logging
import string
import sys
import typing
# from multiprocessing.managers import rebuild_as_list
import re

from beanie import Link, Document
from beanie.operators import NotIn, And, Eq
from fastapi import APIRouter, Security
from fastapi_jwt import JwtAuthorizationCredentials
# from profanity_check import predict

import math

from database.models import *
from utils.security import access_security

from random import randrange

import hashlib

if typing.TYPE_CHECKING:
    from backend.database.models import Challenge

timeout = httpx.Timeout(
    connect=10.0,   # Verbindungsaufbau
    read=30.0,      # Zeit bis zur Antwort
    write=10.0,
    pool=10.0,
)

MAX_RETRIES = 3
RETRY_DELAY = 1.0  # Sekunden

enable_cyber_range = os.getenv("ENABLE_CYBER_RANGE", "False").lower() == "true"
cyber_range_admin_key = os.getenv("CYBER_RANGE_ADMIN_KEY")
cyber_range_base_url = os.getenv("CYBER_RANGE_BASE_URL")
cyber_range_labid = os.getenv("CYBER_RANGE_LABID", "hiy")  # Default falls nicht gesetzt

async def send_flags_with_retry(
    url,
    headers,
    params,
    flags_payload,
    effective_username,
    timeout=10.0,
):
    """Sendet Flags robust mit Retry bei Transportfehlern."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(
                    url,
                    headers=headers,
                    params=params,
                    json=flags_payload,
                )

            # Erfolgreich?
            if resp.status_code == 200:
                logging.info(
                    f"[FLAG-INJECT] SUCCESS for user={effective_username}: "
                    f"{json.dumps(flags_payload, indent=2)}"
                )
                return True

            # Server antwortet, aber mit Fehler → kein Retry
            logging.error(
                f"[FLAG-INJECT] FAILED (HTTP {resp.status_code}) for user={effective_username}, "
                f"response={resp.text}"
            )
            return False

        except (httpx.TransportError, httpx.ReadTimeout, httpx.ConnectError) as e:
            # Netzwerkfehler → Retry
            logging.warning(
                f"[FLAG-INJECT] Network error on attempt {attempt}/{MAX_RETRIES} "
                f"for user={effective_username}: {e}"
            )

            if attempt == MAX_RETRIES:
                logging.error(
                    f"[FLAG-INJECT] Giving up after {MAX_RETRIES} attempts for user={effective_username}"
                )
                return False

            await asyncio.sleep(RETRY_DELAY)

        except Exception as e:
            # Unerwarteter Fehler → kein Retry
            logging.exception(
                f"[FLAG-INJECT] Unexpected error for user={effective_username}: {e}"
            )
            return False

def generate_subdomain(username: str) -> str:
    return hashlib.sha256(username.encode()).hexdigest()[:6]

# forbidden_list = json.loads(open("./static/profane_words.json").read())
forbidden_list = [
    "root", "admin", "administrator", "wheel", "sys", "system", "bin", "daemon", "adm", "lp",
    "sync", "sudo", "??",
    "shutdown", "halt", "mail", "news", "uucp", "operator", "ftp", "etc", "rpc", "nobody", "mongod",
    "mongodb",
]
forbidden_list.sort()
# url-safe & injection safe characters only
allowed_symbols = string.ascii_lowercase + string.digits + r"""-_.~"""


def extract_word_from_flag(flag, word_index):
    """
    Extracts the word at the given 1-based index from the flag content.
    """
    # Extract the content inside the curly braces
    content = re.search(r'{(.*?)}', flag).group(1)
    # Split the content by underscores to get individual words
    words = content.split('_')
    # Return the word at the specified index (1-based index)
    return words[word_index - 1]


def assemble_master_flag(slave_flags, master_format, flag_prefix):
    """
    Assembles the master flag based on the instructions in the master format.
    """
    # Extract the content inside the curly braces of the master format
    master_content = re.search(r'{(.*?)}', master_format).group(1)
    # Split the content by underscores to get individual task instructions
    instructions = master_content.split('_')

    # Initialize an empty list to store the required words
    required_words = []

    # Iterate over each instruction
    for instruction in instructions:
        # Extract the task number and word index
        task_number, word_index = map(int, instruction.split(':'))
        # Get the corresponding slave flag
        slave_flag = slave_flags[task_number - 1]
        # Extract the required word and add it to the list
        required_words.append(extract_word_from_flag(slave_flag, word_index))

    # Assemble the master flag
    master_flag = f"{flag_prefix}{{{'_'.join(required_words)}}}"
    return master_flag

async def _resolve_effective_username(username: str) -> tuple[str, bool]:
    """
    Bestimmt den effektiven Username bei Team-Events mit Leader-Mode.
    Gibt (effective_username, is_answerable) zurück.
    """
    username = (username or "").lower()
    is_answerable = True

    event_config = await EventConfig.find_one({})
    if not event_config:
        return username, is_answerable  # keine Config -> keine Umschreibung

    if event_config.event_teamevent_mode and event_config.event_teamevent_has_leaders:
        user = await User.find_one(User.username == username)
        if user and not user.team_leader:
            is_answerable = False
            team_leader = await User.find_one({"team": user.team, "team_leader": True})
            if team_leader:
                return team_leader.username.lower(), is_answerable

    return username, is_answerable

def _normalize_rank_config(cfg: EventConfig | None) -> tuple[list[str], list[int], int]:
    """
    Liefert eine robuste, stets gültige Rank-Konfiguration zurück.
    - Thresholds werden automatisch repariert (Typen, Sortierung, Länge).
    - Thresholds werden niemals leer zurückgegeben.
    - Backend fällt niemals in den Fallback-Modus.
    """

    default_ppl = 500

    if not cfg:
        return [], [], default_ppl

    names = cfg.event_rank_names or []
    raw_thresholds = cfg.event_rank_thresholds or []
    ppl = int(cfg.event_points_per_level or default_ppl)

    # Wenn keine Rank-Namen existieren → keine Ränge
    if not names or len(names) < 2:
        return names, [], ppl

    # --- 1) Thresholds in ints konvertieren ---
    thresholds = []
    for t in raw_thresholds:
        try:
            thresholds.append(int(t))
        except Exception:
            continue  # ungültige Werte ignorieren

    # --- 2) Negative oder Null-Werte entfernen ---
    thresholds = [t for t in thresholds if t > 0]

    # --- 3) Sortieren & Duplikate entfernen ---
    thresholds = sorted(set(thresholds))

    # --- 4) Länge korrigieren ---
    expected_len = len(names) - 1

    if len(thresholds) < expected_len:
        # Fehlende Werte automatisch auffüllen
        # Linearer Abstand basierend auf points_per_level
        start = thresholds[-1] if thresholds else ppl
        while len(thresholds) < expected_len:
            start += ppl
            thresholds.append(start)

    elif len(thresholds) > expected_len:
        # Zu viele Thresholds → abschneiden
        thresholds = thresholds[:expected_len]

    # --- 5) Garantiert gültige Rückgabe ---
    return names, thresholds, ppl


def _compute_rank(points: int, names: list[str], thresholds: list[int]) -> str:
    if not names or not thresholds:
        return ""  # keine Ränge konfiguriert
    idx = 0
    for t in thresholds:
        if points >= t:
            idx += 1
        else:
            break
    idx = min(idx, len(names) - 1)
    return names[idx] or ""

def _compute_level_and_percent(points: int, points_per_level: int) -> tuple[int, int]:
    """
    Berechnet Level (ab 1) und Fortschritt innerhalb des Levels (0–100%) mit linearer Kurve.
    """
    p = max(0, int(points))
    ppl = max(1, int(points_per_level))
    level = max(1, p // ppl + 1)
    base = (level - 1) * ppl
    next_ = level * ppl
    percent = int(100 * (p - base) / max(1, next_ - base))
    return level, max(0, min(100, percent))

def _compute_level_and_percent_from_thresholds(points: int, thresholds: list[int]) -> tuple[int, int]:
    p = max(0, int(points))

    # Level bestimmen
    level = 1
    for t in thresholds:
        if p >= t:
            level += 1
        else:
            break

    # Progressbar bestimmen
    if level == 1:
        base = 0
        next_ = thresholds[0]

    elif level <= len(thresholds):
        base = thresholds[level - 2]
        next_ = thresholds[level - 1]

    else:
        # Spieler ist über dem letzten Threshold → max Level
        base = thresholds[-1]
        next_ = base + (thresholds[-1] - thresholds[-2])

    percent = int(100 * (p - base) / max(1, next_ - base))
    return level, max(0, min(100, percent))


def format_solutions(sol):
    # Einzelne Lösung
    if isinstance(sol, str):
        return f"Die Antwort lautet: {sol}"

    # Mehrere mögliche Lösungen
    if isinstance(sol, list):
        # Liste von Strings
        if all(isinstance(x, str) for x in sol):
            return "Die möglichen Antworten sind: " + ", ".join(sol)

        # Liste von Listen (sollte bei Freitext nicht vorkommen)
        if all(isinstance(x, list) for x in sol):
            flat = [item for sub in sol for item in sub]
            return "Die möglichen Antworten sind: " + ", ".join(flat)

    # Fallback
    return f"Die Antwort lautet: {sol}"

router = APIRouter()


@router.get("/score")
async def get_points(username: str):
    effective_username, _ = await _resolve_effective_username(username)

    challenges = [
        c for c in await RunningChallenge.get_all(effective_username)
        if c.username == effective_username
    ]
    return {
        "points": sum([challenge.points_earned or 0 for challenge in challenges]),
        "challenges": len([c for c in challenges if c.solved]),
    }

@router.get("/badges")
async def get_badges(username: str):
    effective_username, _ = await _resolve_effective_username(username)

    user = await User.find_one(User.username == effective_username)
    return {"badges": user.stats.badges}


@router.get("/team")
async def get_user_team(username: str):
    user = await User.find_one(User.username == username.lower())
    return {"team": user.team}


@router.get("/team_leader")
async def is_team_leader(username: str):
    user = await User.find_one(User.username == username.lower())
    return {"team_leader": user.team_leader}


@router.get("/get_team_info")
async def get_team_info(username: str):
    user = await User.find_one(User.username == username.lower())
    if user and user.team:
        team_leader = await User.find_one({"team": user.team, "team_leader": True})
        if team_leader:
            return {
                "team_leader_name": team_leader.username,
                "team_name": user.team,
                "team_color": user.team_color,
            }
    return {
        "team_leader_name": None,
        "team_name": "",
        "team_color": "rgba(14, 30, 37, 0.65)",
    }


@router.get("/exists")
async def does_user_exist(username: str, check_forbidden: bool = False):
    username = username.lower()

    forbidden = False
    user = None

    if check_forbidden:
        if username in forbidden_list:
            forbidden = True

        elif not all([x in allowed_symbols for x in username]):
            forbidden = True

        # elif predict([username])[0] == 1:
        #     forbidden = True

    if not forbidden:
        user = await User.find_one(User.username == username, ignore_cache=True)

    return {"exists": user is not None, "forbidden": forbidden if check_forbidden else None}

@router.get("/level")
async def get_user_level(username: str):
    """
    Liefert Punkte, Rang, Level, Badges sowie Team-Infos des Users.
    """
    # 1) Effektiven Username bestimmen (für Punkte/Rang/Level)
    effective_username, _ = await _resolve_effective_username(username)

    # 2) User laden für Punkte etc.
    user_eff = await User.find_one(User.username == effective_username)
    points = 0
    first_solves = 0
    badges = []
    if user_eff and getattr(user_eff, "stats", None):
        try:
            points = int(user_eff.stats.points or 0)
        except Exception:
            points = 0
        try:
            first_solves = int(user_eff.stats.first_solves or 0)
        except Exception:
            first_solves = 0
        badges = getattr(user_eff.stats, "badges", []) or []

    # 3) Event-Konfiguration laden
    cfg = await EventConfig.find_one({})
    rank_names, thresholds, ppl = _normalize_rank_config(cfg)

    # 4) Berechnung
    rank = _compute_rank(points, rank_names, thresholds)

    if thresholds:
        level, level_percent = _compute_level_and_percent_from_thresholds(points, thresholds)
    else:
        level, level_percent = _compute_level_and_percent(points, ppl)


    # 5) Team-Infos über den echten Usernamen
    user_real = await User.find_one(User.username == username.lower())
    team = getattr(user_real, "team", "") if user_real else ""
    team_leader = bool(getattr(user_real, "team_leader", False)) if user_real else False

    # 6) Antwort
    return {
        "points": points,
        "rank": rank,
        "level": level,
        "level_percent": level_percent,
        "first_solves": first_solves,
        "badges": badges,
        "team": team,
        "team_leader": team_leader,
    }

@router.post("/initialize_challenges")
async def initialize_challenges(
    username: str,
    _: JwtAuthorizationCredentials = Security(access_security),
):
    effective_username, is_answerable = await _resolve_effective_username(username)

    # Alle Challenges laden
    all_challenges = await Challenge.find().to_list()

    # Bereits existierende User-Challenges laden
    existing = await RunningChallenge.find(
        RunningChallenge.username == effective_username,
        fetch_links=True
    ).to_list()

    existing_keys = {(rc.day_id, rc.task_id) for rc in existing}

    created = []

    flags_payload = {}
    userid = generate_subdomain(effective_username)

    # ---------------------------------------------------------
    # A) Neue Challenges erzeugen
    # ---------------------------------------------------------
    for ch in all_challenges:
        key = (ch.day_id, ch.task_id)

        if key in existing_keys:
            continue

        if ch.allow_random_order:
            random_index = randrange(len(ch.solutions))
        else:
            random_index = 0

        rc = RunningChallenge(
            username=effective_username,
            challenge=ch,
            day_id=ch.day_id,
            task_id=ch.task_id,
            factor=1,
            tries=0,
            resets=0,
            solved=False,
            finish_time=None,
            hints_gotten=0,
            points_earned=None,
            points_to_get=ch.points,
            random_index=random_index,
        )

        await rc.insert()
        created.append({"day": ch.day_id, "task": ch.task_id})

    # ---------------------------------------------------------
    # B) Flags für ALLE Challenges (neu + existierend) sammeln
    # ---------------------------------------------------------
    if enable_cyber_range and is_answerable:
        # RunningChallenges erneut laden (inkl. der gerade erzeugten)
        all_rc = await RunningChallenge.find(
            RunningChallenge.username == effective_username,
            fetch_links=True
        ).to_list()

        flags_payload = {}

        for rc in all_rc:
            # Challenge-Dokument sicher laden
            ch = rc.challenge
            if hasattr(ch, "fetch"):
                ch = await ch.fetch()

            # Wenn Challenge nicht geladen werden konnte → überspringen
            if not ch:
                continue

            # Wenn vm_name oder flag_type fehlen → überspringen
            if not (ch.vm_name and ch.flag_type):
                continue

            # Lösung anhand des random_index
            try:
                flag_value = ch.solutions[rc.random_index]
            except Exception:
                continue  # falls inkonsistente Daten existieren

            if ch.vm_name not in flags_payload:
                flags_payload[ch.vm_name] = {}

            flags_payload[ch.vm_name][ch.flag_type] = flag_value

        # ---------------------------------------------------------
        # C) Flags an Cyber-Range senden
        # ---------------------------------------------------------

        if flags_payload:
            url = f"{cyber_range_base_url}/flags/write-flags"
            headers = {"X-API-Key": cyber_range_admin_key}
            params = {"labid": cyber_range_labid, "userid": userid}

            await send_flags_with_retry(
                url=url,
                headers=headers,
                params=params,
                flags_payload=flags_payload,
                effective_username=effective_username,
                timeout=timeout,
            )

    return {
        "created": created,
        "total_created": len(created),
        "status": "ok"
    }

@router.get("/challenges_dataset/{day}/{task}")
async def get_uniform_challenge_status(
        username: str,
        day: int,
        task: int,
        _: JwtAuthorizationCredentials = Security(access_security),
):
    effective_username, is_answerable = await _resolve_effective_username(username)

    # Hilfsfunktion: Link → echtes Dokument
    async def resolve_link(link):
        if isinstance(link, Link):
            return await link.document_class.get(link.ref.id)
        if isinstance(link, Document):
            return link
        raise ValueError("Resolve input is neither Link nor Document")

    # async def resolve_link(obj):
    #     if hasattr(obj, "fetch_all_links"):
    #         return await obj.fetch_all_links()
    #     return obj

    # ---------------------------------------------------------
    # 1) RunningChallenge laden
    # ---------------------------------------------------------
    c_run = await RunningChallenge.find_one(
        RunningChallenge.username == effective_username,
        RunningChallenge.day_id == day,
        RunningChallenge.task_id == task,
        fetch_links=True
    )

    # ---------------------------------------------------------
    # FALL A: RunningChallenge existiert
    # ---------------------------------------------------------
    if c_run:

        # Challenge-Dokument sicher laden
        ch = await resolve_link(c_run.challenge)

        # first_solved sicher laden
        fs = None
        if ch and ch.first_solved:
            fs_obj = ch.first_solved
            fs_obj = await resolve_link(fs_obj)
            fs = getattr(fs_obj, "username", None)

        # challenge_index bestimmen
        if ch.allow_random_order:
            challenge_index = c_run.random_index
        else:
            challenge_index = c_run.resets % len(ch.solutions)

        # ---------------------------------------------------------
        # MASTER-TASK LOGIK
        # ---------------------------------------------------------
        slave_flags = []
        master_format = ""
        flag_prefix = ""

        if ch.master_task:

            # Alle RunningChallenges des Users für diesen Tag laden
            user_challenges = await RunningChallenge.find(
                RunningChallenge.username == effective_username,
                RunningChallenge.day_id == day,
                fetch_links=True
            ).to_list()

            # Master-Format
            master_format = ch.solutions[challenge_index]
            flag_prefix = master_format.split('{')[0]

            # Slave-Challenges sortieren
            sorted_user_challenges = []
            for rc in user_challenges:
                challenge_obj = await resolve_link(rc.challenge)
                if not challenge_obj.master_task:
                    sorted_user_challenges.append((rc, challenge_obj))

            sorted_user_challenges.sort(key=lambda x: x[0].task_id)

            # Slave-Flags extrahieren
            for rc, challenge_obj in sorted_user_challenges:
                solutions = challenge_obj.solutions

                if challenge_obj.allow_random_order:
                    slave_challenge_index = rc.random_index
                else:
                    slave_challenge_index = rc.resets % len(solutions)

                slave_flag = solutions[slave_challenge_index]
                slave_flags.append(slave_flag)

        # ---------------------------------------------------------
        # Antwort für existierende RunningChallenge
        # ---------------------------------------------------------
        return {
            "current_points": c_run.points_to_get,
            "maximum_points": int(ch.points * c_run.factor),

            "question": ch.question[challenge_index],
            "question_further": ch.question_further[challenge_index],
            "placeholder_text": ch.placeholder_text[challenge_index],
            "options": (
                ch.options[challenge_index]
                if ch.options and isinstance(ch.options[0], list)
                else ch.options
            ),

            "hints_point_cap" : [int(math.floor(x.multiplier * ch.points)) for x in ch.hints if x.hint_index == challenge_index],
            "hints_unlocked": [x.hint for x in ch.hints if x.hint_index == challenge_index][:c_run.hints_gotten],

            "download_path": ch.download_path[challenge_index],
            "download_text": ch.download_text[challenge_index],

            "solved": c_run.solved,
            "first_blood": fs == effective_username,
            "is_answerable": is_answerable,

            "solution": (
                # MASTER TASK
                f"Die Antwort ist: {assemble_master_flag(slave_flags, master_format, flag_prefix)}"
                if c_run.solved and ch.master_task else

                # MULTIPLE CHOICE (Bitstring, MSB-first)
                (
                    lambda opts, bits: (
                        f"Antworten {', '.join(str(i + 1) for i, b in enumerate(bits) if b == '1')} sind korrekt"
                        if any(b == "1" for b in bits)
                        else "Keine Antwort ist korrekt."
                    )
                )(ch.options[challenge_index], ch.solutions[challenge_index])
                if c_run.solved and ch.task_type == "multiple" else

                # SINGLE CHOICE (SELECT)
                (
                    # Fall A: options ist Liste von Listen (mehrere Fragen)
                    f"Antwort {ch.options[challenge_index].index(ch.solutions[challenge_index]) + 1} ist korrekt"
                    if isinstance(ch.options[0], list)
                    else
                    # Fall B: options ist flache Liste (eine Frage)
                    f"Antwort {ch.options.index(ch.solutions[challenge_index]) + 1} ist korrekt"
                )
                if c_run.solved and ch.task_type == "select" else

                # INPUT
                format_solutions(ch.solutions[challenge_index])
                if c_run.solved and ch.task_type == "input" else

                ""
            )
        }

#        return {
#            "is_answerable": is_answerable,
#            "day": c_run.day_id,
#            "task": c_run.task_id,
#            "challenge_index": challenge_index,
#            "tries": c_run.tries,
#            "resets": c_run.resets,
#            "abs_points": ch.points,
#            "max_points": int(ch.points * c_run.factor),
#            "possible_points": c_run.points_to_get,
#            "solved": c_run.solved,
#            "finish_time": c_run.finish_time,
#            "question": ch.question[challenge_index],
#            "options": (
#                ch.options[challenge_index]
#                if ch.options and isinstance(ch.options[0], list)
#                else ch.options
#            ),
#            "question_further": ch.question_further[challenge_index],
#            "placeholder_text": ch.placeholder_text[challenge_index],
#            "download_text": ch.download_text[challenge_index],
#            "download_path": ch.download_path[challenge_index],
#            "link_text": ch.link_text[challenge_index],
#            "link_path": ch.link_path[challenge_index],
#            "hint_weights": [x[0] for x in ch.hints if x[2] == challenge_index],
#            "hint_unlocked": [x[1] for x in ch.hints if x[2] == challenge_index][:c_run.hints_gotten],
#            "first_blood": fs == effective_username,
#            "solution": (
#                f"Die Antwort ist: {assemble_master_flag(slave_flags, master_format, flag_prefix)}"
#                if c_run.solved and ch.master_task else
#                # MULTIPLE-CHOICE (Bitmask)
#                f"Antworten {', '.join(str(i + 1) for i in range(len(ch.options[challenge_index]))
#                        if (int(ch.solutions[challenge_index]) & (1 << i)))} sind korrekt"
#                if c_run.solved and ch.task_type == "multiple" else
#                # SINGLE-CHOICE (SELECT)
#                (
#                    # Fall A: options ist Liste von Listen (mehrere Fragen)
#                    f"Antwort {ch.options[challenge_index].index(ch.solutions[challenge_index]) + 1} ist korrekt"
#                    if isinstance(ch.options[0], list)
#                    else
#                    # Fall B: options ist flache Liste (eine Frage)
#                    f"Antwort {ch.options.index(ch.solutions[challenge_index]) + 1} ist korrekt"
#                )
#                if c_run.solved and ch.task_type == "select" else
#                # INPUT
#                format_solutions(ch.solutions[challenge_index])
#                if c_run.solved and ch.task_type == "input" else
#                ""
#            )
#        }

    # ---------------------------------------------------------
    # FALL B: RunningChallenge existiert NICHT → Challenge laden
    # ---------------------------------------------------------
    c_che = await Challenge.find_one(
        Challenge.day_id == day,
        Challenge.task_id == task,
        fetch_links=True,
    )

    # Challenge-Dokument sicher laden
    ch = await resolve_link(c_che)

    # first_solved sicher laden
    fs = None
    if ch.first_solved:
        fs_obj = await resolve_link(ch.first_solved)
        fs = getattr(fs_obj, "username", None)

    # challenge_index bestimmen
    if ch.allow_random_order:
        challenge_index = await ch.request_random_index(effective_username, True)
    else:
        challenge_index = await ch.request_random_index(effective_username, False)

    # ---------------------------------------------------------
    # Antwort für ungespielte Challenge
    # ---------------------------------------------------------
    return {
        "current_points": int(ch.points),
        "maximum_points": int(ch.points),

        "question": ch.question[challenge_index],
        "question_further": ch.question_further[challenge_index],
        "placeholder_text": ch.placeholder_text[challenge_index],
        "options": (
            ch.options[challenge_index]
            if ch.options and isinstance(ch.options[0], list)
            else ch.options
        ),

        "hints_point_cap" : [int(math.floor(x.multiplier * ch.points)) for x in ch.hints if x.hint_index == challenge_index],
        "hints_unlocked": [],

        "download_path": ch.download_path[challenge_index],
        "download_text": ch.download_text[challenge_index],

        "solved": False,
        "first_blood": fs == effective_username,
        "is_answerable": is_answerable,

        "solution": ""
    }
#    return {
#        "is_answerable": is_answerable,
#        "day": ch.day_id,
#        "task": ch.task_id,
#        "challenge_index": challenge_index,
#        "tries": 0,
#        "resets": 0,
#        "abs_points": ch.points,
#        "max_points": ch.points,
#        "possible_points": ch.points,
#        "solved": False,
#        "finish_time": None,
#        "question": ch.question[challenge_index],
#        "options": (
#            ch.options[challenge_index]
#            if ch.options and isinstance(ch.options[0], list)
#            else ch.options
#        ),
#        "question_further": ch.question_further[challenge_index],
#        "placeholder_text": ch.placeholder_text[challenge_index],
#        "download_text": ch.download_text[challenge_index],
#        "download_path": ch.download_path[challenge_index],
#        "link_text": ch.link_text[challenge_index],
#        "link_path": ch.link_path[challenge_index],
#        "hint_weights": [x[0] for x in ch.hints if x[2] == challenge_index],
#        "hint_unlocked": [],
#        "first_blood": fs == effective_username,
#        "solution": "",
#    }


@router.get("/get_stats")
async def get_user_stats(
        username: str,
        _: JwtAuthorizationCredentials = Security(access_security),
):
    effective_username, _ = await _resolve_effective_username(username)

    user_challenges = await RunningChallenge.find(
        RunningChallenge.username == effective_username,
        fetch_links=True
    ).sort(+RunningChallenge.day_id, +RunningChallenge.task_id).to_list()

    results = []

    for doc in user_challenges:

        # Challenge-Dokument sicher laden
        ch = doc.challenge
        if hasattr(ch, "fetch"):
            ch = await ch.fetch()

        # First blood sicher prüfen
        fb = False
        if ch:
            fs = getattr(ch, "first_solved", None)
            if fs:
                if hasattr(fs, "fetch"):
                    fs = await fs.fetch()
                if fs and getattr(fs, "username", None) == effective_username:
                    fb = True

        results.append({
            "day": doc.day_id,
            "task": doc.task_id,
            "day_description": ch.day_description if ch else "",
            "task_description": ch.task_description if ch else "",
            "solved": doc.solved,
            "finish_time": doc.finish_time,
            "tries": doc.tries,
            "resets": doc.resets,
            "hints_gotten": doc.hints_gotten,
            "points_earned": doc.points_earned or 0,
            "points_to_get": ch.points if ch else 0,
            "first_blood": fb,
        })

    return results

@router.get("/tasks_solved")
async def tasks_solved(username: str):
    effective_username, _ = await _resolve_effective_username(username)
    tasks_solved = await Challenge.get_tasks_solved(effective_username.lower())
    return tasks_solved


@router.get("/tasks_solved/{day}")
async def tasks_solved(
        username: str,
        day: int,
):
    effective_username, _ = await _resolve_effective_username(username)
    tasks_solved = await Challenge.get_day_tasks_solved(effective_username.lower(), day)
    return tasks_solved


@router.get("/task_points")
async def task_points(username: str):
    task_points = await Challenge.get_task_points(username.lower())
    return task_points


@router.get("/reset_challenges_data/{day}")
async def reset_challenges_data(
        username: str,
        day: int,
        _: JwtAuthorizationCredentials = Security(access_security),
):
    day_reset = await Challenge.reset_day(username.lower(), day)
    return day_reset
