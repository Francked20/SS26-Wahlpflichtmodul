#! /bin/bash

docker compose down

docker system prune --all --force --volumes

docker volume rm $(docker volume ls -q)

docker compose --project-name ba-mengel up --build -d
