import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "."

Dialog {
    id: wizard
    modal: true
    width: Math.min(760, parent ? parent.width - 48 : 760)
    height: Math.min(610, parent ? parent.height - 48 : 610)
    anchors.centerIn: parent
    title: "Mapping Wizard — " + studio.selectedRecordingName
    standardButtons: Dialog.NoButton
    property var recentFilterParameters: ({})
    property int step: 0
    property var columns: studio.selectedColumns
    property var previewRows: studio.selectedPreviewRows
    property bool noTime: false
    property string validationError: ""
    function timeRequest() {
        return {data_start_row:startRow.value,header_row:headerRow.value,time_column:noTime ? "" : timeColumn.currentText,
            time_unit:noTime ? "" : timeUnit.currentText,sample_rate_hz:Number(fixedRate.text)}
    }
    function invalidateFilter() { internalMap.invalidate(); externalMap.invalidate() }

    function failValidation(message) {
        validationError = String(message)
        return false
    }

    function validateCurrentStep() {
        validationError = ""
        if (step === 0 && startRow.value <= headerRow.value)
            return failValidation("Data Start Row must be after Header Row")
        if (step === 1) {
            if (noTime && (!fixedRate.acceptableInput || !Number.isFinite(Number(fixedRate.text)) || Number(fixedRate.text) <= 0))
                return failValidation("No Time Column requires a positive fixed Sample Rate")
            if (!noTime && timeColumn.currentText === "")
                return failValidation("Use a Time column requires a selected Time column")
        }
        if (step === 2 && !internalMap.validate()) return failValidation(internalMap.errorText)
        if (step === 3) {
            if (!externalMap.validate()) return failValidation(externalMap.errorText)
            let inside = internalMap.draft(), outside = externalMap.draft()
            let internalColumns = inside.raw_columns.concat(inside.filtered_columns)
            let externalColumns = outside.raw_columns.concat(outside.filtered_columns)
            if (inside.gyroscope) internalColumns = internalColumns.concat(inside.gyroscope.raw_columns, inside.gyroscope.filtered_columns)
            if (outside.gyroscope) externalColumns = externalColumns.concat(outside.gyroscope.raw_columns, outside.gyroscope.filtered_columns)
            if (externalColumns.some(function(c) { return internalColumns.indexOf(c) >= 0 }))
                return failValidation("Internal and External XYZ must use different columns")
        }
        if (step === 4) {
            if (!speed.acceptableInput || !Number.isFinite(Number(speed.text)) || Number(speed.text) <= 0)
                return failValidation("Robot Speed must be greater than zero")
            if (!offset.acceptableInput || !Number.isFinite(Number(offset.text)))
                return failValidation("Collision Offset must be a finite number")
        }
        return true
    }

    function prefillCurrentFilter() {
        if (step === 2) internalMap.prefillParameters(recentFilterParameters)
        if (step === 3) externalMap.prefillParameters(recentFilterParameters)
    }
    onStepChanged: { validationError = ""; prefillCurrentFilter() }

    onOpened: {
        validationError = ""
        startRow.value = studio.selectedDataStartRow
        headerRow.value = studio.selectedHeaderRow
        let savedTime = studio.selectedMappingTime
        if (savedTime.time_column) timeColumn.currentIndex = columns.indexOf(savedTime.time_column)
        if (savedTime.time_unit) timeUnit.currentIndex = timeUnit.model.indexOf(savedTime.time_unit)
        if (savedTime.sample_rate_hz) fixedRate.text = String(savedTime.sample_rate_hz)
        noTime = !studio.selectedHasTimeColumn
        fixedTime.checked = noTime
        timeFromColumn.checked = !noTime
        let prior = studio.selectedSignalMapping
        internalMap.load(prior.internal, studio.proposedInternalColumns)
        externalMap.load(prior.external, studio.proposedExternalColumns)
        prefillCurrentFilter()
    }

    background: Rectangle { color: DesignTokens.surface; radius: 10; border.color: DesignTokens.border }

    contentItem: ColumnLayout {
        spacing: 10
        RowLayout {
            Layout.fillWidth: true
            Repeater {
                model: ["Rows & Header", "Time Basis", "Internal IMU", "External IMU", "Review"]
                delegate: ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 5
                    Label { text: (index + 1) + ". " + modelData; color: index <= wizard.step ? DesignTokens.primary : DesignTokens.textMuted; font.pixelSize: 12; font.bold: index === wizard.step }
                    Rectangle { Layout.fillWidth: true; height: 3; radius: 2; color: index <= wizard.step ? DesignTokens.primary : DesignTokens.border }
                }
            }
        }

        StackLayout {
            id: steps
            currentIndex: wizard.step
            Layout.fillWidth: true
            Layout.fillHeight: true

            ColumnLayout {
                spacing: 12
                Label { text: "Choose where numeric data begins"; font.pixelSize: 20; font.bold: true; color: DesignTokens.text }
                Label { text: "Rows are 1-based. The surrounding preview remains read-only."; color: DesignTokens.textMuted }
                RowLayout {
                    Label { text: "Header Row"; Layout.preferredWidth: 180 }
                    SpinBox { id: headerRow; objectName: "mappingHeaderRow"; from: 1; to: 1000000; value: 1; editable: true; onValueModified: { wizard.validationError = ""; wizard.invalidateFilter() } }
                }
                RowLayout {
                    Label { text: "Data Start Row"; Layout.preferredWidth: 180 }
                    SpinBox { id: startRow; objectName: "mappingDataStartRow"; from: 1; to: 1000000; value: 2; editable: true; onValueModified: { wizard.validationError = ""; wizard.invalidateFilter() } }
                }
                Label { text: "Detected values are proposals. Confirm both rows before Finish."; color: DesignTokens.warning }
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: DesignTokens.surfaceMuted
                    radius: DesignTokens.radius
                    border.color: DesignTokens.border

                    Flickable {
                        id: rowPreview
                        anchors.fill: parent
                        anchors.margins: 1
                        clip: true
                        boundsBehavior: Flickable.StopAtBounds
                        contentWidth: previewTable.width
                        contentHeight: previewTable.height
                        ScrollBar.horizontal: ScrollBar { policy: ScrollBar.AsNeeded }
                        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

                        Column {
                            id: previewTable
                            width: Math.max(rowPreview.width, 164 + Math.max(1, columns.length) * 150)

                            Rectangle {
                                width: parent.width
                                height: 34
                                color: "#E2E8F0"
                                Row {
                                    anchors.fill: parent
                                    Rectangle { width: 64; height: parent.height; color: "transparent"; border.color: DesignTokens.border
                                        Label { anchors.centerIn: parent; text: "Row"; font.bold: true; color: DesignTokens.text }
                                    }
                                    Rectangle { width: 100; height: parent.height; color: "transparent"; border.color: DesignTokens.border
                                        Label { anchors.centerIn: parent; text: "Meaning"; font.bold: true; color: DesignTokens.text }
                                    }
                                    Repeater {
                                        model: Math.max(1, columns.length)
                                        Rectangle { width: 150; height: 34; color: "transparent"; border.color: DesignTokens.border
                                            Label { anchors.centerIn: parent; text: "Column " + (index + 1); font.bold: true; color: DesignTokens.text }
                                        }
                                    }
                                }
                            }

                            Repeater {
                                model: wizard.previewRows
                                Rectangle {
                                    required property var modelData
                                    property bool isHeader: modelData.rowNumber === headerRow.value
                                    property bool isDataStart: modelData.rowNumber === startRow.value
                                    width: previewTable.width
                                    height: 36
                                    color: isHeader ? DesignTokens.primarySoft : isDataStart ? "#E8F6F1" : DesignTokens.surface
                                    Row {
                                        anchors.fill: parent
                                        Rectangle { width: 64; height: parent.height; color: "transparent"; border.color: DesignTokens.border
                                            Label { anchors.centerIn: parent; text: modelData.rowNumber; font.bold: isHeader || isDataStart; color: DesignTokens.text }
                                        }
                                        Rectangle { width: 100; height: parent.height; color: "transparent"; border.color: DesignTokens.border
                                            Label { anchors.centerIn: parent; text: isHeader ? "Header" : isDataStart ? "Data start" : ""; font.bold: true; color: isHeader ? DesignTokens.primary : DesignTokens.success }
                                        }
                                        Repeater {
                                            model: modelData.cells
                                            Rectangle { width: 150; height: 36; color: "transparent"; border.color: DesignTokens.border
                                                Label { anchors.fill: parent; anchors.margins: 8; verticalAlignment: Text.AlignVCenter; text: modelData; color: DesignTokens.text; elide: Text.ElideRight }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    Label {
                        anchors.centerIn: parent
                        visible: wizard.previewRows.length === 0
                        text: "No source rows available"
                        color: DesignTokens.textMuted
                    }
                }
            }

            ColumnLayout {
                spacing: 12
                Label { text: "Confirm the time basis"; font.pixelSize: 20; font.bold: true; color: DesignTokens.text }
                ButtonGroup { id: timeBasisGroup }
                RadioButton { id: timeFromColumn; text: "Use a Time column"; checked: true; ButtonGroup.group: timeBasisGroup; onCheckedChanged: if (checked) { wizard.noTime = false; wizard.validationError = ""; wizard.invalidateFilter() } }
                ComboBox { id: timeColumn; Layout.fillWidth: true; model: columns; enabled: !wizard.noTime; onActivated: { wizard.validationError = ""; if (wizard.step < 2) wizard.invalidateFilter() } }
                RowLayout {
                    enabled: !wizard.noTime
                    Label { text: "Time Unit" }
                    ComboBox { id: timeUnit; model: ["s", "ms", "µs"]; currentIndex: 1; onActivated: { wizard.validationError = ""; if (wizard.step < 2) wizard.invalidateFilter() } }
                    Label { text: "Must be explicitly confirmed"; color: DesignTokens.warning }
                }
                RadioButton { id: fixedTime; text: "No Time Column"; ButtonGroup.group: timeBasisGroup; onCheckedChanged: if (checked) { wizard.noTime = true; wizard.validationError = ""; wizard.invalidateFilter() } }
                RowLayout {
                    enabled: wizard.noTime
                    Label { text: "Fixed Sample Rate" }
                    TextField { id: fixedRate; objectName: "mappingFixedRate"; text: "1000"; validator: DoubleValidator { bottom: 0.000001 } onTextEdited: { wizard.validationError = ""; if (wizard.step < 2) wizard.invalidateFilter() } }
                    Label { text: "Hz" }
                }
                Label { text: "The source values are never resampled or repaired silently."; color: DesignTokens.textMuted }
            }

            ImuSignalMapping {
                id:internalMap; sensor:"internal"; columns:wizard.columns; timeRequest:wizard.timeRequest()
                onErrorTextChanged: if (wizard.step === 2) wizard.validationError = ""
                onFilterParametersAdopted: parameters => { wizard.recentFilterParameters = parameters }
            }
            ImuSignalMapping {
                id:externalMap; sensor:"external"; columns:wizard.columns; timeRequest:wizard.timeRequest()
                onErrorTextChanged: if (wizard.step === 3) wizard.validationError = ""
                onFilterParametersAdopted: parameters => { wizard.recentFilterParameters = parameters }
            }

            ColumnLayout {
                spacing: 12
                Label { text: "Review mapping and test conditions"; font.pixelSize: 20; font.bold: true; color: DesignTokens.text }
                Rectangle { Layout.fillWidth: true; height: 156; radius: DesignTokens.radius; color: DesignTokens.primarySoft; border.color: "#B8D2F6"
                    GridLayout { anchors.fill: parent; anchors.margins: 16; columns: 2
                        Label { text: "Recording"; color: DesignTokens.textMuted }
                        Label { text: studio.selectedRecordingName; Layout.fillWidth: true; elide: Text.ElideMiddle; font.bold: true }
                        Label { text: "Rows"; color: DesignTokens.textMuted } Label { text: "Header row " + headerRow.value + " · data starts at row " + startRow.value }
                        Label { text: "Time"; color: DesignTokens.textMuted } Label { text: wizard.noTime ? fixedRate.text + " Hz (synthesized)" : timeColumn.currentText + " in " + timeUnit.currentText }
                        Label { text: "IMU columns"; color: DesignTokens.textMuted } Label { text: "Internal: " + internalMap.draft().mode + " · External: " + externalMap.draft().mode }
                    }
                }
                RowLayout {
                    Label { text: "Robot Speed"; Layout.preferredWidth: 150 }
                    TextField { id: speed; objectName: "mappingRobotSpeed"; text: "500"; validator: DoubleValidator { bottom: 0.000001 } onTextEdited: { wizard.validationError = ""; if (wizard.step < 2) wizard.invalidateFilter() } }
                    Label { text: "mm/s" }
                }
                RowLayout {
                    Label { text: "Collision Offset"; Layout.preferredWidth: 150 }
                    TextField { id: offset; objectName: "mappingCollisionOffset"; text: "5"; validator: DoubleValidator {} onTextEdited: { wizard.validationError = ""; if (wizard.step < 2) wizard.invalidateFilter() } }
                    Label { text: "mm" }
                }
                Label { text: "Offset records the commanded Robot coordinate displacement; collision truth still comes only from waveform interval annotation."; color: DesignTokens.textMuted; wrapMode: Text.Wrap; Layout.fillWidth: true }
            }
        }

        Label {
            objectName: "mappingValidationError"
            Layout.fillWidth: true
            visible: wizard.validationError.length > 0
            text: wizard.validationError
            color: DesignTokens.warning
            wrapMode: Text.Wrap
            font.bold: true
        }
        Rectangle { Layout.fillWidth: true; height: 1; color: DesignTokens.border }
        RowLayout {
            Layout.fillWidth: true
            PaddedButton { text: "Cancel"; onClicked: wizard.reject() }
            Item { Layout.fillWidth: true }
            PaddedButton { text: "Back"; enabled: wizard.step > 0; onClicked: wizard.step-- }
            PaddedButton {
                objectName: "mappingWizardNextButton"
                text: wizard.step === 4 ? "Finish" : "Next"
                highlighted: true
                onClicked: {
                    if (!wizard.validateCurrentStep()) return
                    if (wizard.step < 4) { wizard.step++; return }
                    try {
                        var request = wizard.timeRequest()
                        request.robot_speed = Number(speed.text)
                        request.collision_offset = Number(offset.text)
                        request.signals = {internal:internalMap.draft(),external:externalMap.draft()}
                        var ok = studio.confirmSignalMapping(request)
                        if (ok) {
                            wizard.validationError = ""
                            wizard.accept()
                        } else {
                            wizard.failValidation(studio.statusMessage || "Unable to confirm mapping")
                        }
                    } catch (error) {
                        wizard.failValidation(error && error.message ? error.message : String(error))
                    }
                }
            }
        }
    }

}
