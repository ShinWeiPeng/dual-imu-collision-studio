"""Visible Windows startup supervision without importing the application."""

from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
import subprocess
import sys
from time import monotonic, sleep
from typing import TextIO
from uuid import uuid4


def write_console(text: str) -> None:
    encoding = sys.stdout.encoding or "utf-8"
    safe_text = text.encode(encoding, errors="backslashreplace").decode(encoding)
    sys.stdout.write(safe_text)
    sys.stdout.flush()


def emit(message: str, log: TextIO) -> None:
    log.write(message + "\n")
    log.flush()
    write_console(message + "\n")


def run_stage(stage: str, command: list[str], root: Path, log: TextIO) -> int:
    started = monotonic()
    emit(f"[{datetime.now().isoformat(timespec='seconds')}] {stage}", log)
    environment = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
    try:
        with subprocess.Popen(
            command,
            cwd=root,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        ) as process:
            try:
                assert process.stdout is not None
                for line in process.stdout:
                    log.write(line)
                    log.flush()
                    write_console(line)
                code = process.wait()
            except BaseException:
                # Only terminate the process created by this stage, never unrelated Python sessions.
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                raise
    except OSError as exc:
        emit(f"[ERROR] {stage}: {exc}", log)
        code = 1
    emit(f"[Result] {stage}: exit={code}; elapsed={monotonic() - started:.3f}s", log)
    return code


def has_main_window(process_ids: set[int]) -> bool:
    """Observe the visible main window of this launch, never another instance."""
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
    user32.EnumWindows.restype = wintypes.BOOL
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.IsWindowVisible.restype = wintypes.BOOL
    user32.GetWindowThreadProcessId.argtypes = [
        wintypes.HWND,
        ctypes.POINTER(wintypes.DWORD),
    ]
    user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowTextW.restype = ctypes.c_int
    found = False

    @callback_type
    def visit(window, unused):
        nonlocal found
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(window, ctypes.byref(pid))
        if pid.value in process_ids and user32.IsWindowVisible(window):
            title = ctypes.create_unicode_buffer(256)
            user32.GetWindowTextW(window, title, len(title))
            if title.value == "Dual IMU Collision Studio":
                found = True
                return False
        return True

    if not user32.EnumWindows(visit, 0) and not found:
        error = ctypes.get_last_error()
        if error:
            raise ctypes.WinError(error)
        raise OSError(
            "Windows window enumeration is unavailable; startup readiness cannot be confirmed"
        )
    return found


def application_process_ids(pid: int) -> set[int]:
    # Imported only after the environment/dependency check. psutil is an existing
    # application dependency; the venv launcher can own a separate interpreter PID.
    import psutil

    try:
        return {pid} | {
            child.pid for child in psutil.Process(pid).children(recursive=True)
        }
    except psutil.NoSuchProcess:
        return set()


def start_application(
    python: Path, root: Path, log: TextIO, timeout: float = 120
) -> int:
    application_log = Path(log.name).with_suffix(".application.log")
    emit(f"[Info] Application log: {application_log}", log)
    emit("[Info] Starting application; waiting for its main window...", log)
    environment = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
    started = monotonic()
    with application_log.open("xb") as output:
        process = subprocess.Popen(
            [
                str(python.with_name("pythonw.exe")),
                "-u",
                "-m",
                "dual_imu_collision_studio.app",
            ],
            cwd=root,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=output,
            stderr=subprocess.STDOUT,
            close_fds=True,
            creationflags=subprocess.DETACHED_PROCESS,
        )
    # Do not use Popen as a context manager here: that would wait for application
    # exit again. The child owns independent file handles and no launcher console.
    emit(f"[Info] Application process: {process.pid}", log)
    while True:
        code = process.poll()
        if code is not None:
            emit(
                f"[ERROR] Application exited before its main window was ready: exit={code}",
                log,
            )
            with application_log.open(encoding="utf-8", errors="replace") as output:
                for line in output:
                    write_console(line)
            return code or 1
        if (
            has_main_window(application_process_ids(process.pid))
            and process.poll() is None
        ):
            emit(
                f"[Info] Main window ready after {monotonic() - started:.3f}s. Closing launcher; application runs independently.",
                log,
            )
            return 0
        if monotonic() - started >= timeout:
            emit(
                f"[ERROR] Main-window readiness not confirmed within {timeout:g}s; this does not establish a crash. Process {process.pid} remains detached. Check {application_log}",
                log,
            )
            return 1
        sleep(0.1)


def launch(root: Path) -> int:
    try:
        directory = root / "build" / "launcher-logs"
        directory.mkdir(parents=True, exist_ok=True)
        name = f"startup-{datetime.now():%Y%m%d-%H%M%S-%f}-{os.getpid()}-{uuid4().hex[:12]}.log"
        path = directory / name
        log = path.open("x", encoding="utf-8")
    except OSError as exc:
        write_console(f"[ERROR] Cannot create startup log: {exc}\n")
        return 1
    with log:
        try:
            emit(f"[Info] Startup log: {path}", log)
            emit("[Info] Checking environment...", log)
            python = root / ".venv" / "Scripts" / "python.exe"
            bootstrapped = not python.is_file()
            stages = []
            if bootstrapped:
                stages.append(
                    (
                        "Create environment",
                        [sys.executable, "-u", "-m", "venv", str(root / ".venv")],
                    )
                )
            stages.extend(
                [
                    (
                        "Check dependencies",
                        [str(python), "-u", str(root / "tools" / "check_build.py")],
                    ),
                ]
            )
            for stage, command in stages:
                code = run_stage(stage, command, root, log)
                if code:
                    emit(
                        f"[ERROR] {stage} failed: exit={code}. See startup log: {path}",
                        log,
                    )
                    return code
            if bootstrapped:
                # Dependencies were installed into the venv, not this bootstrap
                # interpreter. The child helper checks the now-current hash and
                # performs readiness observation in the prepared environment.
                code = run_stage(
                    "Continue in environment",
                    [str(python), "-u", str(root / "tools" / "launch_studio.py")],
                    root,
                    log,
                )
            else:
                code = start_application(python, root, log)
            if code:
                emit(
                    f"[ERROR] Start application failed: exit={code}. See the logs above.",
                    log,
                )
            return code
        except KeyboardInterrupt:
            emit("[ERROR] Launch interrupted: exit=130.", log)
            return 130
        except (OSError, UnicodeError) as exc:
            # A full disk or broken log must not hide the failure behind another log write.
            write_console(f"[ERROR] Launcher I/O failure: {exc}. Startup log: {path}\n")
            return 1


if __name__ == "__main__":
    raise SystemExit(launch(Path(__file__).resolve().parent.parent))
