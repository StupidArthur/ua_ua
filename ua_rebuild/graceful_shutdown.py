"""Graceful shutdown helpers.

Centralises the SIGINT/SIGTERM/cancel logic so ua_rebuild_server.py can
focus on building the address space.
"""

from __future__ import annotations

import asyncio
import logging
import signal
from typing import Awaitable, Callable


log = logging.getLogger("ua_rebuild.graceful_shutdown")


def install_signal_handlers(
    loop: asyncio.AbstractEventLoop,
    on_stop: Callable[[], Awaitable[None]],
) -> None:
    """Install SIGINT/SIGTERM handlers that invoke ``on_stop``.

    On Windows, SIGTERM is not always delivered; we rely on SIGINT plus
    the harness / process termination.  add_signal_handler is only
    available on Unix; on Windows we use signal.signal().
    """

    async def _handler():
        log.info("[SHUTDOWN] signal received, stopping")
        try:
            await on_stop()
        finally:
            # Stop the loop so asyncio.run() can return cleanly.
            try:
                loop.stop()
            except Exception:
                pass

    try:
        loop.add_signal_handler(signal.SIGINT, lambda: asyncio.ensure_future(_handler()))
        loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.ensure_future(_handler()))
    except (NotImplementedError, RuntimeError):
        # Windows fallback
        def _win_handler(signum, frame):
            log.info("[SHUTDOWN] signal %s received", signum)
            asyncio.ensure_future(_handler())

        try:
            signal.signal(signal.SIGINT, _win_handler)
            signal.signal(signal.SIGTERM, _win_handler)
        except (ValueError, OSError):
            # signal only works in main thread
            pass


async def shutdown_simulator(simulator, timeout: float = 5.0) -> None:
    """Stop the simulator gracefully within ``timeout`` seconds."""
    if simulator is None:
        return
    simulator.stop()
    if hasattr(simulator, "wait"):
        try:
            await simulator.wait(timeout=timeout)
        except Exception:
            pass


async def cancel_background_tasks(timeout: float = 2.0) -> None:
    """Cancel pending tasks other than the current one."""
    current = asyncio.current_task()
    pending = [t for t in asyncio.all_tasks() if t is not current and not t.done()]
    for t in pending:
        t.cancel()
    if pending:
        try:
            await asyncio.wait_for(
                asyncio.gather(*pending, return_exceptions=True),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            pass