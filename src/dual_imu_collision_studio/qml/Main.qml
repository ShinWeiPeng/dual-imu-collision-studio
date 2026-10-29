import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import QtCore
import CollisionStudio 1.0
import "."

ApplicationWindow {
    id: window
    objectName: "mainWindow"
    visible: true
    width: 1366
    height: 820
    minimumWidth: 1180
    minimumHeight: 720
    title: "Dual IMU Collision Studio"
    color: DesignTokens.canvas
    property alias mappingWizardVisible: mappingWizard.visible
    property string pendingProjectTransition: ""
    property url pendingProjectUrl
    property bool allowProjectClose: false
    property var jsonExportQueue: []
    property var jsonExportCurrent: ({})
    property url jsonExportTarget
    property string jsonExportError: ""

    function nextJsonExport() {
        if (!jsonExportQueue.length) return
        let rows = jsonExportQueue.slice()
        jsonExportCurrent = rows.shift()
        jsonExportQueue = rows
        jsonExportError = ""
        jsonModelName.text = jsonExportCurrent.modelName
        jsonNameDialog.open()
    }
    function saveJsonExport(replace) {
        let result = studio.exportJsonModel(jsonExportCurrent.kernelId,
            jsonExportCurrent.modelName, jsonExportTarget, replace)
        if (result === "started") return
        if (result === "exists") jsonReplaceDialog.open()
        else if (result === "saved") nextJsonExport()
        else {
            jsonExportError = studio.statusMessage
            jsonNameDialog.open()
        }
    }

    Connections {
        target: studio
        function onJsonExportFinished(result) {
            if (result === "exists") jsonReplaceDialog.open()
            else if (result === "saved") window.nextJsonExport()
            else {
                window.jsonExportError = studio.statusMessage
                jsonNameDialog.open()
            }
        }
    }

    Dialog {
        id: jsonNameDialog
        objectName: "jsonModelNameDialog"
        title: "Export JSON model — " + (window.jsonExportCurrent.kernelId || "")
        modal: true
        anchors.centerIn: parent
        width: Math.min(540, window.width - 40)
        standardButtons: Dialog.NoButton
        onRejected: window.jsonExportQueue = []
        ColumnLayout {
            anchors.fill: parent
            Label { text: "Model display name"; font.bold: true }
            TextField { id: jsonModelName; objectName: "jsonModelName"; Layout.fillWidth: true; selectByMouse: true }
            Label { text: (window.jsonExportCurrent.sampleRate || "") + " Hz · " + (window.jsonExportCurrent.numericType || "") + " · Internal/External XYZ in g"; Layout.fillWidth: true; wrapMode: Text.Wrap }
            Label { text: "Choose the JSON filename in the next dialog. Changing it will not change the model display name."; Layout.fillWidth: true; wrapMode: Text.Wrap }
            Label { text: window.jsonExportError; visible: text.length > 0; color: DesignTokens.warning; Layout.fillWidth: true; wrapMode: Text.Wrap }
            RowLayout {
                Item { Layout.fillWidth: true }
                PaddedButton { text: "Cancel"; onClicked: jsonNameDialog.reject() }
                PaddedButton {
                    text: "Choose file…"; highlighted: true
                    onClicked: {
                        let error = studio.validateJsonModelName(window.jsonExportCurrent.kernelId, jsonModelName.text)
                        if (error.length) { window.jsonExportError = error; return }
                        let row = Object.assign({}, window.jsonExportCurrent)
                        let fallback = row.modelName
                        row.modelName = jsonModelName.text
                        window.jsonExportCurrent = row
                        let filename = /[<>:"/\\|?*]/.test(row.modelName) ? fallback : row.modelName
                        jsonSaveDialog.selectedFile = jsonSaveDialog.currentFolder.toString().replace(/\/$/, "") + "/" + encodeURIComponent(filename) + ".json"
                        jsonNameDialog.close()
                        jsonSaveDialog.open()
                    }
                }
            }
        }
    }
    FileDialog {
        id: jsonSaveDialog
        objectName: "jsonModelSaveDialog"
        title: "Save JSON model"
        fileMode: FileDialog.SaveFile
        options: FileDialog.DontConfirmOverwrite
        currentFolder: StandardPaths.standardLocations(StandardPaths.DocumentsLocation)[0]
        nameFilters: ["JSON model (*.json)"]
        defaultSuffix: "json"
        onAccepted: { window.jsonExportTarget = selectedFile; window.saveJsonExport(false) }
        onRejected: window.jsonExportQueue = []
    }
    Dialog {
        id: jsonReplaceDialog
        objectName: "jsonModelReplaceDialog"
        title: "Replace existing JSON file?"
        modal: true
        anchors.centerIn: parent
        width: Math.min(540, window.width - 40)
        standardButtons: Dialog.Yes | Dialog.No
        Label { anchors.fill: parent; text: window.jsonExportTarget.toString(); wrapMode: Text.WrapAnywhere }
        onAccepted: window.saveJsonExport(true)
        onRejected: window.jsonExportQueue = []
    }

    function finishProjectTransition() {
        let action = pendingProjectTransition
        let url = pendingProjectUrl
        pendingProjectTransition = ""
        if (action === "open")
            studio.openProject(url)
        else if (action === "close") {
            allowProjectClose = true
            window.close()
        }
    }

    function requestProjectTransition(action, url) {
        pendingProjectTransition = action
        pendingProjectUrl = url || ""
        if (studio.projectDirty)
            unsavedProjectDialog.open()
        else
            finishProjectTransition()
    }

    function saveBeforeProjectTransition() {
        if (studio.projectPath === "") {
            saveProjectDialog.continueTransition = true
            saveProjectDialog.open()
        } else if (studio.saveProject()) {
            finishProjectTransition()
        }
    }

    function openMappingWizardForRecording(index) {
        if (index < 0)
            return
        importPage.captureRecordingsViewport()
        studio.selectRecording(index)
        mappingWizard.step = 0
        mappingWizard.open()
    }

    header: ToolBar {
        height: 58
        background: Rectangle { color: DesignTokens.surface; border.color: DesignTokens.border }
        RowLayout { anchors.fill: parent; anchors.leftMargin: 20; anchors.rightMargin: 20
            Image {
                objectName: "applicationBrandIcon"
                source: "di-icon.svg"
                sourceSize.width: 64; sourceSize.height: 64
                Layout.preferredWidth: 30; Layout.preferredHeight: 30
                fillMode: Image.PreserveAspectFit
            }
            ColumnLayout { spacing: 0
                Label { text: "Dual IMU Collision Studio"; font.bold: true; font.pixelSize: 16; color: DesignTokens.text }
                Label { text: studio.projectName + (studio.projectDirty ? " · Unsaved changes" : " · Saved"); font.pixelSize: 11; color: studio.projectDirty ? DesignTokens.warning : DesignTokens.textMuted }
            }
            Item { Layout.fillWidth: true }
            PaddedButton { objectName: "openProjectButton"; text: "Open Project"; onClicked: openProjectDialog.open() }
            PaddedButton { objectName: "saveProjectButton"; text: "Save"; enabled: studio.projectDirty; onClicked: studio.projectPath === "" ? saveProjectDialog.open() : studio.saveProject() }
            PaddedButton { objectName: "saveProjectAsButton"; text: "Save As"; onClicked: saveProjectDialog.open() }
            Rectangle { width: stateLabel.implicitWidth + 22; height: 30; radius: 15; color: studio.runState === "Complete" ? "#E4F4EE" : DesignTokens.surfaceMuted
                Label { id: stateLabel; anchors.centerIn: parent; text: studio.runState; color: studio.runState === "Complete" ? DesignTokens.success : DesignTokens.textMuted; font.bold: true; font.pixelSize: 12 }
            }
        }
    }

    footer: Rectangle {
        height: studio.diagnosticNotice.length > 0 ? 58 : 32; color: DesignTokens.surface; border.color: DesignTokens.border
        ColumnLayout { anchors.fill: parent; anchors.leftMargin: 16; anchors.rightMargin: 16; spacing: 0
            RowLayout { Layout.fillWidth: true; Layout.preferredHeight: 30
                Label { text: studio.statusMessage; color: DesignTokens.textMuted; elide: Text.ElideRight; Layout.fillWidth: true }
                Label { text: studio.numericType ? "Target: " + studio.numericType : "Target numeric type not selected"; color: studio.numericType ? DesignTokens.textMuted : DesignTokens.warning }
            }
            Label {
                objectName: "diagnosticNotice"
                visible: studio.diagnosticNotice.length > 0
                text: studio.diagnosticNotice + " · Log: " + studio.diagnosticLogPath
                color: DesignTokens.warning
                font.pixelSize: 11
                elide: Text.ElideMiddle
                Layout.fillWidth: true
                Layout.preferredHeight: visible ? 26 : 0
            }
        }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0
        Rectangle {
            Layout.preferredWidth: 238
            Layout.fillHeight: true
            color: "#F9FBFD"
            border.color: DesignTokens.border
            ColumnLayout { anchors.fill: parent; anchors.margins: 12; spacing: 8
                Label { text: "WORKFLOW"; color: DesignTokens.textMuted; font.pixelSize: 11; font.bold: true; leftPadding: 8; topPadding: 8; bottomPadding: 4 }
                ListView {
                    id: stageNavigator
                    objectName: "stageNavigator"
                    Layout.fillWidth: true; Layout.fillHeight: true
                    spacing: 5
                    model: studio.stages
                    delegate: Rectangle {
                        required property var modelData
                        required property int index
                        width: ListView.view.width; height: 58; radius: DesignTokens.radius
                        enabled: modelData.enabled
                        opacity: enabled ? 1.0 : 0.48
                        color: studio.selectedStage === index ? DesignTokens.primarySoft : navMouse.containsMouse ? DesignTokens.surfaceMuted : "transparent"
                        border.color: studio.selectedStage === index ? "#B8D2F6" : "transparent"
                        RowLayout { anchors.fill: parent; anchors.margins: 10; spacing: 10
                            Rectangle { width: 28; height: 28; radius: 14; color: modelData.state === "complete" ? DesignTokens.success : studio.selectedStage === index ? DesignTokens.primary : DesignTokens.surfaceMuted
                                Label { anchors.centerIn: parent; text: modelData.state === "complete" ? "✓" : modelData.number; color: modelData.state === "pending" ? DesignTokens.textMuted : "white"; font.bold: true }
                            }
                            Label { text: modelData.name; Layout.fillWidth: true; wrapMode: Text.Wrap; color: DesignTokens.text; font.bold: studio.selectedStage === index }
                        }
                        MouseArea { id: navMouse; anchors.fill: parent; enabled: modelData.enabled; hoverEnabled: true; onClicked: studio.selectStage(index) }
                    }
                }
                Rectangle { Layout.fillWidth: true; height: 70; radius: DesignTokens.radius; color: DesignTokens.surfaceMuted
                    Column { anchors.fill: parent; anchors.margins: 10; spacing: 4
                        Label { text: "Session limits"; font.bold: true; font.pixelSize: 11; color: DesignTokens.text }
                        Label { text: "50 recordings · 10M rows total"; font.pixelSize: 11; color: DesignTokens.textMuted }
                        Label { text: studio.projectPath === "" ? "Project not saved" : studio.projectName; font.pixelSize: 11; color: DesignTokens.textMuted; elide: Text.ElideMiddle; width: parent.width }
                    }
                }
            }
        }

        StackLayout {
            id: workspaceStack
            objectName: "workspaceStack"
            currentIndex: studio.selectedStage
            Layout.fillWidth: true
            Layout.fillHeight: true
            ImportPage { id: importPage }
            AnnotationPage {}
            TrainPage {}
            QualificationPage {}
            ExportPage {}
        }
    }

    FileDialog {
        id: importDialog
        objectName: "importDialog"
        title: "Import data"
        fileMode: FileDialog.OpenFiles
        nameFilters: ["Recording files (*.csv *.xlsx)"]
        onAccepted: {
            let firstImportedIndex = -1
            for (let index = 0; index < selectedFiles.length; ++index) {
                let importedIndex = studio.importFile(selectedFiles[index])
                if (firstImportedIndex < 0 && importedIndex >= 0)
                    firstImportedIndex = importedIndex
            }
            if (firstImportedIndex >= 0)
                Qt.callLater(window.openMappingWizardForRecording, firstImportedIndex)
        }
    }
    FileDialog {
        id: openProjectDialog
        title: "Open project"
        fileMode: FileDialog.OpenFile
        nameFilters: ["Dual IMU Collision Studio project (*.dicsproj)"]
        onAccepted: window.requestProjectTransition("open", selectedFile)
    }
    FileDialog {
        id: saveProjectDialog
        property bool continueTransition: false
        title: "Save project"
        fileMode: FileDialog.SaveFile
        nameFilters: ["Dual IMU Collision Studio project (*.dicsproj)"]
        defaultSuffix: "dicsproj"
        onAccepted: {
            let saved = studio.saveProjectAs(selectedFile)
            if (saved && continueTransition)
                window.finishProjectTransition()
            continueTransition = false
        }
        onRejected: continueTransition = false
    }
    FileDialog {
        id: relinkProjectFileDialog
        title: "Locate " + studio.projectRelinkSource
        fileMode: FileDialog.OpenFile
        nameFilters: ["Recording files (*.csv *.xlsx)"]
        onAccepted: studio.relinkProjectFile(selectedFile)
    }
    FolderDialog {
        id: relinkProjectFolderDialog
        title: "Locate folder containing moved recordings"
        onAccepted: studio.relinkProjectFolder(selectedFolder)
    }
    Dialog {
        id: relinkProjectDialog
        title: "Project source is missing"
        width: 560
        modal: true
        closePolicy: Popup.NoAutoClose
        visible: studio.projectRelinkRequired
        anchors.centerIn: parent
        contentItem: Label {
            text: "The saved source " + studio.projectRelinkSource + " is unavailable. Select the exact unchanged file or a folder containing moved sources."
            wrapMode: Text.Wrap
            color: DesignTokens.text
            leftPadding: 18; rightPadding: 18; topPadding: 10; bottomPadding: 10
        }
        footer: DialogButtonBox {
            PaddedButton { text: "Cancel"; onClicked: studio.cancelProjectRelink() }
            PaddedButton { text: "Locate Folder"; onClicked: relinkProjectFolderDialog.open() }
            PaddedButton { text: "Locate File"; highlighted: true; onClicked: relinkProjectFileDialog.open() }
        }
    }
    Dialog {
        id: unsavedProjectDialog
        objectName: "unsavedProjectDialog"
        title: "Unsaved project changes"
        width: 500
        modal: true
        closePolicy: Popup.NoAutoClose
        anchors.centerIn: parent
        contentItem: Label {
            text: "Save changes before continuing?"
            color: DesignTokens.text
            leftPadding: 18; rightPadding: 18; topPadding: 10; bottomPadding: 10
        }
        footer: DialogButtonBox {
            PaddedButton { text: "Cancel"; DialogButtonBox.buttonRole: DialogButtonBox.RejectRole; onClicked: { window.pendingProjectTransition = ""; unsavedProjectDialog.close() } }
            PaddedButton { text: "Discard"; onClicked: { unsavedProjectDialog.close(); window.finishProjectTransition() } }
            PaddedButton { text: "Save"; highlighted: true; DialogButtonBox.buttonRole: DialogButtonBox.AcceptRole; onClicked: { unsavedProjectDialog.close(); window.saveBeforeProjectTransition() } }
        }
    }
    FolderDialog { id: exportFolderDialog; title: "Choose Profile header folder"; onAccepted: studio.prepareSelectedExport(selectedFolder.toString()) }
    Dialog {
        id: conflictDialog
        title: "Profile header already exists"
        width: 480
        modal: true
        closePolicy: Popup.NoAutoClose
        visible: studio.exportConflictName.length > 0
        anchors.centerIn: parent
        contentItem: Label {
            text: studio.exportConflictName + " already exists. Replace this file or skip it?"
            wrapMode: Text.Wrap
            color: DesignTokens.text
            leftPadding: 18
            rightPadding: 18
        }
        footer: DialogButtonBox {
            PaddedButton { text: "Skip"; DialogButtonBox.buttonRole: DialogButtonBox.RejectRole; onClicked: studio.resolveExportConflict(false) }
            PaddedButton { text: "Replace"; highlighted: true; DialogButtonBox.buttonRole: DialogButtonBox.AcceptRole; onClicked: studio.resolveExportConflict(true) }
        }
    }
    MappingWizard {
        id: mappingWizard
        objectName: "mappingWizard"
        onAccepted: importPage.restoreRecordingsViewport()
    }

    onClosing: close => {
        if (studio.jsonExportActive || studio.qualificationValidationActive) {
            close.accepted = false
            return
        }
        if (studio.projectDirty && !window.allowProjectClose) {
            close.accepted = false
            window.requestProjectTransition("close", "")
        }
    }

    component SectionTitle: ColumnLayout {
        property string heading
        property string supporting
        spacing: 3
        Label { text: heading; font.pixelSize: 25; font.bold: true; color: DesignTokens.text }
        Label { text: supporting; color: DesignTokens.textMuted; wrapMode: Text.Wrap; Layout.fillWidth: true }
    }
    component Card: Rectangle { color: DesignTokens.surface; radius: DesignTokens.radius; border.color: DesignTokens.border }
    component Tag: Rectangle {
        property string label
        property color tagColor: DesignTokens.primarySoft
        implicitWidth: tagText.implicitWidth + 18; implicitHeight: 26; radius: 13; color: tagColor
        Label { id: tagText; anchors.centerIn: parent; text: label; font.pixelSize: 11; font.bold: true; color: DesignTokens.text }
    }

    component ImportPage: Item {
        property real recordingsViewportY: 0

        function captureRecordingsViewport() {
            recordingsViewportY = recordingsList.contentY
        }

        function restoreRecordingsViewport() {
            const capturedY = recordingsViewportY
            Qt.callLater(function() {
                const minimumY = recordingsList.originY
                const maximumY = Math.max(
                    minimumY,
                    minimumY + recordingsList.contentHeight - recordingsList.height
                )
                recordingsList.contentY = Math.max(minimumY, Math.min(capturedY, maximumY))
            })
        }

        ColumnLayout { anchors.fill: parent; anchors.margins: 20; spacing: 14
            RowLayout { Layout.fillWidth: true
                SectionTitle { heading: "Import & Map"; supporting: "Inventory each CSV or XLSX worksheet, then confirm its rows, time basis, six IMU axes, Robot Speed, and Collision Offset."; Layout.fillWidth: true }
                PaddedButton { objectName: "importDataButton"; text: "Import Data"; onClicked: importDialog.open() }
            }
            RowLayout { Layout.fillWidth: true; Layout.fillHeight: true; spacing: 12
                Card { Layout.preferredWidth: 280; Layout.fillHeight: true
                    ColumnLayout { anchors.fill: parent; anchors.margins: 12; spacing: 8
                        RowLayout {
                            Layout.fillWidth: true
                            Label { text: "Recordings"; font.bold: true; font.pixelSize: 15 }
                            Item { Layout.fillWidth: true }
                            Tag { label: studio.recordings.length.toString() }
                        }
                        ListView { id: recordingsList; objectName: "recordingsList"; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 7; model: studio.recordings
                            delegate: Rectangle { required property var modelData; required property int index; width: ListView.view.width; height: 124; radius: 7; color: studio.selectedRecording === index ? DesignTokens.primarySoft : DesignTokens.surfaceMuted; border.color: studio.selectedRecording === index ? "#AFCDF6" : "transparent"
                                Column { anchors.fill: parent; anchors.margins: 10; spacing: 3
                                    Label { width: parent.width; text: modelData.name; elide: Text.ElideMiddle; font.bold: true; color: DesignTokens.text }
                                    Label { text: modelData.rows + " rows  ·  " + modelData.sampleRate; color: DesignTokens.textMuted; font.pixelSize: 11 }
                                    Label { text: modelData.mappingStatus + "  ·  " + modelData.validation; color: modelData.mappingStatus === "Confirmed" ? DesignTokens.success : DesignTokens.warning; font.pixelSize: 11 }
                                    Label { text: modelData.rateStatus; color: modelData.rateStatus === "Rate mismatch" ? DesignTokens.danger : modelData.rateStatus === "Rate compatible" ? DesignTokens.success : DesignTokens.textMuted; font.pixelSize: 11 }
                                    Label { text: modelData.duplicateStatus; color: modelData.duplicateStatus === "Review duplicate" ? DesignTokens.warning : DesignTokens.textMuted; font.pixelSize: 11 }
                                    Label { text: modelData.condition; color: DesignTokens.textMuted; font.pixelSize: 11 }
                                }
                                MouseArea { anchors.fill: parent; onClicked: studio.selectRecording(index) }
                            }
                            Label { anchors.centerIn: parent; visible: studio.recordings.length === 0; text: "No data imported yet\nCSV and XLSX are supported"; horizontalAlignment: Text.AlignHCenter; color: DesignTokens.textMuted }
                        }
                    }
                }
                Card { Layout.fillWidth: true; Layout.fillHeight: true
                    ColumnLayout { anchors.fill: parent; anchors.margins: 12
                        RowLayout {
                            Layout.fillWidth: true
                            Label { text: "Preview"; font.bold: true; font.pixelSize: 15 }
                            Item { Layout.fillWidth: true }
                            Tag { label: studio.selectedSingleImuConfiguration.sensor === "external" ? "External IMU · X / Y / Z" : "Internal IMU · X / Y / Z" }
                        }
                        Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; color: "#FBFCFE"; border.color: DesignTokens.border; radius: 6
                            WaveformItem { anchors.fill: parent; anchors.margins: 8; channelsProperty: studio.selectedSingleImuConfiguration.sensor === "external" ? studio.externalWaveformChannels : studio.waveformChannels }
                        }
                    }
                }
                Card { Layout.preferredWidth: 300; Layout.fillHeight: true
                    ColumnLayout { anchors.fill: parent; anchors.margins: 14; spacing: 12
                        Label { text: "Recording Configuration"; font.bold: true; font.pixelSize: 15 }
                        Label { text: "Every source is confirmed independently. Mapping is never copied from another file."; wrapMode: Text.Wrap; Layout.fillWidth: true; color: DesignTokens.textMuted }
                        Rectangle { Layout.fillWidth: true; height: 1; color: DesignTokens.border }
                        Label { text: "Test Conditions"; font.bold: true }
                        Label { text: studio.selectedRecording >= 0 ? studio.recordings[studio.selectedRecording].condition : "Select a recording"; color: DesignTokens.textMuted; wrapMode: Text.Wrap; Layout.fillWidth: true }
                        Label {
                            visible: studio.selectedRecording >= 0 && studio.recordings[studio.selectedRecording].importWarnings.length > 0
                            text: visible ? "Import warning: " + studio.recordings[studio.selectedRecording].importWarnings.join("; ") : ""
                            color: DesignTokens.warning
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                            font.pixelSize: 11
                        }
                        PaddedButton { text: "Open Mapping Wizard"; Layout.fillWidth: true; enabled: studio.selectedRecording >= 0; highlighted: true; onClicked: window.openMappingWizardForRecording(studio.selectedRecording) }
                        PaddedButton { text: "Remove Recording"; Layout.fillWidth: true; enabled: studio.selectedRecording >= 0; onClicked: studio.removeRecording(studio.selectedRecording) }
                        Label { visible: studio.duplicateConditionSummary.length > 0; text: studio.duplicateConditionSummary; color: DesignTokens.warning; wrapMode: Text.Wrap; Layout.fillWidth: true; font.pixelSize: 11 }
                        PaddedButton { text: "Confirm Intentional Repeated Acquisition"; Layout.fillWidth: true; visible: studio.duplicateConditionSummary.length > 0; onClicked: studio.confirmIntentionalDuplicates() }
                        Item { Layout.fillHeight: true }
                        Label { text: "No A/B/C file role. Collision truth is assigned later with waveform intervals."; color: DesignTokens.textMuted; wrapMode: Text.Wrap; Layout.fillWidth: true; font.pixelSize: 11 }
                    }
                }
            }
        }
    }

    component AnnotationPage: Item {
        id: annotationPage
        objectName: "annotationPage"
        property string activeTool: "Select / Edit"
        property real startX: 0
        property real endX: 0
        property real pendingIgnoreStart: 0
        property real pendingIgnoreEnd: 0
        property real viewportStart: 0.0
        property real viewportEnd: 1.0
        property bool draggingGroup: false
        property real dragDelta: 0
        property int draggedAnnotationIndex: -1
        readonly property real viewportSpan: viewportEnd - viewportStart
        readonly property real minimumViewportSpan: 0.002
        function bounded(value, low, high) {
            return Math.max(low, Math.min(high, value))
        }
        function globalFraction(localFraction) {
            return viewportStart + bounded(localFraction, 0, 1) * viewportSpan
        }
        function zoomAt(localFraction, wheelSteps) {
            let anchor = bounded(localFraction, 0, 1)
            let requestedSpan = viewportSpan * Math.pow(0.8, wheelSteps)
            let newSpan = bounded(requestedSpan, minimumViewportSpan, 1.0)
            let anchorGlobal = viewportStart + anchor * viewportSpan
            let newStart = anchorGlobal - anchor * newSpan
            newStart = bounded(newStart, 0, 1 - newSpan)
            viewportStart = newStart
            viewportEnd = newStart + newSpan
        }
        function panByFraction(deltaFraction) {
            let newStart = bounded(viewportStart + deltaFraction, 0, 1 - viewportSpan)
            viewportEnd = newStart + viewportSpan
            viewportStart = newStart
        }
        function resetViewport() {
            viewportStart = 0.0
            viewportEnd = 1.0
        }
        function commitDrag(startFraction, endFraction) {
            if (activeTool === "Ignore") {
                pendingIgnoreStart = startFraction
                pendingIgnoreEnd = endFraction
                ignoreReason.text = ""
                ignoreDialog.open()
            } else {
                studio.createAnnotation(activeTool, startFraction, endFraction, "")
            }
        }
        function finishGroupDrag(index, additive, moved, finalDelta) {
            draggingGroup = false
            dragDelta = 0
            draggedAnnotationIndex = -1
            studio.commitAnnotationGesture(index, additive, moved, finalDelta)
        }
        Shortcut { sequences: [StandardKey.Undo]; onActivated: studio.undoAnnotation() }
        Shortcut { sequences: [StandardKey.Redo]; onActivated: studio.redoAnnotation() }
        Shortcut { sequence: "Delete"; onActivated: studio.deleteSelectedAnnotation() }
        Shortcut { sequence: "Escape"; onActivated: activeTool = "Select / Edit" }
        Dialog {
            id: ignoreDialog
            modal: true
            anchors.centerIn: parent
            width: 440
            closePolicy: Popup.NoAutoClose
            background: Rectangle {
                color: DesignTokens.surface
                border.color: DesignTokens.border
                border.width: 1
                radius: DesignTokens.radius
            }
            header: Label {
                text: "Ignore reason"
                color: DesignTokens.text
                font.pixelSize: 18
                font.bold: true
                leftPadding: 18
                rightPadding: 18
                topPadding: 16
                bottomPadding: 8
            }
            ColumnLayout {
                width: parent.width
                spacing: 10
                Label { text: "Explain why this waveform range must be excluded."; wrapMode: Text.Wrap; Layout.fillWidth: true }
                TextField { id: ignoreReason; Layout.fillWidth: true; placeholderText: "Required reason" }
            }
            footer: DialogButtonBox {
                PaddedButton {
                    text: "Cancel"
                    DialogButtonBox.buttonRole: DialogButtonBox.RejectRole
                    onClicked: ignoreDialog.reject()
                }
                PaddedButton {
                    text: "Confirm"
                    highlighted: true
                    enabled: ignoreReason.text.trim().length > 0
                    DialogButtonBox.buttonRole: DialogButtonBox.AcceptRole
                    onClicked: {
                        if (studio.createAnnotation("Ignore", pendingIgnoreStart, pendingIgnoreEnd, ignoreReason.text))
                            ignoreDialog.accept()
                    }
                }
            }
        }
        ColumnLayout { anchors.fill: parent; anchors.margins: 18; spacing: 10
            RowLayout { Layout.fillWidth: true
                SectionTitle { heading: "Annotate & Classify"; supporting: "Choose a label and drag on either waveform to create an interval. Mouse wheel zooms; Select / Edit drag pans. Normal Robot Motion is derived and read-only."; Layout.fillWidth: true }
                Tag { objectName: "annotationRecordingTag"; label: "Recording: " + studio.selectedRecordingName; tagColor: DesignTokens.surfaceMuted }
                ComboBox {
                    id: annotationRecordingSelector
                    objectName: "annotationRecordingSelector"
                    Layout.preferredWidth: 300
                    model: studio.annotationRecordingOptions
                    textRole: "label"
                    valueRole: "index"
                    currentIndex: studio.selectedRecording
                    onActivated: studio.selectRecording(currentIndex)
                    Accessible.name: "Select annotation recording"
                }
                PaddedButton {
                    objectName: "useReferenceButton"
                    text: studio.activeTemplateSummary === "No active reference for this speed"
                          ? "Use as Reference" : "Replace Reference…"
                    enabled: studio.canUseSelectedCycleAsReference
                    onClicked: studio.useSelectedCycleAsReference()
                }
                PaddedButton {
                    objectName: "confirmAllAnnotationsButton"
                    text: "Confirm All Annotation Sets"
                    highlighted: studio.canConfirmAnnotations && !studio.annotationsReady
                    onClicked: studio.confirmAnnotations()
                }
            }
            RowLayout { Layout.fillWidth: true
                Label { text: "Reference: " + studio.activeTemplateSummary; color: DesignTokens.textMuted; font.pixelSize: 11; Layout.fillWidth: true; elide: Text.ElideRight }
                Label { visible: studio.annotationBlockerMessage.length > 0; text: studio.annotationBlockerMessage; color: DesignTokens.warning; font.pixelSize: 11; wrapMode: Text.Wrap; Layout.maximumWidth: 620 }
            }
            Label {
                objectName: "annotationProgressSummary"
                text: studio.annotationProgressText
                color: DesignTokens.textMuted
                font.pixelSize: 11
                Layout.fillWidth: true
                elide: Text.ElideRight
            }
            Label {
                visible: studio.activeTemplateDetails.length > 0
                text: studio.activeTemplateDetails
                color: DesignTokens.textMuted
                font.pixelSize: 11
                Layout.fillWidth: true
                elide: Text.ElideRight
            }
            Card { Layout.fillWidth: true; height: 54
                RowLayout { anchors.fill: parent; anchors.margins: 8; spacing: 6
                    Repeater { model: ["Select / Edit", "Cycle", "Pick", "Put", "Fork Collision", "Ignore"]
                        PaddedButton { required property string modelData; text: modelData; checkable: true; checked: activeTool === modelData; onClicked: activeTool = modelData }
                    }
                    Rectangle { width: 1; Layout.fillHeight: true; color: DesignTokens.border }
                    PaddedButton { text: "Undo"; enabled: studio.canUndoAnnotation; onClicked: studio.undoAnnotation() }
                    PaddedButton { text: "Redo"; enabled: studio.canRedoAnnotation; onClicked: studio.redoAnnotation() }
                    PaddedButton { text: "Delete"; onClicked: studio.deleteSelectedAnnotation() }
                    PaddedButton { text: "Reset View"; onClicked: annotationPage.resetViewport() }
                    Item { Layout.fillWidth: true }
                }
            }
            Card { Layout.fillWidth: true; Layout.fillHeight: true
                ColumnLayout { anchors.fill: parent; anchors.margins: 10; spacing: 6
                    WavePanel {
                        visible: studio.selectedSingleImuConfiguration.sensor !== "external"
                        titleText: "Internal IMU"
                        waveformObjectName: "annotationInternalWaveform"
                        interactionObjectName: "annotationInternalInteraction"
                        intervalObjectPrefix: "annotationInternalInterval"
                        sourceName: "internal_imu"
                        activeTool: annotationPage.activeTool
                        viewportStart: annotationPage.viewportStart
                        viewportEnd: annotationPage.viewportEnd
                        intervals: studio.annotationIntervals
                        groupDragging: annotationPage.draggingGroup
                        groupDragDelta: annotationPage.dragDelta
                        groupDragIndex: annotationPage.draggedAnnotationIndex
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        onCreateRequested: (startFraction, endFraction) => annotationPage.commitDrag(startFraction, endFraction)
                        onZoomRequested: (localFraction, wheelSteps) => annotationPage.zoomAt(localFraction, wheelSteps)
                        onPanRequested: deltaFraction => annotationPage.panByFraction(deltaFraction)
                        onGroupDragStateRequested: (dragging, delta, index) => {
                            annotationPage.draggingGroup = dragging
                            annotationPage.dragDelta = delta
                            annotationPage.draggedAnnotationIndex = index
                        }
                        onGroupDragFinished: (index, additive, moved, delta) => annotationPage.finishGroupDrag(index, additive, moved, delta)
                    }
                    WavePanel {
                        visible: studio.selectedSingleImuConfiguration.sensor !== "internal"
                        titleText: "External IMU"
                        waveformObjectName: "annotationExternalWaveform"
                        interactionObjectName: "annotationExternalInteraction"
                        intervalObjectPrefix: "annotationExternalInterval"
                        sourceName: "external_imu"
                        activeTool: annotationPage.activeTool
                        viewportStart: annotationPage.viewportStart
                        viewportEnd: annotationPage.viewportEnd
                        intervals: studio.annotationIntervals
                        groupDragging: annotationPage.draggingGroup
                        groupDragDelta: annotationPage.dragDelta
                        groupDragIndex: annotationPage.draggedAnnotationIndex
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        onCreateRequested: (startFraction, endFraction) => annotationPage.commitDrag(startFraction, endFraction)
                        onZoomRequested: (localFraction, wheelSteps) => annotationPage.zoomAt(localFraction, wheelSteps)
                        onPanRequested: deltaFraction => annotationPage.panByFraction(deltaFraction)
                        onGroupDragStateRequested: (dragging, delta, index) => {
                            annotationPage.draggingGroup = dragging
                            annotationPage.dragDelta = delta
                            annotationPage.draggedAnnotationIndex = index
                        }
                        onGroupDragFinished: (index, additive, moved, delta) => annotationPage.finishGroupDrag(index, additive, moved, delta)
                    }
                    Rectangle { id: lanes; objectName: "annotationLanes"; Layout.fillWidth: true; Layout.preferredHeight: 184; color: "#FBFCFE"; border.color: DesignTokens.border; radius: 6
                        property real trackLeft: 170
                        property real trackWidth: Math.max(1, width - 190)
                        Column { anchors.fill: parent; anchors.margins: 8; spacing: 4
                            Repeater { model: [["Cycle", DesignTokens.cycle], ["Pick", DesignTokens.pick], ["Put", DesignTokens.put], ["Fork Collision", DesignTokens.collision], ["Ignore", DesignTokens.ignore], ["Normal Robot Motion · read-only", "#A9C5B8"]]
                                Rectangle { required property var modelData; width: parent.width; height: 24; color: "#F1F4F8"; radius: 3
                                    Label { x: 7; anchors.verticalCenter: parent.verticalCenter; text: modelData[0]; font.pixelSize: 10; color: DesignTokens.textMuted }
                                }
                            }
                        }
                        MouseArea {
                            anchors.left: parent.left; anchors.leftMargin: lanes.trackLeft
                            anchors.right: parent.right; anchors.rightMargin: 20
                            anchors.top: parent.top; anchors.bottom: parent.bottom
                            enabled: activeTool !== "Select / Edit"
                            cursorShape: Qt.CrossCursor
                            onPressed: mouse => startX = mouse.x
                            onReleased: mouse => {
                                endX = mouse.x
                                commitDrag(globalFraction(startX / width), globalFraction(endX / width))
                            }
                        }
                        Repeater {
                            objectName: "annotationLaneIntervals"
                            model: studio.annotationIntervals
                            delegate: Rectangle {
                                id: annotationBar
                                objectName: "annotationLaneInterval"
                                required property var modelData
                                required property int index
                                property bool gestureSelected: modelData.selected || index === annotationPage.draggedAnnotationIndex
                                property real visualStart: modelData.startFraction + (annotationPage.draggingGroup && gestureSelected ? annotationPage.dragDelta : 0)
                                property real visualEnd: modelData.endFraction + (annotationPage.draggingGroup && gestureSelected ? annotationPage.dragDelta : 0)
                                property real clippedStart: Math.max(visualStart, annotationPage.viewportStart)
                                property real clippedEnd: Math.min(visualEnd, annotationPage.viewportEnd)
                                visible: visualEnd > annotationPage.viewportStart && visualStart < annotationPage.viewportEnd
                                x: lanes.trackLeft + (clippedStart - annotationPage.viewportStart) / annotationPage.viewportSpan * lanes.trackWidth
                                y: 12 + modelData.lane * 28
                                width: Math.max(5, (clippedEnd - clippedStart) / annotationPage.viewportSpan * lanes.trackWidth)
                                height: 16
                                radius: 3
                                color: [DesignTokens.cycle, DesignTokens.pick, DesignTokens.put, DesignTokens.collision, DesignTokens.ignore][modelData.lane]
                                opacity: modelData.provisional ? 0.48 : 0.82
                                border.width: modelData.selected ? 2 : 0
                                border.color: DesignTokens.text
                                ToolTip.visible: intervalMouse.containsMouse
                                ToolTip.text: (modelData.anchor ? "Anchor · " : modelData.provisional ? "Suggested · " : "") + modelData.kind + (modelData.reason ? " · " + modelData.reason : "")
                                MouseArea {
                                    id: intervalMouse
                                    objectName: "annotationLaneIntervalMouse"
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    enabled: activeTool === "Select / Edit"
                                    property real pressLaneX: 0
                                    property real originalStart: 0
                                    property real originalEnd: 0
                                    property bool wasSelected: false
                                    property bool additiveSelection: false
                                    property bool moved: false
                                    onPressed: mouse => {
                                        wasSelected = modelData.selected
                                        additiveSelection = (mouse.modifiers & Qt.ControlModifier) !== 0
                                        moved = false
                                        annotationPage.draggingGroup = true
                                        annotationPage.dragDelta = 0
                                        annotationPage.draggedAnnotationIndex = index
                                        pressLaneX = mapToItem(lanes, mouse.x, mouse.y).x
                                        originalStart = annotationBar.visualStart
                                        originalEnd = annotationBar.visualEnd
                                    }
                                    onPositionChanged: mouse => { if (pressed) {
                                        let delta = (mapToItem(lanes, mouse.x, mouse.y).x - pressLaneX) / lanes.trackWidth * annotationPage.viewportSpan
                                        annotationPage.dragDelta = delta
                                        moved = moved || Math.abs(delta) > 1e-6
                                    } }
                                    onReleased: {
                                        let finalDelta = annotationPage.dragDelta
                                        annotationPage.finishGroupDrag(index, additiveSelection, moved, finalDelta)
                                    }
                                    onCanceled: {
                                        annotationPage.draggingGroup = false
                                        annotationPage.dragDelta = 0
                                        annotationPage.draggedAnnotationIndex = -1
                                    }
                                }
                                Rectangle {
                                    width: 6; height: parent.height + 6; anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter
                                    color: "white"; border.color: DesignTokens.textMuted; visible: modelData.selected
                                    MouseArea {
                                        anchors.fill: parent; cursorShape: Qt.SizeHorCursor
                                        property real pressLaneX: 0; property real originalStart: 0
                                        onPressed: mouse => { pressLaneX = mapToItem(lanes, mouse.x, mouse.y).x; originalStart = annotationBar.visualStart }
                                        onPositionChanged: mouse => { if (pressed) annotationBar.visualStart = Math.max(0, Math.min(annotationBar.visualEnd - annotationPage.viewportSpan / lanes.trackWidth, originalStart + (mapToItem(lanes, mouse.x, mouse.y).x - pressLaneX) / lanes.trackWidth * annotationPage.viewportSpan)) }
                                        onReleased: studio.updateAnnotation(index, annotationBar.visualStart, annotationBar.visualEnd)
                                    }
                                }
                                Rectangle {
                                    width: 6; height: parent.height + 6; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter
                                    color: "white"; border.color: DesignTokens.textMuted; visible: modelData.selected
                                    MouseArea {
                                        anchors.fill: parent; cursorShape: Qt.SizeHorCursor
                                        property real pressLaneX: 0; property real originalEnd: 0
                                        onPressed: mouse => { pressLaneX = mapToItem(lanes, mouse.x, mouse.y).x; originalEnd = annotationBar.visualEnd }
                                        onPositionChanged: mouse => { if (pressed) annotationBar.visualEnd = Math.min(1, Math.max(annotationBar.visualStart + annotationPage.viewportSpan / lanes.trackWidth, originalEnd + (mapToItem(lanes, mouse.x, mouse.y).x - pressLaneX) / lanes.trackWidth * annotationPage.viewportSpan)) }
                                        onReleased: studio.updateAnnotation(index, annotationBar.visualStart, annotationBar.visualEnd)
                                    }
                                }
                            }
                        }
                        Repeater {
                            model: studio.derivedNormalIntervals
                            delegate: Rectangle {
                                required property var modelData
                                visible: modelData.endFraction > annotationPage.viewportStart && modelData.startFraction < annotationPage.viewportEnd
                                x: lanes.trackLeft + (modelData.startFraction - annotationPage.viewportStart) / annotationPage.viewportSpan * lanes.trackWidth
                                y: 12 + 5 * 28
                                width: Math.max(3, (modelData.endFraction - modelData.startFraction) / annotationPage.viewportSpan * lanes.trackWidth)
                                height: 12; radius: 2; color: "#A9C5B8"; opacity: 0.55
                            }
                        }
                    }
                }
            }
        }
    }

    component WavePanel: Rectangle {
        id: wavePanel
        objectName: interactionObjectName + "Panel"
        property string titleText
        property string waveformObjectName
        property string interactionObjectName
        property string intervalObjectPrefix
        property string sourceName
        property var signalKinds: {
            let value = studio.selectedSignalMapping[sourceName === "internal_imu" ? "internal" : "external"] || ({})
            let names = value.accelerometer_enabled !== false ? ["Accelerometer"] : []
            if (value.gyroscope) names.push("Gyroscope")
            return names
        }
        property var intervals
        property string activeTool: "Select / Edit"
        property real viewportStart: 0.0
        property real viewportEnd: 1.0
        property bool groupDragging: false
        property real groupDragDelta: 0
        property int groupDragIndex: -1
        readonly property real viewportSpan: Math.max(0.000001, viewportEnd - viewportStart)
        signal createRequested(real startFraction, real endFraction)
        signal zoomRequested(real localFraction, real wheelSteps)
        signal panRequested(real deltaFraction)
        signal groupDragStateRequested(bool dragging, real delta, int index)
        signal groupDragFinished(int index, bool additive, bool moved, real delta)
        function localFraction(globalValue) {
            return (globalValue - viewportStart) / viewportSpan
        }
        function intervalColor(lane) {
            let colors = [DesignTokens.cycle, DesignTokens.pick, DesignTokens.put, DesignTokens.collision, DesignTokens.ignore]
            return lane >= 0 && lane < colors.length ? colors[lane] : DesignTokens.primary
        }
        function refreshWaveformProjection() {
            waveformItem.projectionProperty = studio.waveformViewport(
                sourceName + ":" + (signalSelector.currentText === "Gyroscope" ? "gyroscope" : "accelerometer"),
                viewportStart,
                viewportEnd,
                Math.max(1, Math.floor(plotArea.width)))
        }
        onSourceNameChanged: Qt.callLater(refreshWaveformProjection)
        onViewportStartChanged: Qt.callLater(refreshWaveformProjection)
        onViewportEndChanged: Qt.callLater(refreshWaveformProjection)
        Component.onCompleted: refreshWaveformProjection()
        Connections {
            target: studio
            function onStateChanged() { Qt.callLater(wavePanel.refreshWaveformProjection) }
        }
        color: "#FBFCFE"; border.color: DesignTokens.border; radius: 6
        ComboBox { id:signalSelector; objectName:waveformObjectName + "SignalGroup"; x:125; y:1; width:145; height:26; model:wavePanel.signalKinds; onCurrentIndexChanged:Qt.callLater(wavePanel.refreshWaveformProjection) }
        Label { x: 10; y: 7; text: titleText; font.bold: true; font.pixelSize: 11; color: DesignTokens.text }
        Row { anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 7; spacing: 8
            Label { text: "X"; color: "#1769E0"; font.bold: true } Label { text: "Y"; color: "#D14343"; font.bold: true } Label { text: "Z"; color: "#168567"; font.bold: true }
        }
        Item {
            id: plotArea
            anchors.fill: parent
            anchors.margins: 8
            anchors.topMargin: 28
            clip: true
            onWidthChanged: Qt.callLater(wavePanel.refreshWaveformProjection)
            WaveformItem {
                id: waveformItem
                objectName: waveformObjectName
                anchors.fill: parent
            }
            Repeater {
                objectName: "interpolationMarkers"
                model: studio.interpolationMarkers
                delegate: Rectangle {
                    objectName: "interpolationMarker"
                    required property var modelData
                    x: wavePanel.localFraction(modelData.startFraction) * plotArea.width
                    width: Math.max(2, (modelData.endFraction - modelData.startFraction) / wavePanel.viewportSpan * plotArea.width)
                    height: plotArea.height
                    color: "#24D99319"
                    border.color: "#B87510"
                    Accessible.name: "Interpolated " + modelData.count + " samples"
                    Label {
                        text: "Interpolated " + modelData.count
                        color: "#865509"
                        font.pixelSize: 10
                    }
                }
            }
            MouseArea {
                id: waveformInteraction
                objectName: interactionObjectName
                anchors.fill: parent
                z: 10
                acceptedButtons: Qt.LeftButton | Qt.MiddleButton
                hoverEnabled: true
                preventStealing: true
                cursorShape: creating ? Qt.CrossCursor : pressed ? Qt.ClosedHandCursor : activeTool === "Select / Edit" ? Qt.OpenHandCursor : Qt.CrossCursor
                property real pressX: 0
                property real lastX: 0
                property real dragX: 0
                property bool creating: false
                onPressed: mouse => {
                    pressX = mouse.x
                    lastX = mouse.x
                    dragX = mouse.x
                    creating = activeTool !== "Select / Edit" && mouse.button === Qt.LeftButton
                }
                onPositionChanged: mouse => {
                    if (!pressed)
                        return
                    if (creating) {
                        dragX = Math.max(0, Math.min(width, mouse.x))
                    } else {
                        let pixelDelta = mouse.x - lastX
                        wavePanel.panRequested(-pixelDelta / Math.max(1, width) * wavePanel.viewportSpan)
                        lastX = mouse.x
                    }
                }
                onReleased: mouse => {
                    if (creating && Math.abs(dragX - pressX) >= 2) {
                        let localStart = Math.max(0, Math.min(1, pressX / Math.max(1, width)))
                        let localEnd = Math.max(0, Math.min(1, dragX / Math.max(1, width)))
                        wavePanel.createRequested(
                            wavePanel.viewportStart + localStart * wavePanel.viewportSpan,
                            wavePanel.viewportStart + localEnd * wavePanel.viewportSpan
                        )
                    }
                    creating = false
                }
                onCanceled: creating = false
                onWheel: wheel => {
                    wavePanel.zoomRequested(
                        Math.max(0, Math.min(1, wheel.x / Math.max(1, width))),
                        wheel.angleDelta.y / 120.0
                    )
                    wheel.accepted = true
                }
            }
            Repeater {
                objectName: wavePanel.interactionObjectName + "Intervals"
                model: wavePanel.intervals
                delegate: Rectangle {
                    id: waveformInterval
                    required property var modelData
                    required property int index
                    property bool gestureSelected: modelData.selected || index === wavePanel.groupDragIndex
                    property real visualStart: modelData.startFraction + (wavePanel.groupDragging && gestureSelected ? wavePanel.groupDragDelta : 0)
                    property real visualEnd: modelData.endFraction + (wavePanel.groupDragging && gestureSelected ? wavePanel.groupDragDelta : 0)
                    property real clippedStart: Math.max(visualStart, wavePanel.viewportStart)
                    property real clippedEnd: Math.min(visualEnd, wavePanel.viewportEnd)
                    property color intervalBaseColor: wavePanel.intervalColor(modelData.lane)
                    objectName: wavePanel.intervalObjectPrefix + modelData.index
                    // Keep the mouse grab while endpoint bindings settle during a move.
                    visible: (wavePanel.groupDragging && gestureSelected) || clippedEnd > clippedStart
                    x: wavePanel.localFraction(clippedStart) * plotArea.width
                    width: Math.max(5, wavePanel.localFraction(clippedEnd) * plotArea.width - x)
                    height: plotArea.height
                    z: 20
                    color: Qt.rgba(intervalBaseColor.r, intervalBaseColor.g, intervalBaseColor.b, modelData.provisional ? 0.08 : modelData.selected ? 0.24 : 0.14)
                    border.width: modelData.selected ? 2 : 1
                    border.color: intervalBaseColor
                    Rectangle {
                        anchors.left: parent.left
                        anchors.top: parent.top
                        anchors.margins: 4
                        width: intervalLabel.implicitWidth + 10
                        height: intervalLabel.implicitHeight + 5
                        radius: 3
                        color: intervalBaseColor
                        visible: waveformInterval.width >= width + 8
                        Label {
                            id: intervalLabel
                            anchors.centerIn: parent
                            text: (modelData.anchor ? "Anchor · " : modelData.provisional ? "Suggested · " : "") + modelData.kind
                            color: "white"
                            font.bold: true
                            font.pixelSize: 10
                        }
                    }
                    MouseArea {
                        id: waveformIntervalMouse
                        anchors.fill: parent
                        z: 1
                        enabled: wavePanel.activeTool === "Select / Edit"
                        hoverEnabled: true
                        preventStealing: true
                        cursorShape: pressed ? Qt.ClosedHandCursor : Qt.OpenHandCursor
                        property real pressPlotX: 0
                        property real originalStart: 0
                        property real originalEnd: 0
                        property bool wasSelected: false
                        property bool additiveSelection: false
                        property bool moved: false
                        onPressed: mouse => {
                            wasSelected = modelData.selected
                            additiveSelection = (mouse.modifiers & Qt.ControlModifier) !== 0
                            moved = false
                            wavePanel.groupDragStateRequested(true, 0, index)
                            pressPlotX = mapToItem(plotArea, mouse.x, mouse.y).x
                            originalStart = waveformInterval.visualStart
                            originalEnd = waveformInterval.visualEnd
                        }
                        onPositionChanged: mouse => {
                            if (!pressed)
                                return
                            let delta = (mapToItem(plotArea, mouse.x, mouse.y).x - pressPlotX) / Math.max(1, plotArea.width) * wavePanel.viewportSpan
                            wavePanel.groupDragStateRequested(true, delta, index)
                            moved = moved || Math.abs(delta) > 1e-6
                        }
                        onReleased: {
                            let finalDelta = wavePanel.groupDragDelta
                            wavePanel.groupDragFinished(index, additiveSelection, moved, finalDelta)
                        }
                        onCanceled: {
                            wavePanel.groupDragStateRequested(false, 0, -1)
                        }
                        onWheel: wheel => {
                            let point = mapToItem(plotArea, wheel.x, wheel.y)
                            wavePanel.zoomRequested(Math.max(0, Math.min(1, point.x / Math.max(1, plotArea.width))), wheel.angleDelta.y / 120.0)
                            wheel.accepted = true
                        }
                    }
                    Rectangle {
                        width: 8
                        anchors.left: parent.left
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        z: 3
                        visible: modelData.selected && wavePanel.activeTool === "Select / Edit"
                        color: "white"
                        opacity: 0.9
                        border.color: wavePanel.intervalColor(modelData.lane)
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.SizeHorCursor
                            property real pressPlotX: 0
                            property real originalStart: 0
                            onPressed: mouse => {
                                pressPlotX = mapToItem(plotArea, mouse.x, mouse.y).x
                                originalStart = waveformInterval.visualStart
                            }
                            onPositionChanged: mouse => {
                                if (!pressed)
                                    return
                                let delta = (mapToItem(plotArea, mouse.x, mouse.y).x - pressPlotX) / Math.max(1, plotArea.width) * wavePanel.viewportSpan
                                waveformInterval.visualStart = Math.max(0, Math.min(waveformInterval.visualEnd - 1e-6, originalStart + delta))
                            }
                            onReleased: studio.updateAnnotation(index, waveformInterval.visualStart, waveformInterval.visualEnd)
                        }
                    }
                    Rectangle {
                        width: 8
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        z: 3
                        visible: modelData.selected && wavePanel.activeTool === "Select / Edit"
                        color: "white"
                        opacity: 0.9
                        border.color: wavePanel.intervalColor(modelData.lane)
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.SizeHorCursor
                            property real pressPlotX: 0
                            property real originalEnd: 0
                            onPressed: mouse => {
                                pressPlotX = mapToItem(plotArea, mouse.x, mouse.y).x
                                originalEnd = waveformInterval.visualEnd
                            }
                            onPositionChanged: mouse => {
                                if (!pressed)
                                    return
                                let delta = (mapToItem(plotArea, mouse.x, mouse.y).x - pressPlotX) / Math.max(1, plotArea.width) * wavePanel.viewportSpan
                                waveformInterval.visualEnd = Math.min(1, Math.max(waveformInterval.visualStart + 1e-6, originalEnd + delta))
                            }
                            onReleased: studio.updateAnnotation(index, waveformInterval.visualStart, waveformInterval.visualEnd)
                        }
                    }
                }
            }
            Rectangle {
                visible: waveformInteraction.creating
                z: 30
                x: Math.min(waveformInteraction.pressX, waveformInteraction.dragX)
                width: Math.max(2, Math.abs(waveformInteraction.dragX - waveformInteraction.pressX))
                height: plotArea.height
                color: wavePanel.intervalColor(["Cycle", "Pick", "Put", "Fork Collision", "Ignore"].indexOf(wavePanel.activeTool))
                opacity: 0.22
                border.width: 1
                border.color: wavePanel.intervalColor(["Cycle", "Pick", "Put", "Fork Collision", "Ignore"].indexOf(wavePanel.activeTool))
                Label { anchors.left: parent.left; anchors.top: parent.top; anchors.margins: 5; text: wavePanel.activeTool; font.bold: true; font.pixelSize: 10; color: DesignTokens.text }
            }
        }
    }

    component TrainPage: ScrollView {
        id: trainPage
        objectName: "trainPageScroll"
        clip: true
        contentWidth: availableWidth
        contentHeight: trainPageContent.implicitHeight + 40
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
        ScrollBar.vertical.policy: ScrollBar.AsNeeded
        ColumnLayout {
            id: trainPageContent
            x: 20
            y: 20
            width: Math.max(0, trainPage.availableWidth - 40)
            height: implicitHeight
            spacing: 14
            SectionTitle { heading: "Train"; supporting: "Train and qualify a collision profile across the supplied speed conditions." }
            RowLayout { Layout.fillWidth: true; Layout.preferredHeight: learningSettingsContent.implicitHeight + 28; Layout.maximumHeight: learningSettingsContent.implicitHeight + 28; spacing: 12
                Card { objectName: "learningSettingsCard"; Layout.preferredWidth: 640; Layout.preferredHeight: learningSettingsContent.implicitHeight + 28
                    ColumnLayout { id: learningSettingsContent; anchors.fill: parent; anchors.margins: 14; spacing: 16
                        Label { text: "Learning Settings"; font.bold: true; font.pixelSize: 16 }
                        Frame {
                            objectName: "firParameterGroup"
                            Layout.fillWidth: true
                            padding: 12
                            visible: studio.learningSettings.model_families.indexOf("fir") >= 0
                            background: Rectangle { color: DesignTokens.surface; radius: DesignTokens.radius; border.color: DesignTokens.border }
                            contentItem: ColumnLayout {
                                spacing: 8
                                Label { text: "Ridge parameters (FIR / VAR)"; font.bold: true; font.pixelSize: 14; color: DesignTokens.text }
                                Label { visible: studio.learningSettings.model_families.indexOf("fir") >= 0; text: "Training mode"; color: DesignTokens.textMuted }
                                ButtonGroup { id: trainingModeGroup }
                                RowLayout {
                                    visible: studio.learningSettings.model_families.indexOf("fir") >= 0
                                    RadioButton { objectName: "fixedGridModeButton"; text: studio.singleImuMode ? "Fixed grid Ridge" : "Fixed grid FIR + Ridge"; checked: studio.learningSettings.training_mode === "fixed_grid"; enabled: !studio.learningSettingsLocked; ButtonGroup.group: trainingModeGroup; onClicked: studio.setLearningSetting("training_mode", "fixed_grid") }
                                    RadioButton { objectName: "optimizedModeButton"; text: "Optimized linear regression"; checked: studio.learningSettings.training_mode === "optimized"; enabled: !studio.learningSettingsLocked; ButtonGroup.group: trainingModeGroup; onClicked: studio.setLearningSetting("training_mode", "optimized") }
                                }
                                ColumnLayout {
                                    objectName: "fixedGridSettings"
                                    visible: studio.learningSettings.model_families.indexOf("fir") >= 0 && studio.learningSettings.training_mode === "fixed_grid"
                                    Layout.fillWidth: true
                                    Label { text: "History to compare (ms)"; color: DesignTokens.textMuted }
                                    RowLayout {
                                        CheckBox { objectName: "fixedHistory4Setting"; text: "4"; checked: studio.learningSettings.fixed_history_ms.indexOf(4) >= 0; enabled: !studio.learningSettingsLocked; onClicked: studio.setFixedHistorySelected(4, checked) }
                                        CheckBox { objectName: "fixedHistory8Setting"; text: "8"; checked: studio.learningSettings.fixed_history_ms.indexOf(8) >= 0; enabled: !studio.learningSettingsLocked; onClicked: studio.setFixedHistorySelected(8, checked) }
                                        CheckBox { objectName: "fixedHistory16Setting"; text: "16"; checked: studio.learningSettings.fixed_history_ms.indexOf(16) >= 0; enabled: !studio.learningSettingsLocked; onClicked: studio.setFixedHistorySelected(16, checked) }
                                        CheckBox { objectName: "fixedHistory32Setting"; text: "32"; checked: studio.learningSettings.fixed_history_ms.indexOf(32) >= 0; enabled: !studio.learningSettingsLocked; onClicked: studio.setFixedHistorySelected(32, checked) }
                                        CheckBox { objectName: "fixedHistory64Setting"; text: "64"; checked: studio.learningSettings.fixed_history_ms.indexOf(64) >= 0; enabled: !studio.learningSettingsLocked; onClicked: studio.setFixedHistorySelected(64, checked) }
                                        CheckBox { objectName: "fixedHistory128Setting"; text: "128"; checked: studio.learningSettings.fixed_history_ms.indexOf(128) >= 0; enabled: !studio.learningSettingsLocked; onClicked: studio.setFixedHistorySelected(128, checked) }
                                    }
                                    Label { text: "Ridge alpha to compare"; color: DesignTokens.textMuted }
                                    RowLayout {
                                        CheckBox { objectName: "fixedAlpha1e6Setting"; text: "1e-6"; checked: studio.learningSettings.fixed_ridge_alphas.indexOf(0.000001) >= 0; enabled: !studio.learningSettingsLocked; onClicked: studio.setFixedRidgeAlphaSelected(0.000001, checked) }
                                        CheckBox { objectName: "fixedAlpha1e4Setting"; text: "1e-4"; checked: studio.learningSettings.fixed_ridge_alphas.indexOf(0.0001) >= 0; enabled: !studio.learningSettingsLocked; onClicked: studio.setFixedRidgeAlphaSelected(0.0001, checked) }
                                        CheckBox { objectName: "fixedAlpha1e2Setting"; text: "0.01"; checked: studio.learningSettings.fixed_ridge_alphas.indexOf(0.01) >= 0; enabled: !studio.learningSettingsLocked; onClicked: studio.setFixedRidgeAlphaSelected(0.01, checked) }
                                        CheckBox { objectName: "fixedAlpha1Setting"; text: "1"; checked: studio.learningSettings.fixed_ridge_alphas.indexOf(1) >= 0; enabled: !studio.learningSettingsLocked; onClicked: studio.setFixedRidgeAlphaSelected(1, checked) }
                                        CheckBox { objectName: "fixedAlpha100Setting"; text: "100"; checked: studio.learningSettings.fixed_ridge_alphas.indexOf(100) >= 0; enabled: !studio.learningSettingsLocked; onClicked: studio.setFixedRidgeAlphaSelected(100, checked) }
                                    }
                                }
                                CheckBox { objectName: "robustRefitSetting"; visible: studio.learningSettings.model_families.indexOf("fir") >= 0 && studio.learningSettings.training_mode === "optimized"; text: "Use Robust refit"; checked: studio.learningSettings.use_robust_refit; enabled: !studio.learningSettingsLocked; onClicked: studio.setLearningSetting("use_robust_refit", checked) }
                                RowLayout { objectName: "convergenceSettingRow"; visible: studio.learningSettings.model_families.indexOf("fir") >= 0 && studio.learningSettings.training_mode === "optimized"; Layout.fillWidth: true
                                    Label { text: "Loss improvement tolerance (%)"; Layout.preferredWidth: 240 }
                                    TextField { objectName: "convergenceSetting"; Layout.fillWidth: true; Layout.minimumWidth: 80; Layout.preferredWidth: 100; text: String(studio.learningSettings.convergence_tolerance_percent); enabled: !studio.learningSettingsLocked; validator: DoubleValidator { bottom: 0.001; top: 100; decimals: 3; locale: "C" } onEditingFinished: studio.setLearningSetting("convergence_tolerance_percent", Number(text)) }
                                }
                                Tag { visible: studio.learningSettings.model_families.indexOf("fir") >= 0; label: studio.candidateCount < 0 ? "FIR threshold candidates determined after scoring" : studio.candidateCount ? studio.candidateCount.toLocaleString() + " FIR parameter combinations" : "FIR plan waits for Sample Rate" }
                            }
                        }
                        Frame {
                            objectName: "mlpParameterGroup"
                            Layout.fillWidth: true
                            padding: 12
                            visible: studio.learningSettings.model_families.indexOf("mlp") >= 0
                            background: Rectangle { color: DesignTokens.surface; radius: DesignTokens.radius; border.color: DesignTokens.border }
                            contentItem: ColumnLayout {
                                spacing: 8
                                Label { text: "MLP"; font.bold: true; font.pixelSize: 14; color: DesignTokens.text }
                                ColumnLayout {
                                    objectName: "mlpSettings"
                                    visible: studio.learningSettings.model_families.indexOf("mlp") >= 0
                                    Label { text: "MLP History to compare (ms)"; color: DesignTokens.textMuted }
                                    RowLayout {
                                        Repeater { model: [4, 8, 16, 32, 64, 128]
                                            CheckBox { required property int modelData; text: String(modelData); checked: studio.learningSettings.mlp_history_ms.indexOf(modelData) >= 0; enabled: !studio.learningSettingsLocked; onClicked: studio.setMlpSelected("mlp_history_ms", 0, modelData, checked) }
                                        }
                                    }
                                    RowLayout {
                                        Label { text: "Hidden layers" }
                                        TextField { objectName: "mlpDepthSetting"; text: String(studio.learningSettings.mlp_layer_widths.length); enabled: !studio.learningSettingsLocked; validator: IntValidator { bottom: 1 } onEditingFinished: { if (acceptableInput) studio.setMlpDepth(Number(text)); text = Qt.binding(function() { return String(studio.learningSettings.mlp_layer_widths.length) }) } }
                                    }
                                    Repeater {
                                        model: studio.learningSettings.mlp_layer_widths.length
                                        ColumnLayout {
                                            required property int index
                                            readonly property int layerIndex: index
                                            Label { text: "Layer " + (parent.layerIndex + 1) + " widths to compare"; color: DesignTokens.textMuted }
                                            RowLayout {
                                                property int layerIndex: parent.layerIndex
                                                Repeater { model: [4, 8, 16, 32, 64, 128]
                                                    CheckBox { required property int modelData; objectName: "mlpLayer" + parent.layerIndex + "Width" + modelData; text: String(modelData); checked: (studio.learningSettings.mlp_layer_widths[parent.layerIndex] || []).indexOf(modelData) >= 0; enabled: !studio.learningSettingsLocked; onClicked: studio.setMlpSelected("mlp_layer_widths", parent.layerIndex, modelData, checked) }
                                                }
                                            }
                                        }
                                    }
                                    Label { text: "MLP L2 to compare"; color: DesignTokens.textMuted }
                                    RowLayout {
                                        Repeater { model: [0.0001, 0.001, 0.01]
                                            CheckBox { required property real modelData; text: String(modelData); checked: studio.learningSettings.mlp_l2.indexOf(modelData) >= 0; enabled: !studio.learningSettingsLocked; onClicked: studio.setMlpSelected("mlp_l2", 0, modelData, checked) }
                                        }
                                    }
                                    Label { text: studio.mlpCandidateCountText; color: DesignTokens.textMuted }
                                }
                            }
                        }
                        Frame {
                            objectName: "sharedParameterGroup"
                            Layout.fillWidth: true
                            padding: 12
                            background: Rectangle { color: DesignTokens.canvas; radius: DesignTokens.radius; border.color: DesignTokens.border }
                            contentItem: ColumnLayout {
                                spacing: 8
                                Label { text: "Shared settings"; font.bold: true; font.pixelSize: 14; color: DesignTokens.text }
                                Label { text: "Target Numeric Type"; color: DesignTokens.textMuted }
                                ButtonGroup { id: numericGroup }
                                RowLayout {
                                    RadioButton { objectName: "float32TargetButton"; text: "float32"; enabled: ["Learning", "Qualifying", "Refining Speed Range", "Cancelling"].indexOf(studio.runState) < 0; checked: studio.numericType === "float32"; ButtonGroup.group: numericGroup; onClicked: studio.setNumericType("float32") }
                                    RadioButton { objectName: "float64TargetButton"; text: "float64"; enabled: ["Learning", "Qualifying", "Refining Speed Range", "Cancelling"].indexOf(studio.runState) < 0; checked: studio.numericType === "float64"; ButtonGroup.group: numericGroup; onClicked: studio.setNumericType("float64") }
                                }
                                RowLayout {
                                    Label { text: "N-fold"; Layout.preferredWidth: 180 }
                                    SpinBox { objectName: "nFoldSetting"; from: 2; to: 10; value: studio.learningSettings.n_fold; enabled: !studio.learningSettingsLocked; editable: true; onValueModified: studio.setLearningSetting("n_fold", value) }
                                }
                                CheckBox { objectName: "includeTrainingMseSetting"; text: "Include Training MSE (50% / 50%)"; checked: studio.learningSettings.include_training_mse; enabled: !studio.learningSettingsLocked; onClicked: studio.setLearningSetting("include_training_mse", checked) }
                                RowLayout { Layout.fillWidth: true
                                    Label { text: "Validation allowed increase (%)"; Layout.preferredWidth: 240 }
                                    TextField { objectName: "validationAllowanceSetting"; Layout.fillWidth: true; Layout.minimumWidth: 80; Layout.preferredWidth: 100; text: String(studio.learningSettings.validation_allowance_percent); enabled: !studio.learningSettingsLocked; validator: DoubleValidator { bottom: 0; top: 100; decimals: 3; locale: "C" } onEditingFinished: studio.setLearningSetting("validation_allowance_percent", Number(text)) }
                                }
                            }
                        }
                        Label { text: "Selected before Start Learning; immutable for the run."; color: DesignTokens.textMuted; font.pixelSize: 11 }
                    }
                }
                Card { Layout.fillWidth: true; Layout.preferredHeight: learningSettingsContent.implicitHeight + 28
                    ColumnLayout { anchors.fill: parent; anchors.margins: 14; spacing: 8
                        Label { text: "Algorithms and sources"; font.bold: true; font.pixelSize: 16 }
                        ColumnLayout {
                            Layout.fillWidth: true
                            Repeater {
                                model: [
                                    {key:"fir",name:"Dual IMU — MIMO FIR (Ridge)",tip:"Multi-input multi-output finite impulse response model fitted with Ridge.\nPredicts External XYZ from current and historical Internal XYZ.\nBoth IMUs must use raw XYZ or both filtered XYZ."},
                                    {key:"mlp",name:"Dual IMU — MLP",tip:"Multilayer perceptron: a nonlinear prediction model.\nPredicts External XYZ from current and historical Internal XYZ.\nBoth IMUs must use raw XYZ or both filtered XYZ."},
                                    {key:"var",name:"Single IMU — VAR (Ridge)",tip:"Vector autoregressive model fitted with Ridge.\nPredicts the selected IMU current XYZ from its strictly earlier XYZ.\nUses prediction residuals for detection; requires filtered XYZ."}
                                ]
                                delegate: RowLayout {
                                    required property var modelData
                                    Layout.fillWidth:true
                                    HoverHandler { id:algorithmHover }
                                    ToolTip.visible: algorithmHover.hovered
                                    ToolTip.delay: 400
                                    ToolTip.text: modelData.tip + (modelData.key === "var" && !studio.varSourceReady ? "\nUnavailable: the selected IMU needs filtered XYZ in every recording." : "")
                                    CheckBox {
                                        objectName: modelData.key + "ModelSetting"
                                        Layout.fillWidth:true
                                        text:modelData.name
                                        checked:studio.trainingAlgorithms.indexOf(modelData.key) >= 0
                                        enabled:!studio.learningSettingsLocked && (modelData.key !== "var" || studio.varSourceReady || checked)
                                        onClicked:studio.setTrainingAlgorithmSelected(modelData.key,checked)
                                    }
                                    ComboBox {
                                        objectName:modelData.key + "TrainingSource"
                                        Layout.preferredWidth:180
                                        model:modelData.key === "var" ? ["Internal filtered XYZ","External filtered XYZ"] : ["Both raw XYZ","Both filtered XYZ"]
                                        currentIndex:studio.trainingSources[modelData.key] === (modelData.key === "var" ? "external" : "filtered") ? 1 : 0
                                        enabled:!studio.learningSettingsLocked
                                        onActivated:studio.setTrainingSource(modelData.key, modelData.key === "var" ? (currentIndex ? "external" : "internal") : (currentIndex ? "filtered" : "raw"))
                                    }
                                }
                            }
                            Label { text:studio.trainingAdmissionMessage; visible:text.length>0; color:DesignTokens.warning; wrapMode:Text.Wrap; Layout.fillWidth:true }
                        }
                        Label { text: "Readiness"; font.bold: true; font.pixelSize: 16 }
                        ReadinessRow { label: "All active mappings confirmed"; pass: studio.recordings.length > 0 && studio.recordings.every(function(r) { return r.mappingStatus === "Confirmed" }) }
                        ReadinessRow { label: "Cycle and event annotations confirmed"; pass: studio.annotationsReady }
                        ReadinessRow { label: "Select Target Numeric Type"; pass: studio.numericType !== "" }
                        ReadinessRow { label: "One compatible session Sample Rate"; pass: studio.sessionRateReady }
                        ReadinessRow { label: "Select models and required parameters"; pass: studio.modelSelectionsReady }
                    }
                }
            }
            Card { objectName: "candidateDashboardCard"; Layout.fillWidth: true; Layout.preferredHeight: 680; Layout.minimumHeight: 520
                ColumnLayout { anchors.fill: parent; anchors.margins: 16; spacing: 12
                    RowLayout { Layout.fillWidth: true
                        ColumnLayout {
                            Label { text: "Candidate Dashboard"; font.bold: true; font.pixelSize: 16 }
                            Label { text: "Train and qualify a collision profile across the supplied speed conditions."; color: DesignTokens.textMuted }
                            Label { text: studio.learningSettings.training_mode === "fixed_grid" ? "Cycle Normal + Pick + Put · balanced N-fold · selected fixed grid" : "Cycle Normal + Pick + Put · balanced N-fold · bounded coarse/fine search"; color: DesignTokens.textMuted }
                        }
                        Item { Layout.fillWidth: true }
                        PaddedButton {
                            objectName: "trainingActionButton"
                            readonly property bool active: ["Learning", "Qualifying", "Refining Speed Range", "Cancelling"].indexOf(studio.runState) >= 0
                            text: active ? (studio.runState === "Cancelling" ? "Cancelling…" : "Cancel") : "Start Learning"
                            highlighted: !active
                            enabled: studio.canStartLearning || (active && studio.runState !== "Cancelling")
                            onClicked: active ? studio.cancelLearning() : studio.startLearning()
                        }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label { text: "FIR / MLP Training workers" }
                        SpinBox {
                            objectName: "trainingWorkerCount"
                            from: 1; to: 8; value: studio.trainingWorkerCount
                            enabled: !studio.learningSettingsLocked
                            onValueModified: studio.setTrainingWorkers(value)
                        }
                        Item { Layout.fillWidth: true }
                    }
                    ProgressBar { Layout.fillWidth: true; from: 0; to: 1; value: studio.progress }
                    RowLayout {
                        Layout.fillWidth: true
                        Tag { label: studio.runState }
                        Label { text: Math.round(studio.progress * 100) + "%"; color: DesignTokens.textMuted }
                        Item { Layout.fillWidth: true }
                        ColumnLayout {
                            objectName: "trainingTiming"
                            spacing: 2
                            Label { text: studio.runElapsedText; color: DesignTokens.textMuted; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight }
                            Label { text: studio.stageElapsedText; color: DesignTokens.textMuted; font.pixelSize: 11; Layout.alignment: Qt.AlignRight }
                            Label { text: studio.runStartedAtText === "" ? "" : "Started: " + studio.runStartedAtText; color: DesignTokens.textMuted; font.pixelSize: 11; Layout.alignment: Qt.AlignRight }
                            Label { text: studio.runFinishedAtText === "" ? "Qualification starts automatically" : "Finished: " + studio.runFinishedAtText; color: DesignTokens.textMuted; font.pixelSize: 11; Layout.alignment: Qt.AlignRight }
                        }
                    }
                    Label { objectName: "trainingFallbackSummary"; text: studio.trainingFallbackSummary; color: DesignTokens.textMuted; font.pixelSize: 11; wrapMode: Text.Wrap; Layout.fillWidth: true }
                    Label { objectName: "trainingCurrentSummary"; text: studio.trainingCurrentSummary; color: DesignTokens.text; font.pixelSize: 12; wrapMode: Text.Wrap; Layout.fillWidth: true }
                    ColumnLayout {
                        objectName: "trainingFailureReason"
                        visible: studio.runFailureReason !== ""
                        Layout.fillWidth: true
                        Label {
                            Layout.fillWidth: true
                            text: "Failure reason: " + studio.runFailureReason.split("\n")[0]
                            color: "#9B2630"; wrapMode: Text.Wrap
                            maximumLineCount: 4; elide: Text.ElideRight
                        }
                        RowLayout {
                            CheckBox { id: failureDetails; objectName: "trainingFailureDetailsToggle"; text: "Show details" }
                            PaddedButton { text: "Copy details"; onClicked: studio.copyTrainingFailureDetails() }
                        }
                        ScrollView {
                            visible: failureDetails.checked
                            Layout.fillWidth: true; Layout.preferredHeight: 110
                            TextArea { text: studio.runFailureReason; readOnly: true; selectByMouse: true; wrapMode: TextEdit.Wrap }
                        }
                    }
                    Rectangle {
                        id: trainingExecutionLog
                        objectName: "trainingExecutionLog"
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.minimumHeight: 170
                        color: "#FBFCFE"; border.color: DesignTokens.border; radius: 6
                        function positionAtLatestIfPointerOutside() {
                            if (!trainingLogHover.hovered)
                                trainingLogList.positionViewAtEnd()
                        }
                        function scheduleLatestIfPointerOutside() {
                            Qt.callLater(trainingExecutionLog.positionAtLatestIfPointerOutside)
                        }
                        HoverHandler {
                            id: trainingLogHover
                            acceptedDevices: PointerDevice.Mouse
                            onHoveredChanged: {
                                if (!hovered)
                                    trainingExecutionLog.scheduleLatestIfPointerOutside()
                            }
                        }
                        ColumnLayout { anchors.fill: parent; anchors.margins: 10; spacing: 6
                            RowLayout { Layout.fillWidth: true
                                Label { text: "Execution Log"; font.bold: true; font.pixelSize: 14 }
                                Item { Layout.fillWidth: true }
                            }
                            Label { visible: studio.trainingLogDiscardedText !== ""; text: studio.trainingLogDiscardedText; color: DesignTokens.warning; font.pixelSize: 11 }
                            ListView {
                                id: trainingLogList
                                objectName: "trainingExecutionLogList"
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                clip: true
                                spacing: 4
                                model: studio.trainingLogEntries
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                                onCountChanged: trainingExecutionLog.scheduleLatestIfPointerOutside()
                                onContentHeightChanged: trainingExecutionLog.scheduleLatestIfPointerOutside()
                                onHeightChanged: trainingExecutionLog.scheduleLatestIfPointerOutside()
                                delegate: Rectangle {
                                    required property var modelData
                                    width: ListView.view.width
                                    height: logText.implicitHeight + 14
                                    color: DesignTokens.surfaceMuted; radius: 4
                                    Label {
                                        id: logText
                                        anchors.fill: parent; anchors.margins: 7
                                        text: modelData.time + " · " + modelData.stage + " · Round " + modelData.round
                                              + (modelData.scope ? " · " + modelData.scope : "")
                                              + (modelData.work ? " · " + modelData.work : "")
                                              + (modelData.elapsed ? " · " + modelData.elapsed : "")
                                              + "\n" + modelData.detail
                                        color: DesignTokens.text; font.pixelSize: 11; wrapMode: Text.Wrap
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    component ReadinessRow: RowLayout {
        property string label
        property bool pass
        Rectangle {
            width: 21; height: 21; radius: 10; color: pass ? DesignTokens.success : "#F5E5CF"
            Label { anchors.centerIn: parent; text: pass ? "✓" : "!"; color: pass ? "white" : DesignTokens.warning; font.bold: true }
        }
        Label { text: label; color: DesignTokens.text }
    }

    component QualificationPage: Item {
        id: qualificationPage
        FileDialog {
            id: replayCsvDialog
            objectName: "replayCsvDialog"
            title: "Export Replay CSV"
            fileMode: FileDialog.SaveFile
            nameFilters: ["CSV files (*.csv)"]
            defaultSuffix: "csv"
            selectedFile: studio.replayCsvSuggestedFileName
            onAccepted: studio.exportReplayCsv(selectedFile)
        }
        FileDialog {
            id: modelTxtDialog
            objectName: "modelTxtDialog"
            title: "Export Model TXT"
            fileMode: FileDialog.SaveFile
            nameFilters: ["Text files (*.txt)"]
            defaultSuffix: "txt"
            selectedFile: studio.modelTxtSuggestedFileName
            onAccepted: studio.exportModelTxt(selectedFile)
        }
        ColumnLayout { anchors.fill: parent; anchors.margins: 20; spacing: 14
            SectionTitle { heading: "Replay & Qualify"; supporting: "Every supplied speed and Collision Offset is replayed. A passing collision latency is ≤ 150 ms from collision onset. Ignore samples are excluded without extending the deadline." }
            Card { id: retainedWinnerCard; Layout.fillWidth: true; Layout.fillHeight: true
                property var recordingColumnWidths: [220, 120, 120, 190, 170, 190, 120, 110, 280, 170]
                property int recordingColumnSpacing: 12
                property int recordingTableWidth: recordingColumnWidths.reduce(function(total, value) { return total + value }, 0)
                                                  + recordingColumnSpacing * (recordingColumnWidths.length - 1) + 18
                ColumnLayout { anchors.fill: parent; anchors.margins: 14; spacing: 10
                    RowLayout { Layout.fillWidth: true
                        Label { text: "Retained Round Winners"; font.bold: true; font.pixelSize: 16 }
                        Tag { objectName: "completedTrainingModeTag"; visible: studio.completedTrainingMode !== ""; label: studio.completedTrainingMode }
                        Label { text: "Kernel"; color: DesignTokens.textMuted }
                        ComboBox {
                            objectName: "retainedKernelSelector"
                            Layout.preferredWidth: 360
                            model: studio.retainedKernelOptions
                            textRole: "label"
                            currentIndex: studio.retainedKernelIndex
                            onActivated: studio.selectRetainedKernel(currentIndex)
                        }
                        Item { Layout.fillWidth: true }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label { objectName: "qualificationPolicyStatus"; text: studio.selectedQualificationStatus; Layout.fillWidth: true; wrapMode: Text.Wrap }
                        PaddedButton {
                            objectName: "requalifySelectedKernel"
                            text: studio.qualificationValidationActive ? "Cancel Qualification" : "Run Qualification"
                            enabled: !studio.jsonExportActive && !studio.learningSettingsLocked && studio.resultKernels.length > 0
                            onClicked: studio.qualificationValidationActive ? studio.cancelQualification() : studio.requalifySelected()
                        }
                    }
                    Label { objectName:"selectedResultSource"; text:studio.selectedResultSource; visible:text.length>0; Layout.fillWidth:true; wrapMode:Text.Wrap; color:DesignTokens.text }
                    Label { visible: studio.resultKernels.length === 0; text: "One winner from every completed Offset / Speed fallback round will appear here."; color: DesignTokens.textMuted }
                    Rectangle {
                        objectName: "selectedKernelParameters"
                        Layout.fillWidth: true
                        implicitHeight: Math.max(kernelParameterGrid.implicitHeight + 16, exportModelTxtButton.implicitHeight + 24)
                        color: DesignTokens.surfaceMuted; border.color: DesignTokens.border; radius: 5
                        RowLayout { anchors.fill: parent; anchors.margins: 8; spacing: 12
                            GridLayout {
                                id: kernelParameterGrid
                                Layout.fillWidth: true
                                columns: 4; columnSpacing: 20; rowSpacing: 5
                                Repeater {
                                    model: [
                                        { title: "Kernel ID / Round", value: (studio.selectedKernelParameters.kernelId || "—") + " / " + (studio.selectedKernelParameters.round || "—") },
                                        { title: "Training / Qualified range", value: (studio.selectedKernelParameters.trainingRange || "—") + " / " + (studio.selectedKernelParameters.qualifiedRange || "—") },
                                        { title: "Speeds", value: studio.selectedKernelParameters.speeds || "—" },
                                        { title: "Offsets", value: studio.selectedKernelParameters.offsets || "—" },
                                        { title: "History / taps", value: studio.selectedKernelParameters.history || "—" },
                                        { title: "Preprocessing", value: studio.selectedKernelParameters.preprocessing || "—" },
                                        { title: "Readiness", value: studio.selectedKernelParameters.readiness || "—" },
                                        { title: "Model / hidden widths", value: (studio.selectedKernelParameters.modelFamily || "FIR") + " / " + (studio.selectedKernelParameters.architecture || "—") },
                                        { title: "Parameter count", value: String(studio.selectedKernelParameters.parameterCount || 0) },
                                        { title: "Parameters / estimated buffers (bytes)", value: String(studio.selectedKernelParameters.parameterBytes || 0) + " / " + String(studio.selectedKernelParameters.workingBufferBytes || 0) },
                                        { title: "Ridge alpha / MLP L2", value: studio.selectedKernelParameters.ridgeAlpha || "—" },
                                        { title: "Scale method / Robust K", value: studio.selectedKernelParameters.scaleAndK || "—" },
                                        { title: "Threshold", value: studio.selectedKernelParameters.threshold || "—" },
                                        { title: "Training loss", value: studio.selectedKernelParameters.trainingLoss || "N/A" }
                                    ]
                                    delegate: ColumnLayout {
                                        required property var modelData
                                        Layout.fillWidth: true; Layout.minimumWidth: 145; spacing: 1
                                        Label { text: modelData.title; color: DesignTokens.textMuted; font.pixelSize: 10 }
                                        Label { text: modelData.value; color: DesignTokens.text; font.bold: true; font.pixelSize: 11; elide: Text.ElideRight; Layout.fillWidth: true }
                                    }
                                }
                            }
                            PaddedButton {
                                id: exportModelTxtButton
                                objectName: "exportModelTxtButton"
                                text: studio.singleImuMode ? "Single IMU: simulation only" : studio.selectedKernelParameters.modelFamily === "MLP" ? "MLP export deferred" : studio.modelExportActive ? "Exporting..." : "Export Model TXT"
                                enabled: !studio.singleImuMode && studio.selectedKernelParameters.modelFamily !== "MLP" && !studio.replayExportActive && !studio.modelExportActive && studio.resultKernels.length > 0
                                onClicked: modelTxtDialog.open()
                            }
                        }
                    }
                    Label { text: "Recording Qualification Results"; font.bold: true; font.pixelSize: 14 }
                    Flickable {
                        id: recordingResultsTable
                        objectName: "recordingResultsTable"
                        Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 120
                        contentWidth: retainedWinnerCard.recordingTableWidth
                        contentHeight: 31 + studio.replayRecordingResults.length * 49
                        clip: true; boundsBehavior: Flickable.StopAtBounds
                        ScrollBar.horizontal: ScrollBar { policy: ScrollBar.AsNeeded }
                        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                        Column {
                            width: retainedWinnerCard.recordingTableWidth
                            height: recordingResultsTable.contentHeight
                            spacing: 4
                            Row {
                                x: 9; height: 26; spacing: retainedWinnerCard.recordingColumnSpacing
                                Repeater {
                                    model: ["Recording", "Robot Speed", "Collision Offset", "Normal / Pick / Put false", "Collision detected / total", "Collision SNR (dB)", "Worst latency", "Status", "Reason", ""]
                                    Label { required property string modelData; required property int index; width: retainedWinnerCard.recordingColumnWidths[index]; text: modelData; color: DesignTokens.textMuted; font.bold: true; font.pixelSize: 11 }
                                }
                            }
                            Repeater {
                                model: studio.replayRecordingResults
                                delegate: Rectangle {
                                    required property var modelData
                                    width: retainedWinnerCard.recordingTableWidth; height: 45
                                    color: DesignTokens.primarySoft; radius: 5
                                    Row { anchors.fill: parent; anchors.margins: 9; spacing: retainedWinnerCard.recordingColumnSpacing
                                        Label { width: retainedWinnerCard.recordingColumnWidths[0]; text: modelData.recording; elide: Text.ElideMiddle }
                                        Label { width: retainedWinnerCard.recordingColumnWidths[1]; text: modelData.speed }
                                        Label { width: retainedWinnerCard.recordingColumnWidths[2]; text: modelData.offset }
                                        Label { width: retainedWinnerCard.recordingColumnWidths[3]; text: modelData.falseCounts }
                                        Label { width: retainedWinnerCard.recordingColumnWidths[4]; text: modelData.collisionCount }
                                        Label { width: retainedWinnerCard.recordingColumnWidths[5]; text: modelData.collisionSnr }
                                        Label { width: retainedWinnerCard.recordingColumnWidths[6]; text: modelData.latency }
                                        Label { width: retainedWinnerCard.recordingColumnWidths[7]; text: modelData.status; color: modelData.status === "Pass" ? DesignTokens.success : DesignTokens.warning; font.bold: true }
                                        Label { width: retainedWinnerCard.recordingColumnWidths[8]; text: modelData.reason; elide: Text.ElideRight; ToolTip.visible: truncated && reasonHover.hovered; ToolTip.text: modelData.reason
                                            HoverHandler { id: reasonHover }
                                        }
                                        PaddedButton {
                                            objectName: "exportReplayCsvButton"
                                            width: retainedWinnerCard.recordingColumnWidths[9]
                                            text: studio.singleImuMode ? "Simulation only" : studio.replayExportActive ? "Exporting..." : "Export Replay CSV"
                                            enabled: !studio.singleImuMode && !studio.replayExportActive && !studio.modelExportActive
                                            onClicked: {
                                                studio.selectReplayRecording(modelData.recordingIndex)
                                                replayCsvDialog.open()
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    component ExportPage: Item {
        objectName: "jsonExportPage"
        ColumnLayout {
            anchors.fill: parent; anchors.margins: 20; spacing: 14
            RowLayout {
                Layout.fillWidth: true
                SectionTitle {
                    heading: "Export Profile"
                    supporting: "Export models qualified with the common 0.8 / 50 ms event policy. Requalify historical models in Replay & Qualify."
                    Layout.fillWidth: true
                }
                Tag { label: studio.jsonExportKernels.length + " qualified"; tagColor: "#E4F4EE" }
            }
            Card {
                Layout.fillWidth: true; Layout.fillHeight: true
                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 16; spacing: 0
                    RowLayout {
                        Layout.fillWidth: true; Layout.preferredHeight: 42; spacing: 16
                        Label { text: "Kernel ID"; font.bold: true; Layout.preferredWidth: 110 }
                        Label { text: "History / taps"; font.bold: true; Layout.preferredWidth: 180 }
                        Label { text: "Threshold"; font.bold: true; Layout.preferredWidth: 130 }
                        Label { text: "Qualified range (mm/s, offset)"; font.bold: true; Layout.fillWidth: true }
                        Item { Layout.preferredWidth: 170 }
                    }
                    Rectangle { Layout.fillWidth: true; height: 1; color: DesignTokens.border }
                    ListView {
                        id: jsonKernelList
                        objectName: "jsonExportKernelList"
                        Layout.fillWidth: true; Layout.fillHeight: true
                        clip: true; spacing: 2
                        model: studio.jsonExportKernels
                        ScrollBar.vertical: ScrollBar { }
                        delegate: Rectangle {
                            required property var modelData
                            required property int index
                            width: ListView.view.width
                            height: Math.max(64, exportRow.implicitHeight + 24)
                            color: index % 2 ? DesignTokens.surfaceMuted : "transparent"
                            radius: 5
                            RowLayout {
                                id: exportRow
                                anchors.left: parent.left; anchors.right: parent.right
                                anchors.verticalCenter: parent.verticalCenter; spacing: 16
                                Label { text: modelData.kernelId; font.bold: true; Layout.preferredWidth: 110; elide: Text.ElideRight }
                                Label { text: modelData.kernelDepth; Layout.preferredWidth: 180; wrapMode: Text.Wrap }
                                Label { text: modelData.threshold; Layout.preferredWidth: 130; elide: Text.ElideRight }
                                ColumnLayout {
                                    Layout.fillWidth: true; spacing: 4
                                    Label { text: modelData.qualifiedRange; Layout.fillWidth: true; wrapMode: Text.Wrap }
                                    Label { text: modelData.exportReason; visible: text.length > 0; Layout.fillWidth: true; wrapMode: Text.Wrap; color: DesignTokens.warning; font.pixelSize: 11 }
                                }
                                ColumnLayout {
                                    Layout.preferredWidth: 170; spacing: 4
                                    PaddedButton {
                                        objectName: "exportJson_" + modelData.kernelId
                                        text: studio.jsonExportActive && studio.jsonExportKernel === modelData.kernelId ? "Exporting…" : "Export JSON"; highlighted: true
                                        Layout.fillWidth: true
                                        enabled: modelData.exportable && !studio.jsonExportActive && !studio.qualificationValidationActive
                                        onClicked: {
                                            window.jsonExportQueue = studio.prepareJsonExport(modelData.kernelId)
                                            window.nextJsonExport()
                                        }
                                    }
                                }
                            }
                        }
                        ColumnLayout {
                            anchors.centerIn: parent; width: Math.min(440, parent.width)
                            visible: jsonKernelList.count === 0; spacing: 12
                            Label { text: "No qualified kernels"; font.bold: true; font.pixelSize: 18; Layout.alignment: Qt.AlignHCenter }
                            Label { text: "Run Qualification in Replay & Qualify to make current-policy kernels available for JSON export."; Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.Wrap; color: DesignTokens.textMuted }
                            PaddedButton { text: "Replay & Qualify"; Layout.alignment: Qt.AlignHCenter; onClicked: studio.selectStage(3) }
                        }
                    }
                }
            }
        }
    }
}
