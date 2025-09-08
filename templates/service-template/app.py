import asyncio, json, os, subprocess
from typing import Any, Dict, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field
from nats.aio.client import Client as NATS
from nats.aio.msg import Msg

NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
DOMAIN = os.getenv("DOMAIN", "recon")
TOOL = os.getenv("TOOL", "tool_name")
INVOKE_SUBJECT = f"tool.invoke.{DOMAIN}.{TOOL}"
RESULT_SUBJECT = f"tool.result.{DOMAIN}.{TOOL}"

app = FastAPI(title=f"WRAITHS Tool Wrapper: {DOMAIN}.{TOOL}")

class InvokeEvent(BaseModel):
    subject: str
    id: Optional[str] = None
    correlation_id: Optional[str] = None
    timestamp: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    meta: Dict[str, Any] = Field(default_factory=dict)

def run_cli(parameters: Dict[str, Any]) -> Dict[str, Any]:
    cmd = parameters.get("cmd")
    if not cmd:
        raise ValueError("Missing cmd in parameters for demo template.")
    shell = isinstance(cmd, str)
    try:
        res = subprocess.run(cmd, shell=shell, capture_output=True, text=True, check=False, timeout=parameters.get("timeout", 300))
        return {
            "returncode": res.returncode,
            "stdout": res.stdout,
            "stderr": res.stderr
        }
    except subprocess.TimeoutExpired as e:
        return {"error": {"message": "timeout", "details": str(e)}}
    except Exception as e:
        return {"error": {"message": "execution_failure", "details": str(e)}}

async def handle_invoke(nc: NATS, msg: Msg):
    try:
        evt = InvokeEvent(**json.loads(msg.data.decode()))
        result = run_cli(evt.parameters)
        out = {
            "subject": RESULT_SUBJECT,
            "timestamp": evt.timestamp,
            "correlation_id": evt.id or evt.correlation_id,
            "meta": {"producer": f"{DOMAIN}.{TOOL}", "version": "1.0"}
        }
        if "error" in result:
            out["error"] = result["error"]
        else:
            out["result"] = result
        await nc.publish(RESULT_SUBJECT, json.dumps(out).encode())
    except Exception as e:
        await nc.publish(
            RESULT_SUBJECT,
            json.dumps({
                "subject": RESULT_SUBJECT,
                "timestamp": "",
                "correlation_id": None,
                "error": {"message": "unhandled_exception", "details": str(e)}
            }).encode()
        )

@app.get("/health")
def health():
    return {"status": "ok"}

async def nats_worker():
    nc = NATS()
    await nc.connect(servers=[NATS_URL])
    await nc.subscribe(INVOKE_SUBJECT, cb=lambda m: asyncio.create_task(handle_invoke(nc, m)))
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await nc.drain()

def start():
    asyncio.run(nats_worker())

if __name__ == "__main__":
    start()
