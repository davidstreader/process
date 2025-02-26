# Update ui/petri_net_selector.py

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, pyqtSignal
from models.parser import ProcessAlgebraParser

class PetriNetSelectorWindow(QMainWindow):
    """Window for selecting a Petri net to visualize"""
    
    # Signal emitted when a Petri net is selected
    net_selected = pyqtSignal(str)  # Signal passes the selected expression
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Petri Net")
        self.resize(400, 500)
        
        # Create main widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # Add title label
        title_label = QLabel("<h2>Available Petri Nets</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Add instruction label
        instruction_label = QLabel("Select a Petri net from the list below to visualize:")
        layout.addWidget(instruction_label)
        
        # Create list widget
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        layout.addWidget(self.list_widget)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        self.view_button = QPushButton("View Selected")
        self.view_button.setEnabled(False)  # Disabled until selection
        button_layout.addWidget(self.view_button)
        
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.cancel_button)
        
        self.load_parser_definitions_button = QPushButton("Load Parser Definitions")
        button_layout.addWidget(self.load_parser_definitions_button)
        
        layout.addLayout(button_layout)
        
        self.setCentralWidget(main_widget)
        
        # Connect signals
        self.list_widget.currentItemChanged.connect(self.on_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.view_button.clicked.connect(self.on_view_clicked)
        self.cancel_button.clicked.connect(self.close)
        self.load_parser_definitions_button.clicked.connect(self.load_parser_definitions)
        
        # Create parser instance for loading definitions
        self.parser = ProcessAlgebraParser()
        
        # Sample Petri nets list
        self.available_nets = [
            {
                'name': 'Simple Cycle',
                'description': 'P = a.b.P',
                'expression': 'P = a.b.P'
            },
            {
                'name': 'Choice Process',
                'description': 'P = a.P + b.STOP',
                'expression': 'P = a.P + b.STOP'
            },
            {
                'name': 'Ping-Pong Processes',
                'description': 'P = ping.Q\nQ = pong.P',
                'expression': 'P = ping.Q\nQ = pong.P'
            },
            {
                'name': 'Complex Cycle',
                'description': 'P = a.b.P + c.Q\nQ = d.e.P + f.Q',
                'expression': 'P = a.b.P + c.Q\nQ = d.e.P + f.Q'
            },
            {
                'name': 'Producer-Consumer',
                'description': 'Producer = produce.send.Producer\nConsumer = receive.consume.Consumer\nSystem = Producer | Consumer',
                'expression': 'Producer = produce.send.Producer\nConsumer = receive.consume.Consumer\nSystem = Producer | Consumer'
            }
        ]
        
        # List to store named Petri nets from parser
        self.parser_nets = []
    
    def populate_list(self):
        """Populate the list with available Petri nets"""
        self.list_widget.clear()
        
        # Add predefined examples
        if self.available_nets:
            self.list_widget.addItem("--- Predefined Examples ---")
            item = self.list_widget.item(0)
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)  # Make header non-selectable
            
            for net in self.available_nets:
                item = QListWidgetItem(net['name'])
                item.setData(Qt.UserRole, net)  # Store the full net data
                item.setToolTip(net['description'])
                self.list_widget.addItem(item)
        
        # Add parser definitions if any
        if self.parser_nets:
            self.list_widget.addItem("")  # Spacer
            item = self.list_widget.item(self.list_widget.count() - 1)
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)  # Make spacer non-selectable
            
            self.list_widget.addItem("--- Parser Definitions ---")
            item = self.list_widget.item(self.list_widget.count() - 1)
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)  # Make header non-selectable
            
            for net in self.parser_nets:
                item = QListWidgetItem(net['name'])
                item.setData(Qt.UserRole, net)  # Store the full net data
                item.setToolTip(net['description'])
                self.list_widget.addItem(item)
    
    def on_selection_changed(self, current, previous):
        """Handle selection change in the list"""
        # Only enable the view button if current is a selectable item
        if current and current.flags() & Qt.ItemIsSelectable:
            self.view_button.setEnabled(True)
        else:
            self.view_button.setEnabled(False)
    
    def on_item_double_clicked(self, item):
        """Handle double-click on an item"""
        if item and item.flags() & Qt.ItemIsSelectable:
            net_data = item.data(Qt.UserRole)
            self.net_selected.emit(net_data['expression'])
            self.close()
    
    def on_view_clicked(self):
        """Handle view button click"""
        current_item = self.list_widget.currentItem()
        if current_item and current_item.flags() & Qt.ItemIsSelectable:
            net_data = current_item.data(Qt.UserRole)
            self.net_selected.emit(net_data['expression'])
            self.close()
    
    def add_custom_net(self, name, description, expression):
        """Add a custom Petri net to the list"""
        new_net = {
            'name': name,
            'description': description,
            'expression': expression
        }
        
        # Check if this expression already exists in available_nets
        for net in self.available_nets:
            if net['expression'] == expression:
                return  # Skip duplicate expressions
        
        # Check if this expression already exists in parser_nets
        for net in self.parser_nets:
            if net['expression'] == expression:
                return  # Skip duplicate expressions
        
        # Add to available nets
        self.available_nets.append(new_net)
        
        # Refresh the list
        self.populate_list()
        
        # Select the new item
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item and item.flags() & Qt.ItemIsSelectable and item.data(Qt.UserRole) and item.data(Qt.UserRole)['name'] == name:
                self.list_widget.setCurrentItem(item)
                break
    
    def load_parser_definitions(self):
        """Load Petri net definitions from the parser"""
        # Clear previous parser nets
        self.parser_nets = []
        
        # Get process definitions from parser
        process_definitions = self.parser.process_definitions
        if not process_definitions:
            return
        
        # Convert process definitions to net format
        for name, expr in process_definitions.items():
            # Create a complete expression that can be parsed
            full_expr = f"{name} = {expr}"
            
            net = {
                'name': f"Process: {name}",
                'description': full_expr,
                'expression': full_expr
            }
            self.parser_nets.append(net)
        
        # Refresh the list
        self.populate_list()
    
    def show_selector(self):
        """Show the selector window with updated list"""
        self.populate_list()
        self.show()
        self.raise_()