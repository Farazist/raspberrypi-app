import QtQuick 2.10
import QtQuick.Controls 2.3
import QtQuick.VirtualKeyboard 2.1

Rectangle {
    width: 1350  
    height:700
    color: "#f6fdfa"

    // Only set with CONFIG+=disable-desktop.
    property bool handwritingInputPanelActive: false

    Flickable {
        id: flickableUser
        anchors.fill: parent
        contentWidth: contentUser.width
        contentHeight: contentUser.height
        interactive: contentHeight > height
        flickableDirection: Flickable.VerticalFlick

        property real scrollMarginVertical: 20

        ScrollBar.vertical: ScrollBar {}

        MouseArea  {
            id: contentUser
            width: flickableUser.width
            height: textEditorsUser.height + 24

            onClicked: focus = true

            Column {
                id: textEditorsUser
                spacing: 7
                x: 12
                y: 12
                width: parent.width - 26
                
                Label {
                    color: "#000000"
                    text: "نام کاربری"
                    anchors.horizontalCenter: parent.horizontalCenter
                    font.pixelSize: 22
                }
                
                TextField {
                    background: Rectangle {
                        radius: 10
                        border.color: "#1E5631"
                        border.width: 2
                    }
                    width: 300
                    height: 60
                    placeholderText: "09*********"
                    anchors.horizontalCenter: parent.horizontalCenter
                    inputMethodHints: Qt.ImhDialableCharactersOnly
                    onAccepted: passwordField.focus = true
                    font.pixelSize: 24
                }

                Label {
                    color: "#000000"
                    text: "رمز عبور"
                    anchors.horizontalCenter: parent.horizontalCenter
                    font.pixelSize: 22
                }
                
                TextField {
                    background: Rectangle {
                        radius: 10
                        border.color: "#1E5631"
                        border.width: 2
                    }
                    width: 300
                    height: 60
                    placeholderText: "**********"
                    anchors.horizontalCenter: parent.horizontalCenter
                    inputMethodHints: Qt.ImhDialableCharactersOnly
                    onAccepted: passwordField.focus = true
                    font.pixelSize: 24
                }
                Button {
                    background: Rectangle {
                        radius: 10
                        width: 300; height: 60
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: "#1E5631" }
                            GradientStop { position: 1.0; color: "#2ea444" }
                        }
                    }
                    text: "<font color='#ffffff'>  ورود  </font>"
                    //font.family: "Arial"
                    font.pointSize: 24
                    width: 300
                    height: 60
                    anchors.horizontalCenter: parent.horizontalCenter
                    font.pixelSize: 24
                    onClicked: {
                        buttonClickedUser.text = "clicked"
                    }
                }
                Label {
                    id: buttonClickedUser
                    color: "#ff0000"
                    anchors.horizontalCenter: parent.horizontalCenter
                    font.pixelSize: 22
                }
            }
        }
    }

    // Keyboard
    
    InputPanel {
        id: inputPanelUser
        z: 99
        x: 60
        y: parent.height
        width: parent.width - 120

        Component.onCompleted: {
            keyboard.style.keyboardBackground = null;
            keyboard.style.selectionListBackground = null;
        }

        states: State {
            name: "visible"
            when: inputPanelUser.active
            PropertyChanges {
                target: inputPanelUser
                y: parent.height - inputPanelUser.height - 120
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
