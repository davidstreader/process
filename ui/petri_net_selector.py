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
    
   ############################
   # Update this method in ui/petri_net_selector.py

    # Update this method in ui/petri_net_selector.py

    def load_parser_definitions(self):
        """Load Petri net definitions from the parser, handling references properly"""
        
        # Clear previous parser nets
        self.parser_nets = []
        
        # Get process definitions from parser
        process_definitions = self.parser.main_processes
        print(f"Loading parser definitions: {process_definitions}")
        if not process_definitions:
            return
        
        # For each process, create a complete expression that includes all
        # processes it references, directly or indirectly
        for process_name in process_definitions:
            # Start with the selected process
            included_processes = [process_name]
            
            # Follow references recursively
            def add_references(proc):
                expr = process_definitions[proc]
                for ref_name in process_definitions:
                    if ref_name != proc and ref_name not in included_processes:
                        pattern = r'\b' + re.escape(ref_name) + r'\b'
                        if re.search(pattern, expr):
                            included_processes.append(ref_name)
                            add_references(ref_name)
            
            # Find all processes referenced by this one
            add_references(process_name)
            
            # Create the full expression with all required processes
            full_expr = "\n".join([f"{name} = {process_definitions[name]}" 
                                for name in included_processes])
            
            # Create the net entry
            net = {
                'name': f"Process: {process_name}",
                'description': full_expr,
                'expression': full_expr
            }
            
            # Check for duplicates
            if not any(existing['expression'] == full_expr for existing in self.parser_nets):
                self.parser_nets.append(net)
                print(f"Added net for {process_name} with processes: {', '.join(included_processes)}")
        
        # Also create a combined expression with all processes
        
        
        # Refresh the list
        self.populate_list()
   # ###########################
                
    
    def show_selector(self):
        """Show the selector window with updated list"""
        self.populate_list()
        self.show()
        self.raise_()