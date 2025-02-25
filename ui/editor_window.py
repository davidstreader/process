from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTextEdit, QPushButton, 
                           QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from models.parser import ProcessAlgebraParser

class TextEditorWindow(QMainWindow):
    """Window for entering process algebra text"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Process Algebra Editor")
        self.resize(500, 600)
        
        # Create main widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # Create text editor
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Enter process algebra expressions here...\nExample:\nP = a.b + c.d\nQ = e.f.P")
        layout.addWidget(QLabel("<b>Process Algebra Editor</b>"))
        layout.addWidget(self.text_edit)
        
        # Create buttons
        button_layout = QHBoxLayout()
        self.visualize_button = QPushButton("Visualize Petri Net")
        self.clear_button = QPushButton("Clear")
        button_layout.addWidget(self.visualize_button)
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)
        
        # Add example button
        self.example_button = QPushButton("Load Example")
        layout.addWidget(self.example_button)
        
        self.setCentralWidget(main_widget)
        
        # Connect signals
        self.clear_button.clicked.connect(self.text_edit.clear)
        self.example_button.clicked.connect(self.load_example)
        
        # Set up the parser
        self.parser = ProcessAlgebraParser()
        
        # References to other windows (will be set by setup_connections)
        self.petri_net_window = None
        self.settings_window = None
    
    def load_example(self):
        """Load an example process algebra expression"""
        example = """# Simple Process Algebra Example
P = a.b.P + c.d.STOP
Q = e.P + f.g.Q
MAIN = P | Q"""
        self.text_edit.setText(example)
    
    def setup_connections(self, petri_net_window, settings_window):
        """Set up connections to other windows"""
        self.petri_net_window = petri_net_window
        self.settings_window = settings_window
        
        # Connect the visualize button to update the Petri net
        self.visualize_button.clicked.connect(self.visualize_petri_net)
    
    def visualize_petri_net(self):
        """Parse the text and visualize the Petri net"""
        text = self.text_edit.toPlainText()
        if text.strip():
            success = self.parser.parse(text)
            if success:
                self.petri_net_window.update_petri_net(self.parser)
                # Make sure Petri net window is visible
                self.petri_net_window.show()
                self.petri_net_window.raise_()
            else:
                QMessageBox.warning(self, "Parsing Error", 
                                   "Could not parse the process algebra expression. Check syntax.")
