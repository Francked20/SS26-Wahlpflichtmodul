from argon2 import PasswordHasher  # pip install argon2-cffi
import base64

def generate_user_insert_command(password: str,
                                 team: str,
                                 team_color: str,
                                 is_leader: bool) -> str:
    """Baut ein MongoDB insertOne Command fuer einen einzelnen User"""
    # Remove the trailing two-digit index to get the base name + team initial
    trimmed = password[:-3]
    
    username = trimmed.lower()
    display = trimmed
    email = f"{username}@tcv-events.th-deg.de"
    
    # Encode password, then re-decode and hash with Argon2
    encoded_pw = base64.urlsafe_b64encode(password.encode()).decode()
    ph = PasswordHasher(time_cost=3, memory_cost=65_536, parallelism=4)
    pw_hash = ph.hash(base64.urlsafe_b64decode(encoded_pw).decode())
    
    leader_str = "true" if is_leader else "false"

    return (
        f'db.users.insertOne({{'
        f'username: "{username}", '
        f'username_display: "{display}", '
        f'email: "{email}", '
        f'pw_hash: "{pw_hash}", '
        f'avatar_index: "9", '
        f'team: "{team}", '
        f'team_leader: {leader_str}, '
        f'team_color: "{team_color}", '
        f'stats: {{'
            f'points: 0, '
            f'challenges_solved: 0, '
            f'streak: 0, '
            f'first_solves: 0, '
            f'badges: []'
        f'}}'
        f'}});'
    )

if __name__ == "__main__":
    # 1) Define your teams and colors
    team_list = [
        "Sh13ldW@ll",  # Blue – Defensive Security
        "0ff3ns1v3X",  # Red – Offensive Security
        "C0d3C4T4LY",  # Green – Security Automation & Design
        "Arch1t3ct5",  # Yellow – Software Coders & Architects
    ]
    team_color_list = [
        "rgba(0, 123, 255, 0.65)",
        "rgba(220, 53, 69, 0.65)",
        "rgba(40, 167, 69, 0.65)",
        "rgba(255, 193, 7, 0.65)"
    ]

    # 2) Define which single-char prefix to append for each team's password
    password_char = ["b", "r", "g", "y"]

    # 3) Supply a list of username-bases for each team
    teams_usernames = [ 
        ["D3f@nzor", "L0gG@urd", "S3nT!nel", "N@tGuard", "B1uW@tch", "C@lmScan", "S1afeH@v", "P@cF0rtz", "BluSh!ld", "W@llF1sh", "Qu@rHawk", "C0v3D@ta", "N0r=L0ck", "Tr@cPath", "F@stHold", "S3curN@v"], # blue 
        ["H@ckB0tz", "B@shWolf", "R3dn@tor", "PwnF!rez", "C0deD@rk", "Sh@dPwny", "Expl0!tr", "D3@dScan", "R3v@ngel", "N1ghtF@x", "S3cH@vok", "Br3@kOut", "Z3r0F@ce", "T@pSnake", "H@rdFall", "V1r@Hawk"], # red 
        ["Safe@Xen", "Gr@nLock", "C0de!Meh", "Guard#ix", "V3rde$ec", "Secu&Bot", "Aut0$Lay", "Gr!dCraf", "Z@neCure", "Dev$Mint", "F0rm#Sec", "Grn&Code", "Patch@Up", "Gree!Net", "Lock#pix", "Buil*Sfe"], # green 
        ["Dev!Bloc", "Arch#Tag", "Bit@Plan", "Cod3#Map", "Struc!It", "Layr$Dev", "Yel!Node", "Synth#Up", "Log@Form", "Pic$Fold", "Solv#Box", "Crea$Yel", "Modu!Fix", "Arti@Lab", "Prgm#Ink", "Path@Rch"] # yellow
    ]

    # 4) Open file and write out passwords + MongoDB commands
    output_file = "Wahlpflichtmodul_Projekt_Dummy_CTF_User_Inserts.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        for team, color, names, pchar in zip(team_list, team_color_list, teams_usernames, password_char):

            for idx, base in enumerate(names):
                # first member is leader
                is_leader = (idx == 0)

                pwd = f"{base}{pchar}{idx:02d}"
                # write the mongo insert command
                cmd = generate_user_insert_command(
                    password=pwd,
                    team=team,
                    team_color=color,
                    is_leader=is_leader
                )
                f.write(cmd + "\n\n")
    
    print(f"All commands and passwords written to {output_file}")
