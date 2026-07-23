# Customization

The CTF-Plattform can be customized via the .env File to set basic settings, like the Heading, Title Page and so on.

All other customization can be set inside the `custom/` Folder, which is mounted into the Frontend Docker Container.

The `custom`-folder in the ctf-template directory serves as a reference. Commits should be cherry-picked into the different project folders as often as possible to avoid fragmentation.

The File Structure with all the important files is the following:

```
custom/
├── assets/
│   ├── 01_00/
│   ├── 01_01/
│   ├── 01_02/
│   ├── convo_background/
│   │   └── background.jpg
│   ├── css/
│   ├── images/
│   │   └── background.jpg
│   ├── players/
│   ├── poses/
│   ├── Datenschutzinformation_CTF.pdf
│   ├── Einverständniserklärung_CTF.pdf
│   └── favicon.ico
├── sites/
│   ├── errors/
│   │   └── ErrorPages.py
│   ├── general/
│   │   ├── login_chapter_selection.py
│   │   ├── login_limbo.py
│   │   ├── register.py
│   │   ├── reset_pw.py
│   │   └── welcome.py
│   ├── challenge_01.py
│   ├── challenge_02.py
│   ├── convo_01.py
│   ├── convo_02.py
│   └── spielregeln.py
├── tasks/
│   ├── challenge_01_tasks.py
│   └── challenge_02_tasks.py
└── task_conf.py
```

For visual customization the following are the most important:
- `assets/images/background.jpg` -> This is the Background Image on the login page
- `assets/convo_background/background.jpg` -> This is the Background Image shown at conversations
- `assets/favicon.ico` -> The Icon displayed in the browser

# Submodule

Should it be necessary for a project to add project-specific modifications to the core-code that cannot or should not be upstreamed, it is possible to stay in sync with upstream by modifying the git commit needed to update the submodule specified in `DEPLOYMENT.md`:
```bash
git submodule update --remote --merge
``` 
This will rebase your custom commits onto the latest upstream version.