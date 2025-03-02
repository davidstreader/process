# import sys
# from PyQt5.QtWidgets import QApplication
# from ui.main_window import MainWindow  # Use MainWindow instead of TextEditorWindow
# from ui.settings_window import LayoutSettingsWindow

# import sys
# from PyQt5.QtWidgets import QApplication
# from ui.editor_window import TextEditorWindow
# from ui.petri_net_window import PetriNetWindow
# from ui.settings_window import LayoutSettingsWindow
# from models.file_manager import FileManager
# from models.parser import ProcessAlgebraParser


import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.settings_window import LayoutSettingsWindow
from models.file_manager import FileManager

def main():
    # Create the application
    app = QApplication(sys.argv)
    
    # Create the main window
    main_window = MainWindow()
    
    # Create settings window
    settings_window = LayoutSettingsWindow()
    
    # Connect settings window to main window
    settings_window.parameter_changed.connect(main_window.layout_algorithm.set_parameters)
    
    # Connect the settings button in main window
    main_window.settings_button.clicked.connect(settings_window.show)
    
    # Show the main window
    main_window.show()
    
    # Start the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
# Fix for main.py - ensure proper connections between windows

# def main():
#     # Create the application
#     app = QApplication(sys.argv)
    
#     # Create the windows
#     text_editor = TextEditorWindow()
#     petri_net_window = PetriNetWindow()
#     settings_window = LayoutSettingsWindow()
    
#     # Create file manager and ensure it's shared
#     file_manager = FileManager()
#     text_editor.file_manager = file_manager
#     petri_net_window.file_manager = file_manager
    
#     # Ensure parser is shared
#     text_editor.parser = ProcessAlgebraParser()
#     petri_net_window.parser = text_editor.parser
    
#     # Connect the visualize button to update the Petri net
#     text_editor.setup_connections(petri_net_window, settings_window)
    
#     # Connect settings window to petri net window
#     settings_window.parameter_changed.connect(petri_net_window.update_layout_parameters)
    
#     # Connect the settings button in petri net window
#     petri_net_window.settings_button.clicked.connect(settings_window.show)
    
#     # Connect selector window signals to petri net window
#     petri_net_window.selector_window.net_selected.connect(petri_net_window.on_petri_net_selected)
    
#     # Connect clear button to also reset the visualization
#     text_editor.clear_button.clicked.connect(lambda: petri_net_window.scene.clear())
    
#     # Connect visualize button directly
#     text_editor.visualize_button.clicked.connect(lambda: visualize_current_text(text_editor, petri_net_window))
    
#     # Show the main window
#     text_editor.show()
    
#     # Start the application
#     sys.exit(app.exec_())

def visualize_current_text(text_editor, petri_net_window):
    """Helper function to visualize the current text in the editor"""
    # Get the current text
    text = text_editor.text_edit.toPlainText()
    
    if not text.strip():
        QMessageBox.information(text_editor, "Empty Input", "Please enter a process algebra expression first.")
        return
    
    # Parse the text (ensure we're using the same parser instance)
    success = text_editor.parser.parse(text)
    
    if success:
        # Update the Petri net window directly
        petri_net_window.update_petri_net(text_editor.parser)
        petri_net_window.show()
        petri_net_window.raise_()
    else:
        # Show parsing errors
        errors = text_editor.parser.get_parsing_errors()
        error_message = "Unable to parse the process algebra expression:\n\n"
        for error in errors:
            error_message += f"• {error}\n"
        
        QMessageBox.warning(text_editor, "Parsing Error", error_message)


# def main():
#     # Create the application
#     app = QApplication(sys.argv)
    
#     # Create the windows
#     main_window = MainWindow()  # Create MainWindow instead of TextEditorWindow
#     settings_window = LayoutSettingsWindow()
    
#     # Connect settings window to main window
#     settings_window.parameter_changed.connect(main_window.update_layout_parameters)
    
#     # Connect the settings button in main window
#     main_window.settings_button.clicked.connect(settings_window.show)
    
#     # Show the main window
#     main_window.show()
    
#     # Start the application
#     sys.exit(app.exec_())

if __name__ == "__main__":
    main()