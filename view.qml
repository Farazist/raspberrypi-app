import QtQuick 2.10
import QtQuick.Controls 2.3
import QtQuick.VirtualKeyboard 2.1

Rectangle {
    width: 1280
    height: 720
    color: "#F6F6F6"

    // Only set with CONFIG+=disable-desktop.
    property bool handwritingInputPanelActive: false

    Flickable {
        id: flickable
        anchors.fill: parent
        contentWidth: content.width
        contentHeight: content.height
        interactive: contentHeight > height
        flickableDirection: Flickable.VerticalFlick

        property real scrollMarginVertical: 20

        ScrollBar.vertical: ScrollBar {}

        MouseArea  {
            id: content
            width: flickable.width
            height: textEditors.height + 24

            onClicked: focus = true

            Column {
                id: textEditors
                spacing: 15
                x: 12
                y: 12
                width: parent.width - 26

                Label {
                    color: "#565758"
                    text: "Tap fields to enter text"
                    anchors.horizontalCenter: parent.horizontalCenter
                    font.pixelSize: 22
                }
                TextField {
                    width: parent.width
                    placeholderText: "One line field"
                    onAccepted: passwordField.focus = true
                }
                TextField {
                    id: phoneNumberField
                    validator: RegExpValidator { regExp: /^[0-9\+\-\#\*\ ]{6,}$/ }
                    width: parent.width
                    placeholderText: "Phone number field"
                    inputMethodHints: Qt.ImhDialableCharactersOnly
                    onAccepted: formattedNumberField.focus = true
                }
                TextField {
                    id: digitsField
                    width: parent.width
                    placeholderText: "Digits only field"
                    inputMethodHints: Qt.ImhDigitsOnly
                    onAccepted: textArea.focus = true
                }
            }
        }
    }

    // Keyboard
    
    InputPanel {
        id: inputPanel
        z: 99
        x: 0
        y: parent.height
        width: parent.width

        Component.onCompleted: {
            keyboard.style.keyboardBackground = null;
            keyboard.style.selectionListBackground = null;
        }

        states: State {
            name: "visible"
            when: inputPanel.active
            PropertyChanges {
                target: inputPanel
                y: parent.height - inputPanel.height
            }
        }
        transitions: Transition {
            from: ""
            to: "visible"
            reversible: true
            ParallelAnimation {
                NumberAnimation {
                    properties: "y"
                    duration: 250
                    easing.type: Easing.InOutQuad
                }
            }
        }
    }
}
