import os
import sys
import platform
from importlib.metadata import version

import reflex as rx
import reflex.environment
from pyleak.base import LeakAction

production_mode = os.getenv("SET_PRODUCTION_MODE", "false")
production_mode = (production_mode.lower() == "true")

monitor_leak = os.getenv("CTF_MONITOR_LOOP", "false")
monitor_leak = (monitor_leak.lower() == "true")

monitor_perf = os.getenv("REFLEX_PERF_MODE", rx.environment.environment.REFLEX_PERF_MODE.default)

printed_info = os.getenv("CTF_WELCOME_INFO_PRINTED")

msg = f"""
Running on: 
>> Python:      v{platform.python_version()}
>> Reflex:      v{version("reflex")}

Configuration:
>> Log Level:           {os.getenv("LOG_LEVEL")}
>> CTF Platform Mode:   {'Production' if production_mode else 'Development'}
>> Monitoring Leaks:    {monitor_leak}
>> Monitoring Perf:     {monitor_perf}

Starting CTF platform...
"""

if not printed_info:
    print(msg, file=sys.stderr)
    os.environ["CTF_WELCOME_INFO_PRINTED"] = "True"

config = rx.Config(
    app_name="website",
    frontend_port=3000,
    backend_port=8000,
    telemetry_enabled=False,
    show_built_with_reflex=False,
    enable_pyleak_monitoring=monitor_leak,
    pyleak_action=(LeakAction.WARN if monitor_leak else None),
    disable_plugins=[rx.plugins.SitemapPlugin],
    vite_allowed_hosts=[os.getenv("DOMAIN", "")],
    # state_auto_setters=None,
)
