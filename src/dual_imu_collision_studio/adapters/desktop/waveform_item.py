from __future__ import annotations

from PySide6.QtCore import QLineF, QPointF, Property, QRectF, Signal
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath, QPen
from PySide6.QtQuick import QQuickItem, QSGNode, QSGSimpleTextureNode, QSGTexture
from shiboken6 import Shiboken


class WaveformItem(QQuickItem):
    channelsChanged = Signal()
    projectionChanged = Signal()
    viewportChanged = Signal()

    def __init__(self, parent: QQuickItem | None = None) -> None:
        super().__init__(parent)
        self._channels: list[list[float]] = []
        self._projection: dict[str, object] | None = None
        self._viewport_start = 0.0
        self._viewport_end = 1.0
        self.setFlag(QQuickItem.ItemHasContents, True)

    def channels(self) -> list[list[float]]:
        return self._channels

    def setChannels(self, value: list[list[float]]) -> None:
        self._channels = [list(map(float, channel)) for channel in value[:3]]
        self.channelsChanged.emit()
        self.update()

    channelsProperty = Property("QVariantList", channels, setChannels, notify=channelsChanged)

    def projection(self) -> dict[str, object]:
        return self._projection or {}

    def setProjection(self, value: dict[str, object]) -> None:
        positions = [float(item) for item in value.get("positions", [])]
        minimums = [list(map(float, channel)) for channel in value.get("minimums", [])[:3]]
        maximums = [list(map(float, channel)) for channel in value.get("maximums", [])[:3]]
        means = [list(map(float, channel)) for channel in value.get("means", [])[:3]]
        mode = str(value.get("mode", "raw"))
        if mode not in {"raw", "envelope"}:
            mode = "raw"
        if len(minimums) != 3 or len(maximums) != 3 or len(means) != 3 or any(
            len(channel) != len(positions) for channel in minimums + maximums + means
        ):
            positions, minimums, maximums, means = [], [[], [], []], [[], [], []], [[], [], []]
        self._projection = {
            "mode": mode,
            "positions": positions,
            "minimums": minimums,
            "maximums": maximums,
            "means": means,
        }
        self.projectionChanged.emit()
        self.update()

    projectionProperty = Property("QVariantMap", projection, setProjection, notify=projectionChanged)

    def viewportStart(self) -> float:
        return self._viewport_start

    def setViewportStart(self, value: float) -> None:
        bounded = max(0.0, min(float(value), self._viewport_end - 1e-6))
        if bounded == self._viewport_start:
            return
        self._viewport_start = bounded
        self.viewportChanged.emit()
        self.update()

    viewportStartProperty = Property(float, viewportStart, setViewportStart, notify=viewportChanged)

    def viewportEnd(self) -> float:
        return self._viewport_end

    def setViewportEnd(self, value: float) -> None:
        bounded = min(1.0, max(float(value), self._viewport_start + 1e-6))
        if bounded == self._viewport_end:
            return
        self._viewport_end = bounded
        self.viewportChanged.emit()
        self.update()

    viewportEndProperty = Property(float, viewportEnd, setViewportEnd, notify=viewportChanged)

    def geometryChange(self, new_geometry: QRectF, old_geometry: QRectF) -> None:
        super().geometryChange(new_geometry, old_geometry)
        if new_geometry.size() != old_geometry.size():
            self.update()

    def renderImage(self, width: int, height: int) -> QImage:
        width = max(1, width)
        height = max(1, height)
        image = QImage(width, height, QImage.Format_ARGB32_Premultiplied)
        image.fill(QColor(0, 0, 0, 0))
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing, True)
        colors = (QColor("#1769E0"), QColor("#D14343"), QColor("#168567"))
        if self._projection is not None:
            positions = self._projection["positions"]
            minimums = self._projection["minimums"]
            maximums = self._projection["maximums"]
            means = self._projection["means"]
            mode = self._projection["mode"]
            for lows, highs, averages, color in zip(minimums, maximums, means, colors):
                if not positions:
                    continue
                low, high = min(lows), max(highs)
                span = high - low or 1.0
                painter.setPen(QPen(color, 1.25))
                if mode == "envelope":
                    lines = []
                    for position, minimum, maximum in zip(positions, lows, highs):
                        x = (width - 1) * position
                        lines.append(
                            QLineF(
                                x,
                                height * (0.88 - 0.76 * (minimum - low) / span),
                                x,
                                height * (0.88 - 0.76 * (maximum - low) / span),
                            )
                        )
                    painter.drawLines(lines)
                    if len(positions) == 1:
                        painter.drawPoint(
                            QPointF(
                                (width - 1) * positions[0],
                                height * (0.88 - 0.76 * (averages[0] - low) / span),
                            )
                        )
                    else:
                        mean_points = [
                            QPointF(
                                (width - 1) * position,
                                height * (0.88 - 0.76 * (average - low) / span),
                            )
                            for position, average in zip(positions, averages)
                        ]
                        painter.drawLines(
                            [
                                QLineF(start, end)
                                for start, end in zip(mean_points, mean_points[1:])
                            ]
                        )
                elif len(positions) == 1:
                    painter.drawPoint(
                        QPointF(
                            (width - 1) * positions[0],
                            height * (0.88 - 0.76 * (lows[0] - low) / span),
                        )
                    )
                elif len(positions) >= 2:
                    path = QPainterPath()
                    for index, (position, value) in enumerate(zip(positions, lows)):
                        point = QPointF(
                            (width - 1) * position,
                            height * (0.88 - 0.76 * (value - low) / span),
                        )
                        path.moveTo(point) if index == 0 else path.lineTo(point)
                    painter.drawPath(path)
            painter.end()
            return image
        for source_channel, color in zip(self._channels, colors):
            source_count = len(source_channel)
            start_index = min(source_count, max(0, int(self._viewport_start * source_count)))
            end_index = min(source_count, max(start_index + 1, int(round(self._viewport_end * source_count))))
            channel = source_channel[start_index:end_index]
            if len(channel) < 2:
                continue
            low, high = min(channel), max(channel)
            span = high - low or 1.0
            denominator = max(1, len(channel) - 1)
            path = QPainterPath()
            for index, value in enumerate(channel):
                point = QPointF(
                    width * index / denominator,
                    height * (0.88 - 0.76 * (value - low) / span),
                )
                if index == 0:
                    path.moveTo(point)
                else:
                    path.lineTo(point)
            painter.setPen(QPen(color, 1.25))
            painter.drawPath(path)
        painter.end()
        return image

    def updatePaintNode(self, old_node: QSGNode | None, update_data: object) -> QSGNode:
        del update_data
        node = old_node if isinstance(old_node, QSGSimpleTextureNode) else QSGSimpleTextureNode()
        window = self.window()
        if window is None:
            return node
        image = self.renderImage(int(round(self.width())), int(round(self.height())))
        texture = window.createTextureFromImage(image)
        old_texture = node.texture()
        node.setOwnsTexture(False)
        node.setTexture(texture)
        node.setOwnsTexture(True)
        node.setFiltering(QSGTexture.Linear)
        node.setRect(QRectF(0, 0, self.width(), self.height()))
        Shiboken.invalidate(texture)
        if old_texture is not None and Shiboken.isValid(old_texture):
            Shiboken.delete(old_texture)
        return node
