import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QTextEdit, QWidget, QLabel
from PyQt5.QtCore import Qt

# Import the necessary modules from the project
from models.parser import ProcessAlgebraParser
from ui.petri_net_window import PetriNetWindow

class DebugWindow(QMainWindow):
    """Debug window to diagnose visualization issues"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Petri Net Visualization Debugger")
        self.resize(800, 600)
        
        # Create main widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # Add test text input
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Enter test process algebra expression...")
        self.text_edit.setText("P = a.b.P + c")  # Default test case
        layout.addWidget(QLabel("<b>Test Process Algebra</b>"))
        layout.addWidget(self.text_edit)
        
        # Add debug output area
        self.debug_output = QTextEdit()
        self.debug_output.setReadOnly(True)
        layout.addWidget(QLabel("<b>Debug Output</b>"))
        layout.addWidget(self.debug_output)
        
        # Add debug controls
        self.parse_button = QPushButton("1. Parse Expression")
        self.visualize_button = QPushButton("2. Visualize Petri Net")
        self.inspect_button = QPushButton("3. Inspect Scene Objects")
        
        layout.addWidget(self.parse_button)
        layout.addWidget(self.visualize_button)
        layout.addWidget(self.inspect_button)
        
        self.setCentralWidget(main_widget)
        
        # Initialize parser and visualization window
        self.parser = ProcessAlgebraParser()
        self.petri_net_window = PetriNetWindow()
        
        # Connect signals
        self.parse_button.clicked.connect(self.parse_test_expression)
        self.visualize_button.clicked.connect(self.visualize_test_petri_net)
        self.inspect_button.clicked.connect(self.inspect_scene)
        
        # Show parser and scene status
        self.log_debug("Debugger initialized. Parser and PetriNetWindow created.")
        self.log_debug("Use the buttons below to diagnose the visualization issue.")
    
    def log_debug(self, message):
        """Add a debug message to the output area"""
        self.debug_output.append(message)
    
    def parse_test_expression(self):
        """Parse the test expression and log results"""
        expression = self.text_edit.toPlainText()
        self.log_debug(f"\n--- Parsing Expression ---\n{expression}")
        
        success = self.parser.parse(expression)
        
        if success:
            self.log_debug("✅ Parsing successful")
            
            # Log the Petri net structure
            self.log_debug(f"Places: {len(self.parser.places)}")
            for p in self.parser.places:
                self.log_debug(f"  - Place: id={p['id']}, name={p['name']}, tokens={p.get('tokens', 0)}, pos=({p['x']}, {p['y']})")
            
            self.log_debug(f"Transitions: {len(self.parser.transitions)}")
            for t in self.parser.transitions:
                self.log_debug(f"  - Transition: id={t['id']}, name={t['name']}, pos=({t['x']}, {t['y']})")
            
            self.log_debug(f"Arcs: {len(self.parser.arcs)}")
            for a in self.parser.arcs:
                direction = "Place → Transition" if a['is_place_to_transition'] else "Transition → Place"
                self.log_debug(f"  - Arc: {a['source_id']} → {a['target_id']} ({direction})")
        else:
            self.log_debug("❌ Parsing failed")
    
    def visualize_test_petri_net(self):
        """Attempt to visualize the Petri net and debug the process"""
        if not self.parser.places and not self.parser.transitions:
            self.log_debug("❌ No Petri net data available. Please parse an expression first.")
            return
        
        self.log_debug("\n--- Visualizing Petri Net ---")
        
        # Backup the original update_petri_net method for comparison
        original_update = self.petri_net_window.update_petri_net
        
        # Create a wrapper to log what happens during visualization
        def debug_update_petri_net(parser):
            self.log_debug(f"update_petri_net called with parser containing:")
            self.log_debug(f"  - {len(parser.places)} places")
            self.log_debug(f"  - {len(parser.transitions)} transitions")
            self.log_debug(f"  - {len(parser.arcs)} arcs")
            
            # Check if the PetriNetWindow has a valid scene
            if not hasattr(self.petri_net_window, 'scene') or not self.petri_net_window.scene:
                self.log_debug("❌ PetriNetWindow.scene is missing or invalid")
                return
            
            # Log information about the scene before update
            self.log_debug(f"Scene before update: {self.petri_net_window.scene.items().__len__()} items")
            
            # Call the original method
            try:
                original_update(parser)
                self.log_debug("✅ update_petri_net executed without exceptions")
            except Exception as e:
                self.log_debug(f"❌ Exception during update_petri_net: {str(e)}")
                import traceback
                self.log_debug(traceback.format_exc())
                return
            
            # Log information about the scene after update
            self.log_debug(f"Scene after update: {self.petri_net_window.scene.items().__len__()} items")
            
        # Replace the method temporarily
        self.petri_net_window.update_petri_net = debug_update_petri_net
        
        # Call the visualization method
        self.petri_net_window.update_petri_net(self.parser)
        
        # Show the Petri net window
        self.petri_net_window.show()
        self.petri_net_window.raise_()
        
        # Restore the original method
        self.petri_net_window.update_petri_net = original_update
    
    def inspect_scene(self):
        """Inspect the QGraphicsScene objects to diagnose visualization issues"""
        self.log_debug("\n--- Inspecting Scene Objects ---")
        
        if not hasattr(self.petri_net_window, 'scene') or not self.petri_net_window.scene:
            self.log_debug("❌ PetriNetWindow.scene is missing or invalid")
            return
        
        # Get all items in the scene
        scene_items = self.petri_net_window.scene.items()
        self.log_debug(f"Total scene items: {len(scene_items)}")
        
        # Categorize items by type
        item_types = {}
        for item in scene_items:
            item_type = type(item).__name__
            if item_type not in item_types:
                item_types[item_type] = 0
            item_types[item_type] += 1
        
        # Log item types
        self.log_debug("Item types in scene:")
        for t, count in item_types.items():
            self.log_debug(f"  - {t}: {count}")
        
        # Check if the scene is shown correctly in the view
        self.log_debug(f"Scene rect: {self.petri_net_window.scene.sceneRect()}")
        self.log_debug(f"View rect: {self.petri_net_window.view.viewport().rect()}")
        
        # Check if items are positioned correctly
        places = [item for item in scene_items if hasattr(item, 'place_data')]
        transitions = [item for item in scene_items if hasattr(item, 'transition_data')]
        
        self.log_debug(f"Place items: {len(places)}")
        self.log_debug(f"Transition items: {len(transitions)}")
        
        # If there are no items, suggest possible fixes
        if len(scene_items) == 0:
            self.log_debug("\n⚠️ Potential fixes for empty scene:")
            self.log_debug("1. Check if clear_and_draw_petri_net is being called correctly")
            self.log_debug("2. Verify that DraggableScene.draw_arcs is implemented correctly")
            self.log_debug("3. Make sure the parser is generating valid place and transition data")
            self.log_debug("4. Check if view settings like transform or visibility are correct")
            self.log_debug("5. Verify PetriNetScene constructor is correctly setting up properties")

def run_debugger():
    """Run the debugger application"""
    app = QApplication(sys.argv)
    window = DebugWindow()
    window.show()
    app.exec_()

if __name__ == "__main__":
    run_debugger()