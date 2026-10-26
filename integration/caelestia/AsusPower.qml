pragma Singleton
pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import Quickshell.Io
import Quickshell.Services.UPower

Singleton {
    id: root
    signal batteryRequested(string output, bool open)
    property int profile: PowerProfile.Balanced
    property var state: ({})
    property string errorText: ""
    property string lastDisplayProfile: ""
    readonly property bool busy: setter.running
    readonly property int degradationReason: PerformanceDegradationReason.None
    readonly property string helper: Quickshell.env("HOME") + "/.local/bin/frost-power-preset"

    function setProfile(value: int): void {
        const preset = value === PowerProfile.PowerSaver ? "eco"
                     : value === PowerProfile.Performance ? "performance" : "balanced";
        if (!setter.running) {
            root.errorText = "";
            root.lastDisplayProfile = "";
            setter.command = [root.helper, "select", preset];
            setter.running = true;
        }
    }

    function refreshDisplay(): void {
        if (!displaySetter.running && root.state.profile && root.lastDisplayProfile !== root.state.profile) {
            root.lastDisplayProfile = root.state.profile;
            displaySetter.running = true;
        }
    }

    Process {
        id: reader
        running: true
        command: [root.helper, "status"]
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    const data = JSON.parse(text);
                    root.state = data;
                    root.profile = data.profile === "quiet" ? PowerProfile.PowerSaver
                                 : data.profile === "performance" ? PowerProfile.Performance : PowerProfile.Balanced;
                    root.refreshDisplay();
                } catch (e) { root.errorText = "Power preset status unavailable"; }
            }
        }
    }
    Process {
        id: setter
        stderr: StdioCollector { onStreamFinished: if (text.trim()) root.errorText = text.trim(); }
        onExited: (code, status) => {
            if (code !== 0 && !root.errorText) root.errorText = "Could not apply power preset";
            if (!reader.running) reader.running = true;
        }
    }
    Process {
        id: displaySetter
        command: [root.helper, "display"]
        stderr: StdioCollector { onStreamFinished: if (text.trim()) root.errorText = text.trim(); }
        onExited: (code, status) => { if (code === 0) root.refreshDisplay(); }
    }
    Timer {
        interval: 5000
        running: true
        repeat: true
        onTriggered: if (!reader.running) reader.running = true
    }
    IpcHandler {
        target: "asusPower"
        function openBattery(output: string): void { root.batteryRequested(output, true); }
        function closeBattery(output: string): void { root.batteryRequested(output, false); }
        function current(): string { return root.profile === PowerProfile.PowerSaver ? "Quiet" : root.profile === PowerProfile.Performance ? "Performance" : "Balanced"; }
        function status(): string { return JSON.stringify(root.state); }
        function select(preset: string): void {
            if (["eco", "balanced", "performance"].includes(preset))
                root.setProfile(preset === "eco" ? PowerProfile.PowerSaver : preset === "performance" ? PowerProfile.Performance : PowerProfile.Balanced);
        }
    }
}
