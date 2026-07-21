"""ServerProcessHarness: spawn the ua_rebuild_server.py subprocess with
isolated temp dir, wait for the ready file, then tear it down.

This is the only supported way to launch the server in tests.
"""

from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


class ServerProcessHarness:
    def __init__(
        self,
        repo_root: Path,
        *,
        scope: str = "all-sov",
        enable_simulation: bool = True,
        startup_timeout: float = 120.0,
    ) -> None:
        self.repo_root = repo_root
        self.scope = scope
        self.enable_simulation = enable_simulation
        self.startup_timeout = startup_timeout

        self.port = self._find_free_port()

        temp_dir = Path(
            tempfile.mkdtemp(prefix=f"ua_test_{self.port}_")
        )

        self.temp_dir = temp_dir
        self.ready_file = temp_dir / "ready.json"
        self.log_file = temp_dir / "server.log"
        self.report_file = temp_dir / "startup_report.json"

        self.process: subprocess.Popen | None = None
        self._log_handle = None

    @property
    def endpoint(self) -> str:
        return (
            f"opc.tcp://127.0.0.1:{self.port}/ua-rebuild/"
        )

    @staticmethod
    def _find_free_port() -> int:
        with socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        ) as sock:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])

    def start(self) -> None:
        if self.process is not None:
            raise RuntimeError("process already started")

        self.assert_port_released()

        command = [
            sys.executable,
            str(self.repo_root / "ua_rebuild_server.py"),
            "--model",
            str(self.repo_root / "real_server_export_v2.json"),
            "--scope",
            self.scope,
            "--host",
            "127.0.0.1",
            "--port",
            str(self.port),
            "--profile",
            "debug",
            "--report",
            str(self.report_file),
            "--ready-file",
            str(self.ready_file),
        ]

        if self.enable_simulation:
            command.extend(
                [
                    "--enable-simulation",
                    "--tick-ms",
                    "100",
                    "--snapshot-interval-ms",
                    "300",
                    "--seed",
                    "12345",
                ]
            )

        self._log_handle = self.log_file.open(
            "w",
            encoding="utf-8",
        )

        kwargs: dict[str, Any] = {
            "cwd": str(self.repo_root),
            "stdout": self._log_handle,
            "stderr": subprocess.STDOUT,
        }

        if os.name == "nt":
            kwargs["creationflags"] = (
                subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            kwargs["start_new_session"] = True

        self.process = subprocess.Popen(
            command,
            **kwargs,
        )

    def wait_ready(
        self,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        if self.process is None:
            raise RuntimeError("process not started")

        deadline = time.monotonic() + (
            timeout
            if timeout is not None
            else self.startup_timeout
        )

        last_error: Exception | None = None

        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise RuntimeError(
                    "server exited before ready\n"
                    + self.read_log_tail()
                )

            if self.ready_file.exists():
                try:
                    payload = json.loads(
                        self.ready_file.read_text(
                            encoding="utf-8"
                        )
                    )

                    if payload.get("status") == "failed":
                        raise RuntimeError(
                            "server reported failed:\n"
                            + json.dumps(
                                payload,
                                ensure_ascii=False,
                                indent=2,
                            )
                            + "\n"
                            + self.read_log_tail()
                        )

                    if payload.get("status") == "ready":
                        self._wait_tcp(timeout=10.0)
                        return payload

                except json.JSONDecodeError as exc:
                    last_error = exc

            time.sleep(0.1)

        raise TimeoutError(
            f"server ready timeout after "
            f"{timeout or self.startup_timeout}s; "
            f"last_error={last_error}\n"
            + self.read_log_tail()
        )

    def _wait_tcp(self, timeout: float) -> None:
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            with socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM,
            ) as sock:
                sock.settimeout(0.5)
                try:
                    sock.connect(
                        ("127.0.0.1", self.port)
                    )
                    return
                except OSError:
                    pass

            time.sleep(0.1)

        raise TimeoutError(
            f"TCP endpoint did not become ready: "
            f"{self.endpoint}\n"
            + self.read_log_tail()
        )

    def stop(self) -> None:
        process = self.process

        if process is None:
            return

        if process.poll() is None:
            self._request_graceful_stop(process)

            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._force_stop(process)

        if process.poll() is None:
            raise RuntimeError(
                "server process could not be terminated\n"
                + self.read_log_tail()
            )

        if self._log_handle is not None:
            self._log_handle.close()
            self._log_handle = None

        self.process = None

        deadline = time.monotonic() + 10.0

        while time.monotonic() < deadline:
            if self._port_is_free():
                break
            time.sleep(0.1)

        self.assert_port_released()

    def _request_graceful_stop(
        self,
        process: subprocess.Popen,
    ) -> None:
        try:
            if os.name == "nt":
                process.send_signal(
                    signal.CTRL_BREAK_EVENT
                )
            else:
                os.killpg(
                    os.getpgid(process.pid),
                    signal.SIGTERM,
                )
        except Exception:
            try:
                process.terminate()
            except Exception:
                pass

    def _force_stop(
        self,
        process: subprocess.Popen,
    ) -> None:
        if os.name == "nt":
            subprocess.run(
                [
                    "taskkill",
                    "/PID",
                    str(process.pid),
                    "/T",
                    "/F",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        else:
            try:
                os.killpg(
                    os.getpgid(process.pid),
                    signal.SIGKILL,
                )
            except Exception:
                process.kill()

        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass

    def _port_is_free(self) -> bool:
        with socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        ) as sock:
            try:
                sock.bind(("127.0.0.1", self.port))
                return True
            except OSError:
                return False

    def assert_port_released(self) -> None:
        if not self._port_is_free():
            raise AssertionError(
                f"port {self.port} is still occupied\n"
                + self.read_log_tail()
            )

    def read_log_tail(
        self,
        lines: int = 200,
    ) -> str:
        if not self.log_file.exists():
            return "<server log unavailable>"

        content = self.log_file.read_text(
            encoding="utf-8",
            errors="replace",
        ).splitlines()

        return "\n".join(content[-lines:])

    def __enter__(self) -> "ServerProcessHarness":
        self.start()
        self.wait_ready()
        return self

    def __exit__(
        self,
        exc_type,
        exc,
        traceback,
    ) -> None:
        try:
            self.stop()
        except Exception:
            if exc is None:
                raise