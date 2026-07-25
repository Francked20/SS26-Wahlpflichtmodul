# Development Guidelines

**This file is for writing Content for the Plattform!**

1. Make sure to never hardcode links to any of the three domains:
- `app.*.th-deg.de`: Main Plattform
- `api.*.th-deg.de`: FastAPI Backend
- `scr.*.th-deg.de`: Scoreboard

Instead import `os` to the file and source the domains from the .env File like this:
```python
{os.getenv('DOMAIN')}
``` 
Note that you need to convert the String into a format-string by prefixing it with `f`.

2. Switch to Dockerfile.dev in the docker-compose.yaml to reduce startup time and therefore iteration time.
Also only restart the frontend container

3. Adding Assets for Challenges:

To add Assets, e.g. Pictures to Tasks, please place them into `assets/{Challenge_Number}_{TASK_NUMBER}/`.

## Adding Content

```
custom/
├── assets/
├── sites/
├── tasks/
└── task_conf.py
```

## Challenges

Challenges should be added in the `custom/sites` folder with the following naming convention:
`challenge_01.py`
Starting from 01 counting upwards.

The Challenge files always have the same Structure:

1. Imports

Import the according tasks file:
```python
from web.tasks.challenge_01_tasks import *
```
2. Config

Set the following config options for the challenge:
```python
# URL Filepath
self.url = "/challenge_01"
# Chapter Name in sidebar
self.name = "01: Einführung"
# Icon shown in sidebar, native Reflex support of Lucide: https://lucide.dev/icons/
self.icon = "book-open-text"
# Color used for Heading Color
self.main_color = "#04B486"
# Page is displayed on the sidebar if False
self.is_standalone = False
# Hides sidebar on the page if True
self.hide_sidebar = False
# Events or functions to be executed on site loading
self.on_load = [CondState.check_event_enabled,CondState.check_team_event_mode,CondState.check_team_leader,PlayerCardState.update()]
# Background CSS Class defined in assets/css/page/styles.css
self.background_class = "black"
# User needs to be logged in to show site
self.auth_required = True
# Define a Datetime object on which the site gets accessible, only applied in production mode
self.unlock_day = unlock_241201
```

3. For writing the actual content, please refer to the example file.

For example to write inline codeblocks:
```python
rx.code("tcv{...}", color="yellow.300")
```

## Conversations

Conversations can be added in the Challenge FIle like this:
```python
rx.flex(
    rx.spacer(),
    rx.link(rx.button(rx.icon(tag="message-circle-more"),"Nehmen Sie mit uns Kontakt auf..."), href=f"https://{os.getenv('DOMAIN')}/convo_01/"),
    rx.spacer(),
    width="100%",
)
```
Essentially it is just a button referring to the Conversation URL

Conversations should be added in the `custom/sites` folder with the following naming convention:
`convo_01.py`
Starting from 01 counting upwards.

There are always two people in the conversation. You yourself and the other person.
All of the Images are stored in `assets/poses/`.

**Your Avatar:**\
This is loaded via the rx.image defined in the file. Loading the avatar, which was chosen at registration, from the browsers localstorage.

**The other Person:**\
The Person is defined in the python code. In the Conversation Code a `pose_left` argument is supplied.
For each pose a separate file is available. The filenames therefore are dynamically concatenated via the player name and pose.

## Tasks

Tasks can be added in the Challenge File like this:
```python
rx.cond(
    (~CondState.team_event_mode) | (CondState.team_event_mode & CondState.team_leader),
    TaskWidget(task_01_00),
    TaskWidgetTeamMember(task_01_00_tm),
)
```
The conditions assures that the task is only shown if either team event mode is off, OR it's on and the user is the team leader.

Tasks should be added in the `custom/tasks` folder with the following naming convention:
`challenge_01_tasks.py`
Starting from 01 counting upwards.

The files are then synced by the frontend into the database and when called from a challenge file the task is loaded via the task engine from the database.
