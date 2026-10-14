import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "."

ColumnLayout {
    id: pane
    property string sensor: "internal"
    property var columns: []
    property var timeRequest: ({})
    property string errorText: ""
    signal filterParametersAdopted(var parameters)
    function invalidate() { acceleration.invalidate(); gyroscope.invalidate(); errorText = "" }
    function prefillParameters(parameters) { acceleration.prefillParameters(parameters); gyroscope.prefillParameters(parameters) }
    function load(value, proposed) {
        value = value || ({})
        accelerationSelected.checked = value.accelerometer_enabled !== false
        gyroscopeSelected.checked = !!value.gyroscope
        acceleration.load(value, proposed)
        gyroscope.load(value.gyroscope || ({}), ["", "", ""])
        groupSelector.currentIndex = 0
        errorText = ""
    }
    function draft() {
        let value = accelerationSelected.checked ? acceleration.draft() : {mode:"raw",raw_columns:[],filtered_columns:[],settings:null}
        value.accelerometer_enabled = accelerationSelected.checked
        value.gyroscope = gyroscopeSelected.checked ? gyroscope.draft() : null
        return value
    }
    function validate() {
        errorText = ""
        for (let group of [accelerationSelected.checked ? acceleration : null, gyroscopeSelected.checked ? gyroscope : null]) {
            if (!group) continue
            if (!group.validate()) { errorText = group.errorText; return false }
            let value = group.draft()
            if (!value.raw_columns.length && !value.filtered_columns.length) {
                errorText = "Map a complete XYZ group for each selected signal"
                return false
            }
        }
        return true
    }
    RowLayout {
        CheckBox { id: accelerationSelected; objectName:pane.sensor + "AccelerometerSelected"; text:"Accelerometer"; checked:true; onClicked:pane.errorText = "" }
        CheckBox { id: gyroscopeSelected; objectName:pane.sensor + "GyroscopeSelected"; text:"Gyroscope"; checked:false; onClicked:pane.errorText = "" }
        Item { Layout.fillWidth:true }
        ComboBox {
            id:groupSelector; objectName:pane.sensor + "SignalGroup"
            model: accelerationSelected.checked ? (gyroscopeSelected.checked ? ["Accelerometer", "Gyroscope"] : ["Accelerometer"]) : (gyroscopeSelected.checked ? ["Gyroscope"] : [])
        }
    }
    StackLayout {
        Layout.fillWidth:true; Layout.fillHeight:true
        currentIndex:groupSelector.currentText === "Gyroscope" ? 1 : 0
        visible:accelerationSelected.checked || gyroscopeSelected.checked
        SensorMapping {
            id:acceleration; sensor:pane.sensor; columns:pane.columns; timeRequest:pane.timeRequest
            onErrorTextChanged: pane.errorText = acceleration.errorText
            onFilterParametersAdopted: parameters => pane.filterParametersAdopted(parameters)
        }
        SensorMapping {
            id:gyroscope; sensor:pane.sensor; signalKind:"Gyroscope"; columns:pane.columns; timeRequest:pane.timeRequest
            onErrorTextChanged: pane.errorText = gyroscope.errorText
            onFilterParametersAdopted: parameters => pane.filterParametersAdopted(parameters)
        }
    }
    Label { visible:!accelerationSelected.checked && !gyroscopeSelected.checked; text:"No signals selected for this IMU" }
}
