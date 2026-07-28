import os
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database import DhExportVariant
from utils.security import require_challenge_api_key
from utils.dh_export_pool import (
    variant_index_for_user,
    check_factors,
    check_server_secret,
    check_master_secret,
    check_flag,
)

router = APIRouter()

#   dh_factors        -> factor p-1 (yafu)
#   dh_server_secret  -> discrete log of Ys (Pohlig-Hellman)
#   dh_master_secret  -> TLS master secret
#   dh_flag           -> flag from the application data


async def _get_variant_for_user(username: str) -> DhExportVariant:
    variant = await DhExportVariant.find_one(
        DhExportVariant.index == variant_index_for_user(username)
    )
    if variant is None:
        raise HTTPException(status_code=503, detail="Weak-DH variant pool not generated yet")
    return variant


@router.get("/variant/{username}")
async def get_variant(username: str):
    """Tells the day-4 page which pool entry a player was assigned (a pure
    function of username) and the public DH values they need to start the
    attack: p, g and the server public value Ys (all visible in their pcap's
    ServerKeyExchange anyway). Unauthenticated like this service's other
    player-facing endpoints - knowing another player's variant doesn't help
    solve YOUR OWN (differently-indexed) challenge."""
    variant = await _get_variant_for_user(username)
    return {"index": variant.index, "p": variant.p, "g": variant.g, "Ys": variant.Ys}


class CheckAnswerRequest(BaseModel):
    dynamic_check: Literal[
        "dh_factors", "dh_server_secret", "dh_master_secret", "dh_flag"
    ]
    username: str
    answer: str


@router.post("/check_answer", dependencies=[Depends(require_challenge_api_key)])
async def check_answer(body: CheckAnswerRequest):
    """Internal-only: called from core/backend's Challenge.check_answer() when a
    task on day 4 has a dynamic_check set."""
    variant = await _get_variant_for_user(body.username)

    if body.dynamic_check == "dh_factors":
        correct = check_factors(variant.factors, body.answer)
    elif body.dynamic_check == "dh_server_secret":
        correct = check_server_secret(variant.server_secret, body.answer)
    elif body.dynamic_check == "dh_master_secret":
        correct = check_master_secret(variant.master_secret_hex, body.answer)
    else:  # dh_flag
        correct = check_flag(variant.flag, body.answer)

    return {"correct": correct}


@router.get("/vm_replay_data", dependencies=[Depends(require_challenge_api_key)])
async def get_vm_replay_data():
    """Fetched once (and cached) by CTF_Utils/dh_export_vm_listener.py - the
    companion script run manually on the training VM. Only the server-role
    flight bytes are exposed here: that's all the VM-side listener needs to
    play back."""
    variants = await DhExportVariant.find_all().to_list()
    return {
        "variants": [
            {
                "index": v.index,
                "server_flight_1_hex": v.server_flight_1_hex,
                "server_flight_2_hex": v.server_flight_2_hex,
            }
            for v in sorted(variants, key=lambda v: v.index)
        ]
    }


@router.post("/{index}/start_capture")
async def start_capture(index: int):
    """Triggered by the player's 'gestartet' button on challenge_04.py once
    they've started their own Wireshark capture on the training VM. Sends THIS
    player's variant's client-role flights over a real TCP connection to
    DH_EXPORT_VM_HOST/PORT, so their capture is a genuine, self-contained
    DHE_EXPORT conversation."""
    variant = await DhExportVariant.find_one(DhExportVariant.index == index)
    if variant is None:
        raise HTTPException(status_code=404, detail="Unknown variant index")

    host = os.getenv("DH_EXPORT_VM_HOST")
    port_str = os.getenv("DH_EXPORT_VM_PORT")
    if not host or not port_str:
        raise HTTPException(status_code=503, detail="Training VM not configured")

    import asyncio
    try:
        from utils.dh_export_sender import send_variant_to_vm
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="Live VM capture not available (utils/dh_export_sender.py missing). "
                   "Use the pre-generated pcap instead.",
        )
    try:
        await send_variant_to_vm(host, int(port_str), variant)
    except (OSError, asyncio.TimeoutError, ValueError) as e:
        raise HTTPException(status_code=502, detail=f"Could not reach training VM: {e}")

    return {"status": "sent"}
