import os
import asyncio
import contextlib
import logging

import fastapi
import httpx

from kubernetes import config, client

from database.connection import MongoDB


@contextlib.asynccontextmanager
async def fastapi_lifespan(app: fastapi.FastAPI):
    """Ensure clean startup and shutdown"""

    # Before startup
    if MongoDB.instance is None:
        MongoDB.instance = MongoDB()

    instance = MongoDB.instance
    logging.info("Waiting for database connection")

    await instance.ping()
    logging.info("Connected to database")

    await instance.connect_mapper()
    logging.info("Loaded Beanie mapper")

#    loop = asyncio.get_event_loop()

    # ——— Kubernetes startup ———
    # Load in-cluster (or fall back to kubeconfig for local dev)
    try:
        config.load_incluster_config()
        logging.info("Loaded in-cluster kubeconfig")
    except config.ConfigException:
        try:
            config.load_kube_config()
            logging.info("Loaded local kubeconfig")
        except:
            logging.info("Started without Kubernetes support")


    # Create API clients and store on app.state
    app.state.k8s_core_v1 = client.CoreV1Api()
    app.state.k8s_apps_v1 = client.AppsV1Api()
    logging.info("Kubernetes clients initialized")

    yield

    # After shutdown

    await instance.disconnect()
    logging.info("Disconnected from database")
