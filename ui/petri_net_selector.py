# ui/petri_net_selector.py

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, pyqtSignal
from models.parser import ProcessAlgebraParser
import re

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
                'description': 'Process = action.behavior.Process',
                'expression': 'Process = action.behavior.Process'
            },
            {
                'name': 'Choice Process',
                'description': 'Process = action.Process + behavior.STOP',
                'expression': 'Process = action.Process + behavior.STOP'
            },
            {
                'name': 'Ping-Pong Processes',
                'description': 'Ping = ping.Pong\nPong = pong.Ping',
                'expression': 'Ping = ping.Pong\nPong = pong.Ping'
            },
            {
                'name': 'Complex Cycle',
                'description': 'Process = action.behavior.Process + choice.Query\nQuery = decide.execute.Process + follow.Query',
                'expression': 'Process = action.behavior.Process + choice.Query\nQuery = decide.execute.Process + follow.Query'
            },
            {
                'name': 'Bracketed Example',
                'description': 'Process = (action.behavior).Process + (choice.done).STOP',
                'expression': 'Process = (action.behavior).Process + (choice.done).STOP'
            },
            {
                'name': 'Producer-Consumer',
                'description': 'Producer = produce.send.Producer\nConsumer = receive.consume.Consumer\nSystem = Producer | Consumer',
                'expression': 'Producer = produce.send.Producer\nConsumer = receive.consume.Consumer\nSystem = Producer | Consumer'
            },
            {
                'name': 'Nested Brackets',
                'description': 'Process = (action.(behavior.next)).Process + choice.(done.(exit.STOP))',
                'expression': 'Process = (action.(behavior.next)).Process + choice.(done.(exit.STOP))'
            }
        ]
        
        # List to store named Petri nets from parser
        self.parser_nets = []
    
    def find_processes_in_right_hand_side(self, process_definitions):
        """Find process names that appear on the right-hand side of any definition"""
        right_side_processes = set()
        
        for process_name, definition in process_definitions.items():
            # Look for process names (including when they're part of expressions)
            for other_name in process_definitions.keys():
                if other_name != process_name:  # Skip self-references
                    # Use regex to find whole word matches only
                    pattern = r'\b' + re.escape(other_name) + r'\b'
                    if re.search(pattern, definition):
                        right_side_processes.add(other_name)
        
        return right_side_processes
    
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
                
        # Select the first selectable item automatically if available
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item and item.flags() & Qt.ItemIsSelectable:
                self.list_widget.setCurrentItem(item)
                break

    
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
            
            # Show a message with the selected net name
            print(f"Selected: {net_data['name']}")
            
            # Emit the signal with the expression
            self.net_selected.emit(net_data['expression'])
            
            # Close the selector window
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
        """Load Petri net definitions from the parser, filtering out
        those that appear on the right-hand side of other definitions"""
        
        # Clear previous parser nets
        self.parser_nets = []
        
        # Get process definitions from parser
        process_definitions = self.parser.process_definitions
        print(f"Loading parser definitions...", process_definitions)
        if not process_definitions:
            return
        
        # Find processes that appear on the right-hand side
        right_side_processes = self.find_processes_in_right_hand_side(process_definitions)
        print(f"Processes on right-hand side: {right_side_processes}")
        
        # Convert process definitions to net format, excluding those on the right side
        for name, expr in process_definitions.items():
            # Skip if this process appears on the right-hand side of another process
            if name in right_side_processes:
                continue
                
            # Create a complete expression that can be parsed
            full_expr = f"{name} = {expr}"
            print(f"Including process for display: {full_expr}")
            
            # Skip duplicates
            duplicate = False
            for net in self.parser_nets:
                if net['expression'] == full_expr:
                    duplicate = True
                    break
                    
            if not duplicate:
                net = {
                    'name': f"Process: {name}",
                    'description': full_expr,
                    'expression': full_expr
                }
                self.parser_nets.append(net)
                print(f"Added to selector: {net['name']}")
    
        # Add a special entry for the combined processes if there are multiple
        # and at least one process is not on the right-hand side
        if len(process_definitions) > 1 and len(self.parser_nets) > 0:
            # Create a combined expression with all processes
            combined_expr = "\n".join([f"{name} = {expr}" for name, expr in process_definitions.items()])
            
            # Add a "Main System" entry that includes all processes
            all_processes = {
                'name': "Main System (All Processes)",
                'description': "Combined system with all defined processes",
                'expression': combined_expr
            }
            self.parser_nets.append(all_processes)
        
        # Refresh the list
        self.populate_list()
    
    def show_selector(self):
        """Show the selector window with updated list"""
        self.populate_list()
        self.show()
        self.raise_()