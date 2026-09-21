import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "."

ColumnLayout {
    id: pane
    signal edited()
    property bool forceApplicationFiltering: false
    property bool alreadyFiltered: !forceApplicationFiltering && sourceChoice.currentIndex === 0
    property double warmupSamples: Number(warmup.text)

    property int templateIndex: -1

    function singleEdge(kind) { return kind === "highpass" || kind === "lowpass" }
    function inferredKind(passband, stopband) {
        let p = Number(passband), s = Number(stopband)
        if (!isFinite(p) || !isFinite(s) || p <= 0 || s <= 0 || p === s) return ""
        return p > s ? "highpass" : "lowpass"
    }
    function addStage() {
        let i = templateIndex >= 0 && templateIndex < stages.count ? templateIndex : stages.count - 1
        let s = i >= 0 ? stages.get(i) : {kind:"highpass",fp1:"",fp2:"",fs1:"",fs2:"",rp:"",amplitude:""}
        // Copy scalar roles: the new stage must never alias the template row.
        stages.append({kind:s.kind,fp1:s.fp1,fp2:s.fp2,fs1:s.fs1,fs2:s.fs2,rp:s.rp,amplitude:s.amplitude})
        templateIndex = stages.count - 1
        edited()
    }
    function removeStage(i) {
        let previous = templateIndex
        stages.remove(i)
        templateIndex = previous === i ? stages.count - 1 : previous > i ? previous - 1 : previous
        edited()
    }
    function moveStage(from, to) {
        let previous = templateIndex
        stages.move(from, to, 1)
        templateIndex = previous === from ? to : previous === to ? from : previous
        edited()
    }
    function editStage(i, role, value) {
        templateIndex = i
        stages.setProperty(i, role, value)
        edited()
    }
    function stageSpecifications() {
        let result = []
        if (alreadyFiltered) return result
        for (let i = 0; i < stages.count; ++i) {
            let s = stages.get(i)
            result.push({kind:singleEdge(s.kind) ? (inferredKind(s.fp1, s.fs1) || "highpass") : s.kind,
                passband_hz:singleEdge(s.kind) ? [Number(s.fp1)] : [Number(s.fp1),Number(s.fp2)],
                stopband_hz:singleEdge(s.kind) ? [Number(s.fs1)] : [Number(s.fs1),Number(s.fs2)],
                passband_attenuation_ratio:Number(s.rp), stopband_amplitude_ratio:Number(s.amplitude)})
        }
        return result
    }
    function parameterSettings() {
        return {source_mode:"application_filtered",warmup_samples:warmupSamples,filters:stageSpecifications()}
    }
    function prefillIfEmpty(settings) {
        if (!settings || !settings.filters || !settings.filters.length || Number(warmup.text) !== 500) return false
        for (let i = 0; i < stages.count; ++i) {
            let s = stages.get(i)
            if (s.kind !== "highpass" || [s.fp1,s.fp2,s.fs1,s.fs2,s.rp,s.amplitude].some(function(v) { return String(v).trim().length > 0 })) return false
        }
        loadSettings(settings)
        return true
    }
    function loadSettings(settings) {
        templateIndex = -1
        stages.clear()
        sourceChoice.currentIndex = settings.source_mode === "application_filtered" ? 1 : 0
        warmup.text = String(settings.warmup_samples || 500)
        for (let d of (settings.filters || [])) {
            stages.append({kind:d.kind,fp1:String(d.passband_hz[0]),fp2:String(d.passband_hz[1] || ""),
                fs1:String(d.stopband_hz[0]),fs2:String(d.stopband_hz[1] || ""),rp:String(d.passband_attenuation_ratio),amplitude:String(d.stopband_amplitude_ratio)})
        }
        templateIndex = stages.count - 1
    }
    spacing: 8
    Label { text:"Filter design"; font.bold:true; font.pixelSize:18 }
    ComboBox {
        id:sourceChoice; objectName:"singleImuSourceMode"; visible:!pane.forceApplicationFiltering
        Layout.fillWidth:true
        model:["Use existing filtered XYZ columns", "Filter the selected raw Accel XYZ"]
        onActivated:pane.edited()
    }
    Label {
        visible:pane.alreadyFiltered; Layout.fillWidth:true; wrapMode:Text.Wrap
        text:"The selected values are used directly. No additional filter or warmup is applied; prediction still requires enough past samples."
    }
    RowLayout {
        visible:!pane.alreadyFiltered
        Label { text:"Warmup length" }
        TextField {
            id:warmup; objectName:"singleImuWarmup"; text:"500"; Layout.preferredWidth:110
            validator:IntValidator { bottom:1 }
            onTextEdited:pane.edited()
        }
        Label { text:"samples" }
        Item { Layout.fillWidth:true }
        PaddedButton {
            objectName:"addFilter"; text:"Add filter"
            onClicked:pane.addStage()
        }
    }
    ListModel { id:stages }
    ColumnLayout {
        visible:!pane.alreadyFiltered
        Layout.fillWidth:true
        spacing:8
        Repeater {
            model:stages
            delegate:Frame {
                id:stageCard
                property int stageIndex:index
                property bool isSingleEdge:pane.singleEdge(kind)
                Layout.fillWidth:true
                contentItem: ColumnLayout {
                    RowLayout {
                        Label { text:"Stage " + (index+1); font.bold:true }
                        ComboBox {
                            objectName:"filterKind" + index
                            model:["High / Low pass","bandpass","bandstop"]
                            currentIndex:stageCard.isSingleEdge ? 0 : model.indexOf(kind)
                            onActiveFocusChanged:if (activeFocus) pane.templateIndex = stageCard.stageIndex
                            onActivated:pane.editStage(stageCard.stageIndex,"kind",currentIndex === 0 ? "highpass" : currentText)
                        }
                        Item { Layout.fillWidth:true }
                        PaddedButton { objectName:"filterUp" + index; text:"↑"; enabled:index>0; onClicked:pane.moveStage(stageCard.stageIndex,stageCard.stageIndex-1) }
                        PaddedButton { objectName:"filterDown" + index; text:"↓"; enabled:index<stages.count-1; onClicked:pane.moveStage(stageCard.stageIndex,stageCard.stageIndex+1) }
                        PaddedButton { objectName:"filterRemove" + index; text:"Remove"; onClicked:pane.removeStage(stageCard.stageIndex) }
                    }
                    Label {
                        objectName:"filterDirection" + index
                        visible:stageCard.isSingleEdge
                        Layout.fillWidth:true; wrapMode:Text.Wrap
                        text: {
                            let direction = pane.inferredKind(fp1, fs1)
                            return direction === "highpass" ? "High pass" : direction === "lowpass" ? "Low pass" : "Enter distinct positive passband and stopband frequencies"
                        }
                    }
                    GridLayout {
                        columns:4; Layout.fillWidth:true
                        Label { text:stageCard.isSingleEdge ? "Passband edge (Hz)" : "Passband lower (Hz)" }
                        TextField { implicitWidth:100; Layout.minimumWidth:60; objectName:"filterPassband" + index; text:fp1; onActiveFocusChanged:if (activeFocus) pane.templateIndex = stageCard.stageIndex; Layout.fillWidth:true; onTextEdited:pane.editStage(stageCard.stageIndex,"fp1",text) }
                        Label { text:"Passband upper (Hz)"; visible:!stageCard.isSingleEdge }
                        TextField { implicitWidth:100; Layout.minimumWidth:60; objectName:"filterPassbandUpper" + index; text:fp2; onActiveFocusChanged:if (activeFocus) pane.templateIndex = stageCard.stageIndex; visible:!stageCard.isSingleEdge; Layout.fillWidth:true; onTextEdited:pane.editStage(stageCard.stageIndex,"fp2",text) }
                        Label { text:stageCard.isSingleEdge ? "Stopband edge (Hz)" : "Stopband lower (Hz)" }
                        TextField { implicitWidth:100; Layout.minimumWidth:60; objectName:"filterStopband" + index; text:fs1; onActiveFocusChanged:if (activeFocus) pane.templateIndex = stageCard.stageIndex; Layout.fillWidth:true; onTextEdited:pane.editStage(stageCard.stageIndex,"fs1",text) }
                        Label { text:"Stopband upper (Hz)"; visible:!stageCard.isSingleEdge }
                        TextField { implicitWidth:100; Layout.minimumWidth:60; objectName:"filterStopbandUpper" + index; text:fs2; onActiveFocusChanged:if (activeFocus) pane.templateIndex = stageCard.stageIndex; visible:!stageCard.isSingleEdge; Layout.fillWidth:true; onTextEdited:pane.editStage(stageCard.stageIndex,"fs2",text) }
                        Label { text:"Max passband attenuation ratio"; Layout.maximumWidth:170; wrapMode:Text.Wrap }
                        TextField { implicitWidth:100; Layout.minimumWidth:60; objectName:"filterAttenuation" + index; text:rp; onActiveFocusChanged:if (activeFocus) pane.templateIndex = stageCard.stageIndex; placeholderText:"e.g. 1.3"; Layout.fillWidth:true; onTextEdited:pane.editStage(stageCard.stageIndex,"rp",text) }
                        Label { text:"Max stopband amplitude ratio"; Layout.maximumWidth:170; wrapMode:Text.Wrap }
                        TextField { implicitWidth:100; Layout.minimumWidth:60; objectName:"filterAmplitude" + index; text:amplitude; onActiveFocusChanged:if (activeFocus) pane.templateIndex = stageCard.stageIndex; placeholderText:"e.g. 0.3"; Layout.fillWidth:true; onTextEdited:pane.editStage(stageCard.stageIndex,"amplitude",text) }
                    }
                }
            }
        }
    }

    Item { visible:pane.alreadyFiltered; Layout.fillHeight:true }
}
