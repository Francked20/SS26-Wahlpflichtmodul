# Deployment

1. Repo cloning

Clone the Repository including the submodule via the following command, depending on the authorization mode:

```bash
git clone --recurse-submodules git@gitlab.th-deg.de:tcv_ctf/ctf-template

git clone --recurse-submodules https://gitlab.th-deg.de/tcv_ctf/ctf-template.git
```

2. Environment Variables

- change the three domain variables, but don't change the three subdomains `app`,`scr`,`api` to ensure consistency.
- Change `SET_PRODUCTION_MODE` to true
- modify the three credentials and rotate the JWT secret

3. Branding

For the Branding please checkout `docs/CUSTOMIZATION.md`

4. TLS Certificates

Place the wildcard TLS Certificates in `cert/`. The reverse proxy will use them automatically.

5. `gen_new.sh`

Change the `--project` cli flag to the project name

# Forking

To Develop, always use a Fork, especially for the `ctf-core`.

1. Fork the template or a specific project

2. Fork the Core Repo

3. Change the .gitmodule and point it to the fork repository

## Update the submodule

If you do this for the first time you have to use this command:
```bash
git submodule update --init --remote
```
Consecutively it is the following:
```bash
git submodule update --remote
```

## Fetch Upstream commits

1. Add the upstream as a remote source:
```bash
git remote add upstream git@gitlab.th-deg.de:tcv_ctf/PROJECT.git
```

2. Fetch all the commits from upstream:
```bash
git fetch upstream
```

3. Rebase your fork onto the latest upstream commits:
```bash
git rebase upstream/main
git push --force-with-lease origin main
```
You essentially now have the latest version of the repository with your fork commits on top.
