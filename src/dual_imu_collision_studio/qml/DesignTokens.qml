pragma Singleton
import QtQuick

QtObject {
    readonly property color canvas: "#F4F7FB"
    readonly property color surface: "#FFFFFF"
    readonly property color surfaceMuted: "#EDF2F7"
    readonly property color border: "#D6DEE8"
    readonly property color text: "#172033"
    readonly property color textMuted: "#617087"
    readonly property color primary: "#1769E0"
    readonly property color primarySoft: "#E8F1FF"
    readonly property color success: "#168567"
    readonly property color warning: "#B86B08"
    readonly property color danger: "#C43B45"
    readonly property color cycle: "#51677F"
    readonly property color pick: "#7357C7"
    readonly property color put: "#168567"
    readonly property color collision: "#D14343"
    readonly property color ignore: "#7A8797"
    readonly property int radius: 8
    readonly property int spacing: 12
    readonly property int buttonHorizontalPadding: 16
    readonly property int buttonVerticalPadding: 8
    readonly property int buttonMinimumWidth: 96
    readonly property int buttonHeight: 36
}
