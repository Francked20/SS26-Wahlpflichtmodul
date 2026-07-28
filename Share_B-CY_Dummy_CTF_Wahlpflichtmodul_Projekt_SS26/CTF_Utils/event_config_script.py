import argparse
import os
import requests
import json
import re

# How to use:
# Specify ADMIN_API_TOKEN environment variable e.g. in VS Code terminal:
# $env:ADMIN_API_TOKEN = "adminapitoken"

# Call the script to read the configuration by:
# python .\event_config_script.py read

# Call the script to preregister a specific email address
# python .\event_config_script.py preregister sample.email@fake.com

# Call the script to preregister a batch of email addresses given in file emails.txt
# python .\event_config_script.py preregister_batch email.txt

# python .\event_config_script.py set --event_status true --registration_status true --preregister_mode true --badges_mode true --badges_file dummy_badges.json --player_levels_mode true --rank_config_file dummy_rank_config.json --stats_options_file dummy_stats_options.json --scoreboard_options_file dummy_scoreboard_options.json --teamevent_mode true --teamevent_leader_mode false --teams_list "Sh13ldW@ll,0ff3ns1v3X,C0d3C4T4LY,Arch1t3ct5" --team_colors "rgba(0, 123, 255, 0.65),rgba(220, 53, 69, 0.65),rgba(40, 167, 69, 0.65),rgba(255, 193, 7, 0.65)" --show_answers_mode true --allow_task_reset_mode true --enable_test_mode true --toast_mode false --confetti_mode false

BASE_URL = "https://api.localhost/admin/event"

ADMIN_TOKEN = os.getenv("ADMIN_API_TOKEN")

HEADERS = {
    "X-Admin-Token": ADMIN_TOKEN,
    "Content-Type": "application/json"
}

def get(endpoint: str):
    try:
        resp = requests.get(f"{BASE_URL}/{endpoint}", headers=HEADERS, verify=False)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"GET {endpoint} failed:", e)
        return None

def post(endpoint: str, payload: dict):
    try:
        resp = requests.post(f"{BASE_URL}/{endpoint}", headers=HEADERS, json=payload, verify=False)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"POST {endpoint} failed:", e)
        return None

def read_config():
    endpoints = {
        "Event Badges List":                        "get_event_badges_list",
        "Event Badges Mode":                        "badges_mode",
        "Event Preregister Mode":                   "preregister_mode",
        "Event Registration Status":                "registration_status",
        "Event Status":                             "status",
        "Event Teams List":                         "get_event_teams_list",
        "Event Teamevent Mode":                     "teamevent_mode",
        "Event Teamevent Leader Mode":              "teamevent_leader_mode",
        "Event Team Colors List":                   "get_event_team_colors_list",
        "Event Scoreboard Options":                 "scoreboard/options",
        "Event Show Answers Mode":                  "show_answers_mode",
        "Event Allow Task Reset Mode":              "allow_task_reset_mode",
        "Event Enable Test Mode":                   "enable_test_mode",
        "Event Stats Options":                      "stats/options",
        "Event Rank Config":                        "get_rank_config",
        "Event Player Levels Mode":                 "player_levels_mode",
        "Event Confetti Mode":                      "confetti_mode",
        "Event Toast Mode":                         "toast_mode",
    }

    for name, ep in endpoints.items():
        data = get(ep)
        print(f"{name}: {json.dumps(data, indent=2, ensure_ascii=False)}")

def set_config(args):

    if args.badges_file:
        if not os.path.isfile(args.badges_file):
            print(f"Badges file not found: {args.badges_file}")
        else:
            with open(args.badges_file, "r", encoding="utf-8") as f:
                badges = json.load(f)  # list[dict]
            # Optional: basic validation
            if not isinstance(badges, list) or not all(isinstance(b, dict) and "emoji" in b for b in badges):
                print("Badges file must be a JSON list of objects with 'emoji' (and optional 'tooltip').")
                return
            print("Setting badges list...")
            print(post("set_event_badges_list", {"badges": badges}))

    if args.badges_mode is not None:
        print("Setting badges mode...")
        print(post("badges_mode", {"badges_mode": args.badges_mode}))

    if args.preregister_mode is not None:
        print("Setting preregister mode...")
        print(post("preregister_mode", {"pre_registration": args.preregister_mode}))

    if args.registration_status is not None:
        print("Setting registration status...")
        print(post("registration_status", {"enabled": args.registration_status}))

    if args.event_status is not None:
        print("Setting event status...")
        print(post("status", {"enabled": args.event_status}))

    if args.teamevent_mode is not None:
        print("Setting teamevent mode...")
        print(post("teamevent_mode", {"team_event": args.teamevent_mode}))

    if args.teamevent_leader_mode is not None:
        print("Setting teamevent leader mode...")
        print(post("teamevent_leader_mode", {"team_event_leader": args.teamevent_leader_mode}))

    if args.teams_list:
        teams = [t.strip() for t in args.teams_list.split(",")]
        print("Setting teams list...")
        print(post("set_event_teams_list", {"teams": teams}))

    if args.team_colors:
        raw = args.team_colors.strip()
        # this regex grabs each rgba(…)
        colors = re.findall(r'rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[0-9.]+\s*\)', raw)
        if not colors:
            print("No valid rgba(...) entries found in --team_colors")
        else:
            print("Parsed team colors:", colors)
            print("Setting team colors list…")
            print(post("set_event_team_colors_list", {"team_colors": colors}))

    if args.scoreboard_options_file:
        if not os.path.isfile(args.scoreboard_options_file):
            print(f"Scoreboard options file not found: {args.scoreboard_options_file}")
        else:
            with open(args.scoreboard_options_file, "r", encoding="utf-8") as f:
                opts = json.load(f)
            print("Setting event scoreboard options...")
            print(post("scoreboard/options", opts))

    if args.show_answers_mode is not None:
        print("Setting Show Players with Points Only mode...")
        print(post("show_answers_mode", {"show_answers": args.show_answers_mode}))

    if args.allow_task_reset_mode is not None:
        print("Setting Allow Task Reset mode...")
        print(post("allow_task_reset_mode", {"allow_task_reset": args.allow_task_reset_mode}))

    if args.enable_test_mode is not None:
        print("Setting Enable Test mode...")
        print(post("enable_test_mode", {"enable_test_mode": args.enable_test_mode}))

    if args.stats_options_file:
        if not os.path.isfile(args.stats_options_file):
            print(f"Stats options file not found: {args.stats_options_file}")
        else:
            with open(args.stats_options_file, "r", encoding="utf-8") as f:
                opts = json.load(f)
            print("Setting event stats options...")
            print(post("stats/options", opts))

    if args.rank_config_file:
        if not os.path.isfile(args.rank_config_file):
            print(f"Rank config file not found: {args.rank_config_file}")
        else:
            with open(args.rank_config_file, "r", encoding="utf-8") as f:
                rank_cfg = json.load(f)
            print("Setting rank config...")
            print(post("set_rank_config", rank_cfg))

    if args.player_levels_mode is not None:
        print("Setting Player Levels mode...")
        print(post("player_levels_mode", {"player_levels_mode": args.player_levels_mode}))

    if args.confetti_mode is not None:
        print("Setting Confetti mode...")
        print(post("confetti_mode", {"confetti": args.confetti_mode}))

    if args.toast_mode is not None:
        print("Setting Toast mode...")
        print(post("toast_mode", {"toast": args.toast_mode}))

def preregister_user(email: str):
    try:
        resp = requests.get(
            f"{BASE_URL}/preregister_user",
            headers=HEADERS,
            params={"email": email},
            verify=False
        )
        resp.raise_for_status()
        try:
            print("Preregister user successfully:", resp.json())
        except ValueError:
            print(f"Preregister user (status {resp.status_code}): {resp.text or 'No body'}")
    except requests.exceptions.RequestException as e:
        print("Error preregistering user:", e)

def preregister_users_from_file(file_path: str):
    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        return
    with open(file_path, "r", encoding="utf-8") as f:
        for email in [l.strip() for l in f if l.strip()]:
            print(f"\nPreregistering: {email}")
            preregister_user(email)

def main():
    parser = argparse.ArgumentParser(description="CTF Event Configuration Tool")
    subparsers = parser.add_subparsers(dest="command")

    # read
    subparsers.add_parser("read", help="Read current event configuration")

    # set
    set_parser = subparsers.add_parser("set", help="Set event configuration")
    set_parser.add_argument("--event_status", type=lambda x: x.lower()=='true',
                            help="Enable/disable event")
    set_parser.add_argument("--registration_status", type=lambda x: x.lower()=='true',
                            help="Enable/disable registration")
    set_parser.add_argument("--preregister_mode", type=lambda x: x.lower()=='true',
                            help="Enable/disable preregistration")
    set_parser.add_argument("--badges_mode", type=lambda x: x.lower()=='true',
                            help="Enable/disable badges mode")
    set_parser.add_argument("--badges_file", type=str,
                            help="Path to comma-separated badge emojis file")
    set_parser.add_argument("--teamevent_mode", type=lambda x: x.lower()=='true',
                            help="Enable/disable team event mode")
    set_parser.add_argument("--teamevent_leader_mode", type=lambda x: x.lower()=='true',
                            help="Enable/disable team event leader mode")
    set_parser.add_argument("--teams_list", type=str,
                            help="Comma-separated list of team names")
    set_parser.add_argument("--team_colors",type=str,
                            help="Comma- or space-separated list of CSS rgba(...) codes, e.g. 'rgba(0,123,255,0.65),rgba(220,53,69,0.65)'")
    set_parser.add_argument("--scoreboard_options_file", type=str,
                            help="Path to JSON file with scoreboard options flags")
    set_parser.add_argument("--show_answers_mode", type=lambda x: x.lower()=='true',
                            help="Enable/disable show answers mode")
    set_parser.add_argument("--allow_task_reset_mode", type=lambda x: x.lower()=='true',
                            help="Enable/disable allow task reset mode")
    set_parser.add_argument("--enable_test_mode", type=lambda x: x.lower()=='true',
                            help="Enable/disable test mode")
    set_parser.add_argument("--stats_options_file", type=str,
                            help="Path to JSON file with stats options flags")
    set_parser.add_argument("--rank_config_file", type=str,
                            help="Path to JSON file with rank configuration")
    set_parser.add_argument("--player_levels_mode", type=lambda x: x.lower()=='true',
                            help="Enable/disable player levels mode")
    set_parser.add_argument("--confetti_mode", type=lambda x: x.lower()=='true',
                            help="Enable/disable confetti mode")
    set_parser.add_argument("--toast_mode", type=lambda x: x.lower()=='true',
                            help="Enable/disable toast mode")


    # preregister
    prereg_parser = subparsers.add_parser("preregister", help="Preregister a user by email")
    prereg_parser.add_argument("email", type=str, help="Email address")

    # preregister batch
    batch_parser = subparsers.add_parser("preregister_batch",
                                         help="Preregister multiple users from a file")
    batch_parser.add_argument("file", type=str, help="Path to file with email addresses")

    args = parser.parse_args()
    if not ADMIN_TOKEN:
        print("Error: ADMIN_API_TOKEN environment variable not set.")
        return

    if args.command == "read":
        read_config()
    elif args.command == "set":
        set_config(args)
    elif args.command == "preregister":
        preregister_user(args.email)
    elif args.command == "preregister_batch":
        preregister_users_from_file(args.file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()