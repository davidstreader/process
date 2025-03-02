# ui/editor_window.py

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTextEdit, QPushButton, 
                           QLabel, QMessageBox, QFileDialog, QMenu, QAction,
                           QListWidget, QListWidgetItem, QDialog, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import os
import json
from models.parser import ProcessAlgebraParser
from models.file_manager import FileManager
from ui.petri_net_selector import PetriNetSelectorWindow

class SaveDialog(QDialog):
    """Dialog for saving Petri nets with a name"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save Petri Net")
        self.resize(300, 100)
        
        layout = QVBoxLayout(self)
        
        # Add name label and text field
        layout.addWidget(QLabel("Enter name for Petri net:"))
        self.name_edit = QTextEdit()
        self.name_edit.setPlaceholderText("Enter name...")
        self.name_edit.setMaximumHeight(50)
        layout.addWidget(self.name_edit)
        
        # Add buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        # Connect signals
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
    
    def get_name(self):
        """Get the entered name"""
        return self.name_edit.toPlainText().strip()

class LoadDialog(QDialog):
    """Dialog for loading Petri nets"""
    
    def __init__(self, nets, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Load Petri Net")
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Add title
        layout.addWidget(QLabel("Select a Petri net to load:"))
        
        # Add list widget
        self.list_widget = QListWidget()
        for net in nets:
            item = QListWidgetItem(net['name'])
            item.setData(Qt.UserRole, net['path'])
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)
        
        # Add buttons
        button_layout = QHBoxLayout()
        self.load_button = QPushButton("Load")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        # Connect signals
        self.load_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.list_widget.itemDoubleClicked.connect(self.accept)
    
    def get_selected_path(self):
        """Get the selected Petri net path"""
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            return selected_items[0].data(Qt.UserRole)
        return None

class TextEditorWindow(QMainWindow):
    """Window for entering process algebra text"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Process Algebra Editor")
        self.resize(500, 600)
        
        # Create file manager
        self.file_manager = FileManager()
        
        # Create main widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # Create text editor
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Enter process algebra expressions here...\nExample:\nP = a.b + c.d\nQ = e.f.P")
        layout.addWidget(QLabel("<b>Process Algebra Editor</b>"))
        layout.addWidget(self.text_edit)
        
        # Create buttons for visualization
        button_layout = QHBoxLayout()
        self.visualize_button = QPushButton("Visualize Petri Net")
        self.clear_button = QPushButton("Clear")
        button_layout.addWidget(self.visualize_button)
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)
        
        # Create file operation buttons
        file_button_layout = QHBoxLayout()
        self.load_button = QPushButton("Load")
        self.save_button = QPushButton("Save")
        self.example_button = QPushButton("Load Example")
        file_button_layout.addWidget(self.load_button)
        file_button_layout.addWidget(self.save_button)
        file_button_layout.addWidget(self.example_button)
        layout.addLayout(file_button_layout)
        
        self.setCentralWidget(main_widget)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Connect signals
        self.clear_button.clicked.connect(self.text_edit.clear)
        self.example_button.clicked.connect(self.load_example)
        self.load_button.clicked.connect(self.open_load_dialog)
        self.save_button.clicked.connect(self.open_save_dialog)
        
        # Set up the parser
        self.parser = ProcessAlgebraParser()
        
        # References to other windows (will be set by setup_connections)
        self.petri_net_window = None
        self.settings_window = None
        
        # Check for last net and try to load it
        self.load_last_net()
    

    def open_load_dialog(self):
        """Open dialog to load a Petri net"""
        # Get available nets
        nets = self.file_manager.get_available_nets()
        
        if not nets:
            QMessageBox.information(self, "No Nets", "No saved Petri nets found.")
            return
        
        # Open load dialog
        dialog = LoadDialog(nets, self)
        if dialog.exec_() == QDialog.Accepted:
            path = dialog.get_selected_path()
            if path:
                self.load_petri_net_from_file(path)

    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # New action
        new_action = QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.text_edit.clear)
        file_menu.addAction(new_action)
        
        # Load action
        load_action = QAction('Load...', self)
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.open_load_dialog)
        file_menu.addAction(load_action)
        
        # Save action
        save_action = QAction('Save...', self)
        save_action.setShortcut('Ctrl+S')
        #
        # 
        #save_action.triggered.connect(self.open_save_dialog(self))
        save_action.triggered.connect(self.open_save_dialog)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Petri Net menu
        petri_menu = menubar.addMenu('Petri Net')
        
        # Visualize action
        visualize_action = QAction('Visualize', self)
        visualize_action.setShortcut('F5')
        visualize_action.triggered.connect(self.show_petri_net_selector)  # Updated to use selector
        petri_menu.addAction(visualize_action)
        
        # Load example action
        example_action = QAction('Load Example', self)
        example_action.triggered.connect(self.load_example)
        petri_menu.addAction(example_action)
    
    
        
    def load_example(self):
        """Load an example process algebra expression"""
        example = """# Simple Process Algebra Example with Brackets
    Process = (action.behavior).Process + choice.(done.STOP)
    Query = event.(Process) + (function.going).Query
    Main = (Process) | (Query)"""
        self.text_edit.setText(example)    

    def open_save_dialog(self):
        """Open dialog to save current Petri net"""
        # Ensure there's a Petri net to save
        if not self.parser.places and not self.parser.transitions:
            QMessageBox.warning(self, "Save Error", "No Petri net to save. Please visualize a valid process algebra expression first.")
            return
        
        # Open save dialog
        dialog = SaveDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name = dialog.get_name()
            if name:
                try:
                    path = self.file_manager.save_petri_net(self.parser, name)
                    QMessageBox.information(self, "Save Successful", f"Petri net saved as '{name}'")
                except Exception as e:
                    QMessageBox.critical(self, "Save Error", f"Error saving Petri net: {str(e)}")
            else:
                QMessageBox.warning(self, "Save Error", "Please enter a name for the Petri net.")

    
    def setup_connections(self, petri_net_window, settings_window):
        """Set up connections to other windows"""
        self.petri_net_window = petri_net_window
        self.settings_window = settings_window
        
        # Connect the visualize button to show the selector instead of directly visualizing
        self.visualize_button.clicked.connect(self.show_petri_net_selector) 
    #####
  # Locate this method in ui/editor_window.py and replace it with this fixed version
        
        ####
        # Calls the parser that builds the Petri nets
    def show_petri_net_selector(self):
        """Show the Petri net selector when the visualize button is clicked"""
        # Get the current text from the editor
        text = self.text_edit.toPlainText()
        
        if text.strip():
            # First try to parse the text to get process definitions
            success = self.parser.parse(text)
            
            if not success:
                # Get parsing errors
                errors = self.parser.get_parsing_errors()
                error_message = "Unable to parse the process algebra expression:\n\n"
                for error in errors:
                    error_message += f"• {error}\n"
                
                QMessageBox.warning(self, "Parsing Error", error_message)
                return
            
            # Successful parse - ensure parser is shared with both windows
            self.petri_net_window.parser = self.parser
            self.petri_net_window.selector_window.parser = self.parser
            
            # Load the parser definitions into the selector
            self.petri_net_window.selector_window.load_parser_definitions()
            
            # Add the current editor content as a custom net
            self.petri_net_window.selector_window.add_custom_net(
                name="Current Editor Content",
                description=text if len(text) < 100 else text[:97] + "...",
                expression=text
            )

            # Connect the net_selected signal if not already connected
            if not self.petri_net_window.selector_window.net_selected.receivers(self.petri_net_window.on_petri_net_selected):
                self.petri_net_window.selector_window.net_selected.connect(self.petri_net_window.on_petri_net_selected)

            # Show the selector
            self.petri_net_window.selector_window.show_selector()
        else:
            QMessageBox.information(self, "Empty Input", "Please enter a process algebra expression first.")   
        
            
            def open_load_dialog(self):
                """Open dialog to load a Petri net"""
                # Get available nets
                nets = self.file_manager.get_available_nets()
                
                if not nets:
                    QMessageBox.information(self, "No Nets", "No saved Petri nets found.")
                    return
                
                # Open load dialog
                dialog = LoadDialog(nets, self)
                if dialog.exec_() == QDialog.Accepted:
                    path = dialog.get_selected_path()
                    if path:
                        self.load_petri_net_from_file(path)


    def load_petri_net_from_file(self, file_path):
        """Load a Petri net from a file"""
        data = self.file_manager.load_petri_net(file_path)
        if data:
            try:
                # Update parser with loaded data
                self.parser.reset()
                self.parser.places = data['places']
                self.parser.transitions = data['transitions']
                self.parser.arcs = data['arcs']
                
                # Load parse tree if available
                if 'parse_tree' in data:
                    # Load process definitions - prioritize expanded if available
                    if 'expanded_definitions' in data['parse_tree']:
                        self.parser.process_definitions = data['parse_tree']['expanded_definitions']
                    else:
                        self.parser.process_definitions = data['parse_tree'].get('process_definitions', {})
                    
                    self.parser.process_places = data['parse_tree'].get('process_places', {})
                    self.parser.current_id = data['parse_tree'].get('current_id', len(self.parser.places) + len(self.parser.transitions))
                else:
                    # Set correct current_id
                    max_place_id = max([p['id'] for p in self.parser.places]) if self.parser.places else -1
                    max_trans_id = max([t['id'] for t in self.parser.transitions]) if self.parser.transitions else -1
                    self.parser.current_id = max(max_place_id, max_trans_id) + 1
                
                # Update the Petri net window
                if self.petri_net_window:
                    self.petri_net_window.update_petri_net(self.parser, file_path)
                    self.petri_net_window.show()
                    self.petri_net_window.raise_()
                
                # Show success message
                QMessageBox.information(self, "Load Successful", f"Petri net loaded from '{os.path.basename(file_path)}'")
                
                # Set the source code in the editor if available
                if 'source_code' in data and data['source_code']:
                    self.text_edit.setText(data['source_code'])
                else:
                    # Try to generate process algebra code from the Petri net
                    try:
                        process_algebra_code = self.parser.export_to_process_algebra()
                        if process_algebra_code:
                            self.text_edit.setText(process_algebra_code)
                    except Exception as e:
                        print(f"Error generating process algebra code: {str(e)}")
                
            except Exception as e:
                QMessageBox.critical(self, "Load Error", f"Error loading Petri net: {str(e)}")
        else:
            QMessageBox.critical(self, "Load Error", f"Could not load Petri net from '{file_path}'")

                
         
    def load_last_net(self):
         """Try to load the last opened Petri net"""
         last_net = self.file_manager.get_last_net()
         if last_net:
             self.load_petri_net_from_file(last_net)