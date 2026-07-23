from kubernetes import client
import hashlib
import os
import re

def sanitize_k8s_name(name: str) -> str:
    # Kleinbuchstaben
    name = name.lower()
    # Ungültige Zeichen durch '-'
    name = re.sub(r'[^a-z0-9.-]', '-', name)
    # Mehrere '-' zusammenfassen
    name = re.sub(r'-+', '-', name)
    # Am Anfang/Ende keine '-'
    name = name.strip('-')
    return name

def generate_subdomain(username: str) -> str:
    return hashlib.sha256(username.encode()).hexdigest()[:6]

def make_codeserver_pvc(name: str, expiry_timestamp: str) -> client.V1PersistentVolumeClaim:
    return client.V1PersistentVolumeClaim(
        metadata=client.V1ObjectMeta(
            name=name,
            annotations={"expiry": expiry_timestamp},
        ),
        spec=client.V1PersistentVolumeClaimSpec(
            access_modes=["ReadWriteOnce"],
            resources=client.V1ResourceRequirements(
                requests={"storage": "128Mi"}
            ),
            storage_class_name="local-path"  # ggf. anpassen
        )
    )

def make_codeserver_ingress(subdomain: str,host: str, service_name: str, expiry_timestamp: str) -> client.V1Ingress:

    ingress = client.V1Ingress(
        metadata=client.V1ObjectMeta(
            name=f"{service_name}",
#            namespace="default",
            annotations={
                "expiry": expiry_timestamp,
            },
        ),
        spec=client.V1IngressSpec(
            tls=[
                client.V1IngressTLS(
                    hosts=[host],
                    secret_name="api-tls-cert",
                )
            ],
            rules=[
                client.V1IngressRule(
                    host=host,
                    http=client.V1HTTPIngressRuleValue(
                        paths=[
                            client.V1HTTPIngressPath(
                                path="/",
                                path_type="Prefix",
                                backend=client.V1IngressBackend(
                                    service=client.V1IngressServiceBackend(
                                        name=service_name,
                                        port=client.V1ServiceBackendPort(number=8443),
                                    )
                                ),
                            )
                        ]
                    ),
                )
            ],
        )
    )
    return ingress

VSCODE_IMAGE_MAP = {
    "chipwhisperer": "registry.gitlab.th-deg.de/tcv_ctf/project-chip-whisperer:vscode",
    "tcv-events-ba-m-engel": "registry.gitlab.th-deg.de/tcv_ctf/project-tcv-events-ba-m-engel:vscode",
    # weitere Einträge hier ergänzen
}

def get_codeserver_image() -> str:
    key = os.getenv("VSCODE_IMAGE_KEY", "default")
    return VSCODE_IMAGE_MAP.get(key, "registry.gitlab.th-deg.de/tcv_ctf/project-tcv-events-ba-m-engel:vscode")

def make_codeserver_deployment(name: str, pvc_name: str, expiry_timestamp: str) -> client.V1Deployment:
    enable_cw_traces = os.getenv("ENABLE_CW_TRACES", "False").lower() == "true"

    volume_mounts = [
        client.V1VolumeMount(
            name="user-storage",
            mount_path="/config/workspace"
        )
    ]
    volumes = [
        client.V1Volume(
            name="user-storage",
            persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                claim_name=pvc_name
            )
        )
    ]

    if enable_cw_traces:
        volume_mounts.append(
            client.V1VolumeMount(
                name="cw-traces-pvc",
                mount_path="/config/chipwhisperer/traces",
                read_only=True
            )
        )
        volumes.append(
            client.V1Volume(
                name="cw-traces-pvc",
                persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                    claim_name="cw-traces-pvc"
                )
            )
        )

    return client.V1Deployment(
        metadata=client.V1ObjectMeta(
            name=name,
            labels={"app": name},
            annotations={"expiry": expiry_timestamp},
        ),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector=client.V1LabelSelector(match_labels={"app": name}),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": name}),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="code-server",
                            image=get_codeserver_image(),
#                            image_pull_policy="IfNotPresent",
                            image_pull_policy="Always",
                            ports=[client.V1ContainerPort(container_port=8443)],
                            volume_mounts=volume_mounts,
                        )
                    ],
                    volumes=volumes,
                    image_pull_secrets=[
                        client.V1LocalObjectReference(name="gitlab-registry-secret")
                    ]
                )
            )
        )
    )

def make_codeserver_service(name: str, expiry_timestamp: str) -> client.V1Service:
    return client.V1Service(
        metadata=client.V1ObjectMeta(
            name=name,
            annotations={
                "expiry": expiry_timestamp,
            },
        ),
        spec=client.V1ServiceSpec(
            selector={"app": name},
            ports=[client.V1ServicePort(port=8443, target_port=8443)],
            type="ClusterIP"
        )
    )

def make_injector_job(job_name: str, pvc_name: str, configmap_name: str, namespace: str):
    container = client.V1Container(
        name="injector",
        image="alpine:3.18",
        command=["/bin/sh", "-c"],
        args=[
            "set -e; "
            "mkdir -p /config/workspace/challenge; "
            "rm -rf /config/workspace/challenge/*; "
            "find -L /challenge -maxdepth 1 -type f -exec cp {} /config/workspace/challenge/ \\;; "
            "chmod -R u+rwX,go+rwX /config/workspace/challenge; "
            "touch /config/workspace/challenge/* || true; "
            "ls -l /config/workspace/challenge; "
            'echo \"Injection complete.\"'
        ],
        volume_mounts=[
            client.V1VolumeMount(name="user-pvc", mount_path="/config/workspace"),
            client.V1VolumeMount(name="challenge-files", mount_path="/challenge"),
        ],
    )

    pod_spec = client.V1PodSpec(
        restart_policy="Never",
        service_account_name=os.getenv("CTF_SERVICEACCOUNT_NAME", "ctf-serviceaccount"),
        containers=[container],
        volumes=[
            client.V1Volume(
                name="user-pvc",
                persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(claim_name=pvc_name),
            ),
            client.V1Volume(
                name="challenge-files",
                config_map=client.V1ConfigMapVolumeSource(name=configmap_name),
            ),
        ],
    )

    # PodTemplateSpec
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"job": job_name}),
        spec=pod_spec,
    )

    # JobSpec mit TTL
    job_spec = client.V1JobSpec(
        template=template,
        backoff_limit=0,
        ttl_seconds_after_finished=10,  # <-- hier: 10 Sekunden nach Abschluss löschen
    )

    # V1Job
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=job_name, namespace=namespace),
        spec=job_spec,
    )

    return job

def make_injector_job_pvc(job_name: str, pvc_name: str, challenge_day: str, challenge_task: str, challenge_index: str, namespace: str):
    container = client.V1Container(
        name="injector",
        image="alpine:3.18",
        command=["/bin/sh", "-c"],
        args=[
            (
                "set -e; "
                "mkdir -p /config/workspace/challenge; "
                "rm -rf /config/workspace/challenge/*; "
                f"ls -l /assets/{challenge_day}{challenge_task}; "
                f"find /assets/{challenge_day}{challenge_task} -maxdepth 1 -type f -exec cp {{}} /config/workspace/challenge/ \\; || true; "
                f"if [ -d /assets/{challenge_day}{challenge_task}/{challenge_index} ]; then "
                f"cp -r /assets/{challenge_day}{challenge_task}/{challenge_index}/* /config/workspace/challenge/ || true; "
                "fi; "
                "chmod -R u+rwX,go+rwX /config/workspace/challenge; "
                "ls -l /config/workspace/challenge; "
                "echo 'Injection complete.'"
            )
        ],
        volume_mounts=[
            client.V1VolumeMount(name="user-pvc", mount_path="/config/workspace"),
            client.V1VolumeMount(name="assets-pvc", mount_path="/assets"),
        ],
        security_context=client.V1SecurityContext(
            allow_privilege_escalation=False,
            run_as_non_root=True,
            run_as_user=1000,
            capabilities=client.V1Capabilities(drop=["ALL"]),
            seccomp_profile=client.V1SeccompProfile(type="RuntimeDefault"),
        ), 
    )

    pod_spec = client.V1PodSpec(
        restart_policy="Never",
        service_account_name=os.getenv("CTF_SERVICEACCOUNT_NAME", "ctf-serviceaccount"),
        containers=[container],
        volumes=[
            client.V1Volume(
                name="user-pvc",
                persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(claim_name=pvc_name),
            ),
            client.V1Volume(
                name="assets-pvc",
                persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(claim_name="assets-pvc"),
            ),
        ],
        security_context=client.V1PodSecurityContext(
            run_as_non_root=True,
            fs_group=1000,
        ),
    )

    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"job": job_name}),
        spec=pod_spec,
    )

    job_spec = client.V1JobSpec(
        template=template,
        backoff_limit=0,
        ttl_seconds_after_finished=10,
    )

    return client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=job_name, namespace=namespace),
        spec=job_spec,
    )


def make_kali_ingress(subdomain: str,host: str, service_name: str, expiry_timestamp: str) -> client.V1Ingress:

    ingress = client.V1Ingress(
        metadata=client.V1ObjectMeta(
            name=f"{service_name}",
#            namespace="default",
            annotations={
                "expiry": expiry_timestamp,
            },
        ),
        spec=client.V1IngressSpec(
            tls=[
                client.V1IngressTLS(
                    hosts=[host],
                    secret_name="api-tls-cert",
                )
            ],
            rules=[
                client.V1IngressRule(
                    host=host,
                    http=client.V1HTTPIngressRuleValue(
                        paths=[
                            client.V1HTTPIngressPath(
                                path="/",
                                path_type="Prefix",
                                backend=client.V1IngressBackend(
                                    service=client.V1IngressServiceBackend(
                                        name=service_name,
                                        port=client.V1ServiceBackendPort(number=3000),
                                    )
                                ),
                            )
                        ]
                    ),
                )
            ],
        )
    )
    return ingress


def make_kali_deployment(name: str, expiry_timestamp: str) -> client.V1Deployment:
    return client.V1Deployment(
        metadata=client.V1ObjectMeta(name=name,
            labels={"app": name},
            annotations={
                "expiry": expiry_timestamp,
            }
        ),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector=client.V1LabelSelector(match_labels={"app": name}),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": name}),
                spec=client.V1PodSpec(containers=[
                    client.V1Container(
                        name="kali-linux",
                        image="lscr.io/linuxserver/kali-linux:latest",
                        ports=[client.V1ContainerPort(container_port=3000)],
                    )
                ])
            )
        )
    )

def make_kali_service(name: str, expiry_timestamp: str) -> client.V1Service:
    return client.V1Service(
        metadata=client.V1ObjectMeta(
            name=name,
            annotations={
                "expiry": expiry_timestamp,
            },
        ),
        spec=client.V1ServiceSpec(
            selector={"app": name},
            ports=[client.V1ServicePort(port=3000, target_port=3000)],
            type="ClusterIP"
        )
    )
