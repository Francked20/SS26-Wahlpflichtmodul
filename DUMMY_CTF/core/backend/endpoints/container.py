import os
import logging

from fastapi import APIRouter, HTTPException, Request, Security
from fastapi.params import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi_jwt import JwtAuthorizationCredentials
from pydantic import BaseModel, field_validator
from kubernetes.client.rest import ApiException
from kubernetes import client
import datetime

from database.models import *
from utils.security import access_security
from utils.kubernetes import *

from endpoints.users import _resolve_effective_username

router = APIRouter()

@router.post("/code/start")
async def start_container(
    request: Request,
    auth: JwtAuthorizationCredentials = Security(access_security),
):
    username = auth.subject["username"].lower()
    subdomain = generate_subdomain(username)

    # Einheitliche Namen
    name = f"code-{subdomain}-{os.getenv('CONTAINER')}"
    pvc_name = f"pvc-{subdomain}-{os.getenv('CONTAINER')}"
    host = f"{name}.{os.getenv('ROOT')}"

    ttl_seconds = 21600  # 6 hours TTL
    expiry_timestamp = (datetime.datetime.utcnow() + datetime.timedelta(seconds=ttl_seconds)).isoformat() + "Z"

    apps_v1 = request.app.state.k8s_apps_v1
    core_v1 = request.app.state.k8s_core_v1
    networking_v1 = client.NetworkingV1Api()

    # Prüfen, ob Deployment schon existiert
    try:
        apps_v1.read_namespaced_deployment(name=name, namespace=os.getenv("NAMESPACE"))
        ingress = networking_v1.read_namespaced_ingress(name=name, namespace=os.getenv("NAMESPACE"))
        existing_host = ingress.spec.rules[0].host
        raise HTTPException(
            status_code=409,
            detail={
                "message": f"code-server für '{username}' läuft bereits",
                "url": f"https://{existing_host}",
            },
        )
    except ApiException as e:
        if e.status != 404:
            logging.error(f"Fehler beim Prüfen des Deployments für {username}: {e}")
            raise HTTPException(status_code=500, detail=e.body or e.reason)

    # PVC nur anlegen, wenn es noch nicht existiert
    try:
        core_v1.read_namespaced_persistent_volume_claim(name=pvc_name, namespace=os.getenv("NAMESPACE"))
        logging.info(f"PVC {pvc_name} existiert bereits, wird wiederverwendet")
    except ApiException as e:
        if e.status == 404:
            pvc = make_codeserver_pvc(pvc_name, expiry_timestamp)
            core_v1.create_namespaced_persistent_volume_claim(namespace=os.getenv("NAMESPACE"), body=pvc)
            logging.info(f"PVC {pvc_name} neu erstellt")
        else:
            logging.error(f"Fehler beim Prüfen des PVC {pvc_name}: {e}")
            raise HTTPException(status_code=500, detail=e.body or e.reason)

    # Deployment, Service, Ingress erzeugen
    deployment = make_codeserver_deployment(name, pvc_name, expiry_timestamp)
    service = make_codeserver_service(name, expiry_timestamp)
    route = make_codeserver_ingress(subdomain=subdomain, host=host, service_name=name, expiry_timestamp=expiry_timestamp)

    try:
        apps_v1.create_namespaced_deployment(namespace=os.getenv("NAMESPACE"), body=deployment)
        core_v1.create_namespaced_service(namespace=os.getenv("NAMESPACE"), body=service)
        networking_v1.create_namespaced_ingress(namespace=os.getenv("NAMESPACE"), body=route)
    except ApiException as e:
        logging.error(f"Fehler beim Starten von code-server für {username}: {e}")
        raise HTTPException(status_code=500, detail=e.body or e.reason)

    return {"status": "started", "name": name, "url": f"https://{host}"}

@router.post("/code/stop")
async def stop_container(
    request: Request,
    auth: JwtAuthorizationCredentials = Security(access_security),
):
    username = auth.subject["username"].lower()
    subdomain = generate_subdomain(username)

    name = f"code-{subdomain}-{os.getenv('CONTAINER')}"
    pvc_name = f"pvc-{subdomain}-{os.getenv('CONTAINER')}"  # bleibt bestehen

    apps_v1 = request.app.state.k8s_apps_v1
    core_v1 = request.app.state.k8s_core_v1
    networking_v1 = client.NetworkingV1Api()

    # Deployment löschen
    try:
        apps_v1.delete_namespaced_deployment(name=name, namespace=os.getenv("NAMESPACE"))
    except ApiException as e:
        if e.status != 404:
            logging.error(f"Fehler beim Löschen des Deployments {name}: {e}")
            raise HTTPException(status_code=500, detail=e.body or e.reason)

    # Service löschen
    try:
        core_v1.delete_namespaced_service(name=name, namespace=os.getenv("NAMESPACE"))
    except ApiException as e:
        if e.status != 404:
            logging.error(f"Fehler beim Löschen des Service {name}: {e}")
            raise HTTPException(status_code=500, detail=e.body or e.reason)

    # Ingress löschen
    try:
        networking_v1.delete_namespaced_ingress(name=name, namespace=os.getenv("NAMESPACE"))
    except ApiException as e:
        if e.status != 404:
            logging.error(f"Fehler beim Löschen des Ingress {name}: {e}")
            raise HTTPException(status_code=500, detail=e.body or e.reason)

    # PVC bleibt bestehen
    logging.info(f"PVC {pvc_name} bleibt erhalten für User {username}")

    return {"status": "stopped", "name": name}

@router.get("/code/status")
async def get_container_status(
    request: Request,
    auth: JwtAuthorizationCredentials = Security(access_security),
):
    username = auth.subject["username"].lower()
    subdomain = generate_subdomain(username)
    name = f"code-{subdomain}-{os.getenv('CONTAINER')}"

    apps_v1 = request.app.state.k8s_apps_v1
    networking_v1 = client.NetworkingV1Api()

    try:
        # Prüfe ob das Deployment existiert
        deployment = apps_v1.read_namespaced_deployment(name=name, namespace=f"{os.getenv('NAMESPACE')}")

        # If it exists, check for matching Ingress and return existing subdomain URL
        ingress_name = f"code-{subdomain}-{os.getenv('CONTAINER')}"
        host = None
        try:
            ingress = networking_v1.read_namespaced_ingress(name=ingress_name, namespace=f"{os.getenv('NAMESPACE')}")
            host = ingress.spec.rules[0].host
        except ApiException as ingress_exc:
            raise HTTPException(status_code=500, detail=ingress_exc.body or ingress_exc.reason)

        return {
            "running": True,
            "url": f"https://{host}" if host else None,
        }

    except ApiException as e:
        if e.status == 404:
            return {
                "running": False,
            }
        else:
            logging.error(f"Error checking status for {username}: {e}")
            raise HTTPException(status_code=500, detail=e.body or e.reason)


@router.post("/code/extend")
async def extend_container_ttl(
    request: Request,
    auth: JwtAuthorizationCredentials = Security(access_security),
):
    username = auth.subject["username"].lower()
    subdomain = generate_subdomain(username)
    name = f"code-{subdomain}-{os.getenv('CONTAINER')}"

    apps_v1 = request.app.state.k8s_apps_v1
    core_v1 = request.app.state.k8s_core_v1
    networking_v1 = client.NetworkingV1Api()

    ttl_seconds = 21600  # extend by 6 hours
    new_expiry = (datetime.datetime.utcnow() + datetime.timedelta(seconds=ttl_seconds)).isoformat() + "Z"

    patch_body = {
        "metadata": {
            "annotations": {
                "cleanup/expiry": new_expiry
            }
        }
    }

    async def patch_resource(api, patch_func, name, namespace=f"{os.getenv('NAMESPACE')}"):
        try:
            patch_func(name=name, namespace=namespace, body=patch_body)
        except ApiException as e:
            if e.status == 404:
                raise HTTPException(status_code=404, detail=f"Resource {name} not found")
            logging.error(f"Error patching resource {name}: {e}")
            raise HTTPException(status_code=500, detail=e.body or e.reason)

    # Patch deployment
    await patch_resource(apps_v1, apps_v1.patch_namespaced_deployment, name)
    # Patch service
    await patch_resource(core_v1, core_v1.patch_namespaced_service, name)
    # Patch ingress
    await patch_resource(networking_v1, networking_v1.patch_namespaced_ingress, name)

    return {
        "status": "extended",
        "name": name,
        "new_expiry": new_expiry,
        "message": f"Extended TTL by {ttl_seconds} seconds",
    }

class ChallengePVC(BaseModel):
    day_id: int
    task_id: int

@router.post("/code/inject_challenge_pvc")
async def inject_challenge_pvc(
    request: Request,
    ch_data: ChallengePVC,
    auth: JwtAuthorizationCredentials = Security(access_security),
):
    username = auth.subject["username"].lower()
    safe_username = sanitize_k8s_name(username)
    subdomain = generate_subdomain(username)

    pvc_name = f"pvc-{subdomain}-{os.getenv('CONTAINER')}"
    namespace = os.getenv("NAMESPACE")

    effective_username, _ = await _resolve_effective_username(username)
    c_run = await RunningChallenge.find_one(
        RunningChallenge.username == effective_username,
        RunningChallenge.day_id == ch_data.day_id,
        RunningChallenge.task_id == ch_data.task_id,
        fetch_links=True
    )

    job_name = f"inject-pvc-{c_run.day_id:02d}-{c_run.task_id:02d}-{c_run.random_index:02d}-{safe_username}"

    batch_v1 = client.BatchV1Api()
    job = make_injector_job_pvc(
        job_name,
        pvc_name,
        f"{c_run.day_id:02d}",
        f"{c_run.task_id:02d}",
        f"{c_run.random_index:02d}",
        namespace
    )

    try:
        batch_v1.create_namespaced_job(namespace=namespace, body=job)
        return {
            "status": "injecting",
            "day": c_run.day_id,
            "task": c_run.task_id,
            "challenge": c_run.random_index,
            "pvc": pvc_name,
            "message": f"Challenge {c_run.day_id:02d}-{c_run.task_id:02d}-{c_run.random_index:02d} wird in Workspace injiziert"
        }
    except ApiException as e:
        if e.status == 409:
            raise HTTPException(
                status_code=409,
                detail=f"Injection für Challenge {c_run.day_id:02d}-{c_run.task_id:02d}-{c_run.random_index:02d} läuft bereits"
            )
        else:
            logging.error(f"Fehler beim Erzeugen des Injector-Jobs: {e}")
            raise HTTPException(status_code=500, detail=e.body or e.reason)

"""
KALI Setup below!
"""

@router.post("/kali/start")
async def start_container(
    request: Request,
    auth: JwtAuthorizationCredentials = Security(access_security),
):
    username = auth.subject["username"].lower()
    subdomain = generate_subdomain(username)
    name = f"kali-{subdomain}-{os.getenv('CONTAINER')}"
    host = f"{name}.{os.getenv('ROOT')}"

    ttl_seconds = 21600  # 6 hours TTL
    expiry_timestamp = (datetime.datetime.utcnow() + datetime.timedelta(seconds=ttl_seconds)).isoformat() + "Z"

    apps_v1 = request.app.state.k8s_apps_v1
    core_v1 = request.app.state.k8s_core_v1
    networking_v1 = client.NetworkingV1Api()

    # Check if deployment already exists
    try:
        apps_v1.read_namespaced_deployment(name=name, namespace=f"{os.getenv('NAMESPACE')}")

        # If it exists, check for matching Ingress and return existing subdomain URL
        ingress_name = f"kali-{subdomain}-{os.getenv('CONTAINER')}"
        try:
            ingress = networking_v1.read_namespaced_ingress(name=ingress_name, namespace=f"{os.getenv('NAMESPACE')}")
            existing_host = ingress.spec.rules[0].host
        except ApiException as ingress_exc:
            if ingress_exc.status == 404:
                existing_host = host
            else:
                logging.error(f"Error reading HTTPRoute for {username}: {ingress_exc}")
                raise HTTPException(status_code=500, detail=ingress_exc.body or ingress_exc.reason)

        logging.warning(f"Deployment '{name}' already exists for user {username}, reusing subdomain")
        raise HTTPException(
            status_code=409,
            detail={
                "message": f"kali for '{username}' is already running",
                "url": f"https://{existing_host}",
            },
        )
    except ApiException as e:
        if e.status != 404:
            logging.error(f"Error checking deployment for {username}: {e}")
            raise HTTPException(status_code=500, detail=e.body or e.reason)

    # If we reach here, deployment doesn't exist → create it
    deployment = make_kali_deployment(name, expiry_timestamp)
    service = make_kali_service(name, expiry_timestamp)
    route = make_kali_ingress(subdomain=subdomain, host=host, service_name=name, expiry_timestamp=expiry_timestamp)

    try:
        apps_v1.create_namespaced_deployment(namespace=f"{os.getenv('NAMESPACE')}", body=deployment)
        core_v1.create_namespaced_service(namespace=f"{os.getenv('NAMESPACE')}", body=service)
        networking_v1.create_namespaced_ingress(namespace=f"{os.getenv('NAMESPACE')}", body=route)
    except ApiException as e:
        logging.error(f"Failed to start code-server for {username}: {e}")
        raise HTTPException(status_code=500, detail=e.body or e.reason)

    return {"status": "started", "name": name, "url": f"https://{host}"}


@router.post("/kali/stop")
async def stop_container(
    request: Request,
    auth: JwtAuthorizationCredentials = Security(access_security),
):
    username = auth.subject["username"].lower()
    subdomain = generate_subdomain(username)
    name = f"kali-{subdomain}-{os.getenv('CONTAINER')}"

    apps_v1 = request.app.state.k8s_apps_v1
    core_v1 = request.app.state.k8s_core_v1
    networking_v1 = client.NetworkingV1Api()

    try:
        apps_v1.delete_namespaced_deployment(name=name, namespace=f"{os.getenv('NAMESPACE')}")
    except ApiException as e:
        if e.status != 404:
            logging.error(f"Error deleting deployment {name}: {e}")
            raise HTTPException(status_code=500, detail=e.body or e.reason)

    try:
        core_v1.delete_namespaced_service(name=name, namespace=f"{os.getenv('NAMESPACE')}")
    except ApiException as e:
        if e.status != 404:
            logging.error(f"Error deleting service {name}: {e}")
            raise HTTPException(status_code=500, detail=e.body or e.reason)
    
    try:
        networking_v1.delete_namespaced_ingress(name=name, namespace=f"{os.getenv('NAMESPACE')}")
    except ApiException as e:
        if e.status != 404:
            logging.error(f"Error deleting ingress {name}: {e}")
            raise HTTPException(status_code=500, detail=e.body or e.reason)

    return {"status": "stopped", "name": name}

@router.get("/kali/status")
async def get_container_status(
    request: Request,
    auth: JwtAuthorizationCredentials = Security(access_security),
):
    username = auth.subject["username"].lower()
    subdomain = generate_subdomain(username)
    name = f"kali-{subdomain}-{os.getenv('CONTAINER')}"

    apps_v1 = request.app.state.k8s_apps_v1
    networking_v1 = client.NetworkingV1Api()

    try:
        # Prüfe ob das Deployment existiert
        deployment = apps_v1.read_namespaced_deployment(name=name, namespace=f"{os.getenv('NAMESPACE')}")

        # If it exists, check for matching Ingress and return existing subdomain URL
        ingress_name = f"kali-{subdomain}-{os.getenv('CONTAINER')}"
        host = None
        try:
            ingress = networking_v1.read_namespaced_ingress(name=ingress_name, namespace=f"{os.getenv('NAMESPACE')}")
            host = ingress.spec.rules[0].host
        except ApiException as ingress_exc:
            raise HTTPException(status_code=500, detail=ingress_exc.body or ingress_exc.reason)

        return {
            "running": True,
            "url": f"https://{host}" if host else None,
        }

    except ApiException as e:
        if e.status == 404:
            return {
                "running": False,
            }
        else:
            logging.error(f"Error checking status for {username}: {e}")
            raise HTTPException(status_code=500, detail=e.body or e.reason)


@router.post("/kali/extend")
async def extend_container_ttl(
    request: Request,
    auth: JwtAuthorizationCredentials = Security(access_security),
):
    username = auth.subject["username"].lower()
    subdomain = generate_subdomain(username)
    name = f"kali-{subdomain}-{os.getenv('CONTAINER')}"

    apps_v1 = request.app.state.k8s_apps_v1
    core_v1 = request.app.state.k8s_core_v1
    networking_v1 = client.NetworkingV1Api()

    ttl_seconds = 21600  # extend by 6 hours
    new_expiry = (datetime.datetime.utcnow() + datetime.timedelta(seconds=ttl_seconds)).isoformat() + "Z"

    patch_body = {
        "metadata": {
            "annotations": {
                "cleanup/expiry": new_expiry
            }
        }
    }

    async def patch_resource(api, patch_func, name, namespace=f"{os.getenv('NAMESPACE')}"):
        try:
            patch_func(name=name, namespace=namespace, body=patch_body)
        except ApiException as e:
            if e.status == 404:
                raise HTTPException(status_code=404, detail=f"Resource {name} not found")
            logging.error(f"Error patching resource {name}: {e}")
            raise HTTPException(status_code=500, detail=e.body or e.reason)

    # Patch deployment
    await patch_resource(apps_v1, apps_v1.patch_namespaced_deployment, name)
    # Patch service
    await patch_resource(core_v1, core_v1.patch_namespaced_service, name)
    # Patch ingress
    await patch_resource(networking_v1, networking_v1.patch_namespaced_ingress, name)

    return {
        "status": "extended",
        "name": name,
        "new_expiry": new_expiry,
        "message": f"Extended TTL by {ttl_seconds} seconds",
    }


@router.get("/test-connection")
async def test_k8s_connection(request: Request):
    core_v1 = request.app.state.k8s_core_v1

    try:
        pods = core_v1.list_pod_for_all_namespaces(limit=1)
        pod_names = [pod.metadata.name for pod in pods.items]

        logging.info(f"Kubernetes API reachable, pods found: {pod_names}")
        return {"message": "Kubernetes API connection successful", "pods_found": pod_names}

    except ApiException as e:
        logging.error(f"Kubernetes API exception: {e}")
        raise HTTPException(status_code=500, detail=f"Kubernetes API error: {e}")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
