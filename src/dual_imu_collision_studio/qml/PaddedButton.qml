import QtQuick
import QtQuick.Controls

Button {
    leftPadding: DesignTokens.buttonHorizontalPadding
    rightPadding: DesignTokens.buttonHorizontalPadding
    topPadding: DesignTokens.buttonVerticalPadding
    bottomPadding: DesignTokens.buttonVerticalPadding
    implicitWidth: Math.max(DesignTokens.buttonMinimumWidth,
                            contentItem ? contentItem.implicitWidth + leftPadding + rightPadding
                                        : DesignTokens.buttonMinimumWidth)
    implicitHeight: DesignTokens.buttonHeight
}
