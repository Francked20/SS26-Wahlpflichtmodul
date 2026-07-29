import asyncio
import os
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database import ExportCipherVariant
from utils.security import require_challenge_api_key
from utils.export_cipher_pool import (
    variant_index_for_user, check_factor256, check_factor512, check_master_secret, check_flag,
)
from utils.export_cipher_sender import send_variant_to_vm

router = APIRouter()


async def _get_variant_for_user(username: str) -> ExportCipherVariant:
    variant = await ExportCipherVariant.find_one(
        ExportCipherVariant.index == variant_index_for_user(username)
    )
    if variant is None:
        raise HTTPException(status_code=503, detail="Export-cipher variant pool not generated yet")
    return variant


@router.get("/variant/{username}")
async def get_variant(username: str):
    """Tells the day-3 page which pool entry a player was assigned (a pure
    function of username) and their practice 256-bit modulus to factor with
    YAFU - unauthenticated like this service's other player-facing endpoints
    (e.g. primes.py); knowing another player's N/variant index doesn't help
    solve YOUR OWN (differently-indexed) challenge. n512 is the real RSA
    modulus - public by definition (part of the public key), so exposing it
    here (mirroring dh_export.py's p/g/Ys) is not a leak; it lets the
    Beginner page show it as decimal without requiring a manual Wireshark
    hex->decimal conversion."""
    variant = await _get_variant_for_user(username)
    return {"index": variant.index, "n256": variant.n256, "n512": variant.n512}


@router.get("/reveal_factor/{username}", dependencies=[Depends(require_challenge_api_key)])
async def get_reveal_factor(username: str):
    """Internal-only: called by core/backend's /challenges/solve after a
    correct export_factor256 answer, to reveal one factor of the real
    512-bit N."""
    variant = await _get_variant_for_user(username)
    return {"factor": variant.p512}


class CheckAnswerRequest(BaseModel):
    dynamic_check: Literal["export_factor256", "export_factor512", "export_master_secret", "export_flag"]
    username: str
    answer: str


@router.post("/check_answer", dependencies=[Depends(require_challenge_api_key)])
async def check_answer(body: CheckAnswerRequest):
    """Internal-only: called from core/backend's Challenge.check_answer()."""
    variant = await _get_variant_for_user(body.username)

    if body.dynamic_check == "export_factor256":
        correct = check_factor256(variant.p256, variant.q256, body.answer)
    elif body.dynamic_check == "export_factor512":
        correct = check_factor512(variant.q512, body.answer)
    elif body.dynamic_check == "export_master_secret":
        correct = check_master_secret(variant.master_secret_hex, body.answer)
    else:
        correct = check_flag(variant.flag, body.answer)

    return {"correct": correct}


@router.get("/vm_replay_data", dependencies=[Depends(require_challenge_api_key)])
async def get_vm_replay_data():
    """Fetched once (and cached) by CTF_Utils/export_cipher_vm_listener.py -
    the companion script run manually on the training VM. Only the
    server-role flight bytes are exposed here: that's all the VM-side
    listener ever needs to play back."""
    variants = await ExportCipherVariant.find_all().to_list()
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
    """Triggered by the player's 'gestartet' button on challenge_03.py once
    they've started their own Wireshark capture on the training VM. Sends
    THIS player's variant's client-role flights over a real TCP connection to
    EXPORT_CIPHER_VM_HOST/PORT, so what ends up in their capture is a genuine,
    self-contained conversation - unlike the old periodic sender (removed),
    this is on-demand and targeted, so no other player's variant is mixed in."""
    variant = await ExportCipherVariant.find_one(ExportCipherVariant.index == index)
    if variant is None:
        raise HTTPException(status_code=404, detail="Unknown variant index")

    host = os.getenv("EXPORT_CIPHER_VM_HOST")
    port_str = os.getenv("EXPORT_CIPHER_VM_PORT")
    if not host or not port_str:
        raise HTTPException(status_code=503, detail="Training VM not configured")

    try:
        await send_variant_to_vm(host, int(port_str), variant)
    except (OSError, asyncio.TimeoutError, ValueError) as e:
        raise HTTPException(status_code=502, detail=f"Could not reach training VM: {e}")

    return {"status": "sent"}
