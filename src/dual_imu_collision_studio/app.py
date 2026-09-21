from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QStandardPaths, QUrl
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide6.QtQuickControls2 import QQuickStyle

from .adapters.desktop.controller import StudioController
from .adapters.desktop.diagnostics import ProcessDiagnostics
from .adapters.desktop.waveform_item import WaveformItem
from .domain.process_diagnostics.contracts import DiagnosticsPort


_WINDOWS_APP_USER_MODEL_ID = "DualIMU.CollisionStudio"


def _set_windows_taskbar_identity() -> None:
    if sys.platform != "win32":
        return
    import ctypes

    shell32 = ctypes.WinDLL("shell32", use_last_error=True)
    set_app_id = shell32.SetCurrentProcessExplicitAppUserModelID
    set_app_id.argtypes = [ctypes.c_wchar_p]
    set_app_id.restype = ctypes.c_long
    result = set_app_id(_WINDOWS_APP_USER_MODEL_ID)
    if result != 0:
        raise OSError(f"Unable to set Windows AppUserModelID (HRESULT 0x{result & 0xffffffff:08x})")


def build_engine(diagnostics: DiagnosticsPort | None = None) -> QQmlApplicationEngine:
    QQuickStyle.setStyle("Basic")
    application = QGuiApplication.instance()
    if application is not None:
        icon_path = Path(__file__).resolve().parent / "qml" / "di-icon.svg"
        application.setWindowIcon(QIcon(str(icon_path)))
    qmlRegisterType(WaveformItem, "CollisionStudio", 1, 0, "WaveformItem")
    engine = QQmlApplicationEngine()
    load_warnings: list[str] = []
    engine.warnings.connect(lambda warnings: load_warnings.extend(item.toString() for item in warnings))
    controller = StudioController(diagnostics=diagnostics)
    controller.setParent(engine)
    engine._studio_controller = controller
    engine.rootContext().setContextProperty("studio", controller)
    engine.setProperty("studioController", controller)
    qml_path = Path(__file__).resolve().parent / "qml" / "Main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    if not engine.rootObjects():
        raise RuntimeError("QML failed to load:\n" + "\n".join(load_warnings))
    return engine


def main() -> int:
    _set_windows_taskbar_identity()
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    app.setApplicationName("Dual IMU Collision Studio")
    app.setOrganizationName("Dual IMU Collision Studio")
    diagnostic_directory = Path(
        QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
    ) / "diagnostics"
    diagnostics = ProcessDiagnostics(diagnostic_directory)
    diagnostics.begin_session()
    diagnostics.install_handlers()
    clean_exit = False
    try:
        engine = build_engine(diagnostics=diagnostics)
        if not engine.rootObjects():
            return 2
        exit_code = app.exec()
        clean_exit = True
        return exit_code
    except BaseException as exc:
        diagnostics.record_python_exception(type(exc), exc, exc.__traceback__)
        raise
    finally:
        if clean_exit:
            diagnostics.mark_clean_shutdown()
        diagnostics.close()


if __name__ == "__main__":
    raise SystemExit(main())
