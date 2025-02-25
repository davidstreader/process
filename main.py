import sys
from PyQt5.QtWidgets import QApplication
from ui.editor_window import TextEditorWindow
from ui.petri_net_window import PetriNetWindow
from ui.settings_window import LayoutSettingsWindow
from models.file_manager import FileManager

def main():
    # Create the application
    app = QApplication(sys.argv)
    
    # Create the windows
    text_editor = TextEditorWindow()
    petri_net_window = PetriNetWindow()
    settings_window = LayoutSettingsWindow()
    
    # Connect the visualize button to update the Petri net
    text_editor.setup_connections(petri_net_window, settings_window)
    
    # Connect settings window to petri net window
    settings_window.parameter_changed.connect(petri_net_window.update_layout_parameters)
    
    # Connect the settings button in petri net window
    petri_net_window.settings_button.clicked.connect(settings_window.show)
    
    # Show the main window
    text_editor.show()
    
    # Start the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
