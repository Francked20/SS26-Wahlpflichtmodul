Use this command for iterative Development:
```bash
docker compose --project-name PROJECTNAME up --build --force-recreate
```

Rebuild a specific container:
```bash
docker compose --project-name PROJECTNAME up --build --force-recreate scoreboard
```

Stop all containers:
```bash
docker stop $(docker ps -q)
```

View the Database interactively:
```bash
tongo --url 'mongodb://admin:very-strong-admin-password@localhost:27017/?authSource=admin'
```

Get a Shell inside a container:
```bash
docker exec -it ID sh
```