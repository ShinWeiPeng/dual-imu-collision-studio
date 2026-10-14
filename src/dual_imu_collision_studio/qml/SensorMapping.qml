import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "."

ScrollView {
    id: pane
    signal filterParametersAdopted(var parameters)
    property string sensor: "internal"
    property string signalKind: "Accelerometer"
    readonly property string mappingPrefix: sensor + (signalKind === "Gyroscope" ? "Gyro" : "")
    property var columns: []
    property var timeRequest: ({})
    property var filterPreview: ({})
    property var adoptedFilter: ({})
    property string errorText: ""
    property var selection: rawAvailable.checked ? [rawX.currentText,rawY.currentText,rawZ.currentText] : []
    clip: true
    contentWidth: availableWidth
    contentHeight: mappingContent.implicitHeight
    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
    ScrollBar.vertical.policy: ScrollBar.AlwaysOn

    function invalidate() { filterPreview = ({}); adoptedFilter = ({}); errorText = "" }
    function prefillParameters(parameters) {
        if (adoptedFilter.source_mode) return
        if (editor.prefillIfEmpty(parameters)) invalidate()
    }
    function setColumn(box, value) { box.currentIndex = box.model.indexOf(value || "") }
    function load(value, proposed) {
        value = value || ({})
        let raw = value.raw_columns || proposed || []
        let filtered = value.filtered_columns || []
        rawAvailable.checked = raw.length === 3
        existing.checked = value.mode === "already_filtered"
        software.checked = value.mode === "application_filtered"
        setColumn(rawX, raw[0]); setColumn(rawY, raw[1]); setColumn(rawZ, raw[2])
        setColumn(filteredX, filtered[0]); setColumn(filteredY, filtered[1]); setColumn(filteredZ, filtered[2])
        editor.loadSettings(value.settings || ({}))
        invalidate()
        if (software.checked && value.settings) adoptedFilter = value.settings
    }
    function draft() {
        return {mode:existing.checked ? "already_filtered" : software.checked ? "application_filtered" : "raw",
            raw_columns:rawAvailable.checked ? [rawX.currentText,rawY.currentText,rawZ.currentText] : [],
            filtered_columns:existing.checked ? [filteredX.currentText,filteredY.currentText,filteredZ.currentText] : [],
            settings:software.checked ? adoptedFilter : null}
    }
    function validate() {
        errorText = ""
        let d = draft()
        for (let values of [d.raw_columns,d.filtered_columns]) {
            if (values.length && (values.indexOf("") >= 0 || new Set(values).size !== 3)) {
                errorText = "Map three distinct columns for each enabled XYZ group"
                return false
            }
        }
        if (software.checked && !adoptedFilter.source_mode) {
            errorText = "Calculate the filter and adopt the design before continuing"
            return false
        }
        return true
    }
    function preview() {
        let request = Object.assign({}, timeRequest, {sensor:sensor,columns:selection,
            source_mode:"application_filtered",warmup_samples:editor.warmupSamples,stages:editor.stageSpecifications()})
        adoptedFilter = ({})
        filterPreview = studio.previewSingleImuMapping(request)
        errorText = filterPreview.ok ? "" : filterPreview.error
    }

    ColumnLayout {
        id: mappingContent
        width: pane.availableWidth
        height: implicitHeight
        spacing: 8
        Label { text:"Map " + pane.sensor + " " + pane.signalKind; font.pixelSize:20; font.bold:true }
        Label { text:"Map available XYZ signals here. Choose algorithms and their sources in Training."; Layout.fillWidth:true; wrapMode:Text.Wrap }
        CheckBox {
            id:rawAvailable; objectName:pane.mappingPrefix + "RawAvailable"; text:"Raw " + pane.signalKind + " XYZ available"
            onClicked:{ if (!checked) software.checked = false; pane.invalidate() }
        }
        GridLayout {
            visible:rawAvailable.checked; columns:2; Layout.fillWidth:true
            Label { text:"Raw X" }
            ComboBox { id:rawX; objectName:pane.mappingPrefix + "RawX"; Layout.fillWidth:true; model:[""].concat(pane.columns); onActivated:pane.invalidate() }
            Label { text:"Raw Y" }
            ComboBox { id:rawY; objectName:pane.mappingPrefix + "RawY"; Layout.fillWidth:true; model:[""].concat(pane.columns); onActivated:pane.invalidate() }
            Label { text:"Raw Z" }
            ComboBox { id:rawZ; objectName:pane.mappingPrefix + "RawZ"; Layout.fillWidth:true; model:[""].concat(pane.columns); onActivated:pane.invalidate() }
        }
        CheckBox {
            id:existing; objectName:pane.mappingPrefix + "ExistingFiltered"; text:"Existing filtered XYZ in this file"
            onClicked:{ if (checked) software.checked = false; pane.invalidate() }
        }
        GridLayout {
            visible:existing.checked; columns:2; Layout.fillWidth:true
            Label { text:"Filtered X" }
            ComboBox { id:filteredX; objectName:pane.mappingPrefix + "FilteredX"; Layout.fillWidth:true; model:[""].concat(pane.columns); onActivated:pane.invalidate() }
            Label { text:"Filtered Y" }
            ComboBox { id:filteredY; objectName:pane.mappingPrefix + "FilteredY"; Layout.fillWidth:true; model:[""].concat(pane.columns); onActivated:pane.invalidate() }
            Label { text:"Filtered Z" }
            ComboBox { id:filteredZ; objectName:pane.mappingPrefix + "FilteredZ"; Layout.fillWidth:true; model:[""].concat(pane.columns); onActivated:pane.invalidate() }
        }
        CheckBox {
            id:software; objectName:pane.mappingPrefix + "SoftwareFilter"; text:"Enable software filtering of raw XYZ"; enabled:rawAvailable.checked
            onClicked:{ if (checked) existing.checked = false; pane.invalidate() }
        }
        Label { visible:!existing.checked && !software.checked; text:"No filtering: only raw XYZ can be selected for this IMU."; Layout.fillWidth:true; wrapMode:Text.Wrap }
        SingleImuFilters {
            id:editor; visible:software.checked; forceApplicationFiltering:true
            Layout.fillWidth:true
            onEdited:pane.invalidate()
        }
        Label {
            visible:!!pane.filterPreview.ok; Layout.fillWidth:true; wrapMode:Text.Wrap
            text:pane.filterPreview.ok ? "Stage orders: " + pane.filterPreview.orders.join(", ") + " · Total order: " + pane.filterPreview.total_order + " · Warmup: " + Number(pane.filterPreview.warmup_seconds).toFixed(4) + " s" : ""
        }
        Label {
            visible:!!pane.filterPreview.ok; Layout.fillWidth:true; wrapMode:Text.Wrap
            text:(pane.filterPreview.cascade_response || []).map(function(r) { return "Stage " + r.stage + ": pass amplitude " + Number(r.passband_min_amplitude).toPrecision(4) + " (min " + Number(r.passband_required_min).toPrecision(4) + "), stop " + Number(r.stopband_max_amplitude).toPrecision(4) + " (max " + Number(r.stopband_required_max).toPrecision(4) + ")" }).join("\n")
        }
        Item {
            visible:software.checked
            implicitWidth:Math.ceil(Math.max(filterAction.implicitWidth, adoptedLabel.implicitWidth))
            implicitHeight:Math.ceil(Math.max(DesignTokens.buttonHeight,
                filterAction.contentItem.implicitHeight + filterAction.topPadding + filterAction.bottomPadding,
                adoptedLabel.implicitHeight))
            Layout.minimumWidth:implicitWidth
            Layout.preferredWidth:implicitWidth
            Layout.minimumHeight:implicitHeight
            Layout.preferredHeight:implicitHeight
            PaddedButton {
                id:filterAction; objectName:pane.mappingPrefix + "FilterDesignAction"
                anchors.fill:parent
                visible:!pane.adoptedFilter.source_mode
                enabled:visible
                text:pane.filterPreview.ok ? "Adopt design" : "Calculate filter"
                onClicked: {
                    if (pane.filterPreview.ok) {
                        pane.adoptedFilter = pane.filterPreview.settings
                        pane.errorText = ""
                        pane.filterParametersAdopted(editor.parameterSettings())
                    }
                    else pane.preview()
                }
            }
            Label {
                id:adoptedLabel; objectName:pane.mappingPrefix + "FilterDesignAdopted"
                anchors.fill:parent
                visible:!!pane.adoptedFilter.source_mode
                text:"Design adopted"; color:DesignTokens.success
                leftPadding:DesignTokens.buttonHorizontalPadding
                rightPadding:DesignTokens.buttonHorizontalPadding
                verticalAlignment:Text.AlignVCenter
            }
        }
        Label { text:pane.errorText; visible:text.length>0; color:DesignTokens.warning; Layout.fillWidth:true; wrapMode:Text.Wrap }
    }
}
