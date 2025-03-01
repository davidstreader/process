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
    main_window.show_layout_settings = settings_window.show
    
    # Show the main window
    main_window.show()
    
    # Start the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()