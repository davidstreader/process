

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QTextEdit, QPushButton, QMenuBar, QMenu, 
                             QAction, QFileDialog, QMessageBox, QDialog, QLabel,
                             QGraphicsView, QCheckBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPainter

from ui.petri_net_scene import PetriNetScene, DraggableScene
from models.parser import ProcessAlgebraParser
from models.layout import ForceDirectedLayout
from models.file_manager import FileManager

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
        self.add_resize_controls()
        self.add_resize_menu_actions()
        self.connect_splitter_signals()
    
    def get_name(self):
        """Get the entered name"""
        return self.name_edit.toPlainText().strip()

class MainWindow(QMainWindow):
    """Main application window with split pane layout"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Process Algebra to Petri Net")
        self.resize(1200, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Create file manager
        self.file_manager = FileManager()
        
        # Create parser and layout algorithm
        self.parser = ProcessAlgebraParser()
        self.layout_algorithm = ForceDirectedLayout()
        
        # Create splitter for the two panes
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Left pane: Process Algebra text editor
        self.left_pane = QWidget()
        left_layout = QVBoxLayout(self.left_pane)
        
        left_layout.addWidget(QLabel("<b>Process Algebra Editor</b>"))
        
        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("Enter process algebra expressions here...\nExample:\nP = a.b + c.d\nQ = e.f.P")
        left_layout.addWidget(self.text_editor)
        
        # Button to visualize
        visualize_layout = QHBoxLayout()
        self.visualize_button = QPushButton("Visualize")
        self.clear_button = QPushButton("Clear")
        visualize_layout.addWidget(self.visualize_button)
        visualize_layout.addWidget(self.clear_button)
        left_layout.addLayout(visualize_layout)
        
        # Add the left pane to the splitter
        self.splitter.addWidget(self.left_pane)
        
        # Right pane: Petri Net visualization
        self.right_pane = QWidget()
        right_layout = QVBoxLayout(self.right_pane)
        
        right_layout.addWidget(QLabel("<b>Petri Net Visualization</b>"))
        
        # Create the Petri net scene and view
        self.scene = DraggableScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        #self.view.setRenderHint(QGraphicsView.Antialiasing)
        right_layout.addWidget(self.view)
        
        # Layout controls
        layout_controls = QHBoxLayout()
        self.enable_layout_checkbox = QCheckBox("Enable Spring Layout")
        self.apply_layout_button = QPushButton("Apply Full Layout")
        self.settings_button = QPushButton("Layout Settings")
        layout_controls.addWidget(self.enable_layout_checkbox)
        layout_controls.addWidget(self.apply_layout_button)
        layout_controls.addWidget(self.settings_button)
        right_layout.addLayout(layout_controls)
        
        # Zoom controls
        zoom_controls = QHBoxLayout()
        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_out_button = QPushButton("Zoom Out")
        self.reset_view_button = QPushButton("Reset View")
        zoom_controls.addWidget(self.zoom_in_button)
        zoom_controls.addWidget(self.zoom_out_button)
        zoom_controls.addWidget(self.reset_view_button)
        right_layout.addLayout(zoom_controls)
        
        # Add the right pane to the splitter
        self.splitter.addWidget(self.right_pane)
        
        # Add splitter to main layout
        main_layout.addWidget(self.splitter)
        
        # Set initial splitter position (40% left, 60% right)
        self.splitter.setSizes([480, 720])
        
        # Set up animation timer for layout
        self.animation_timer = QTimer(self)
        self.animation_timer.setInterval(50)  # 20 fps
        
        # Set as central widget
        self.setCentralWidget(main_widget)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Connect signals
        self.connect_signals()
        
        # State tracking
        self.node_being_dragged = False
        self.enable_layout = False
        
        # Try to load last net
        self.load_last_net()
    
    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # New action
        new_action = QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        # Load action
        load_action = QAction('Load...', self)
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.load_file)
        file_menu.addAction(load_action)
        
        # Save action
        save_action = QAction('Save...', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Visualize menu
        visualize_menu = menubar.addMenu('Visualize')
        
        # Visualize action
        visualize_action = QAction('Visualize Petri Net', self)
        visualize_action.setShortcut('F5')
        visualize_action.triggered.connect(self.visualize_petri_net)
        visualize_menu.addAction(visualize_action)
        
        # Load example action
        example_action = QAction('Load Example', self)
        example_action.triggered.connect(self.load_example)
        visualize_menu.addAction(example_action)
        
        # Layout settings action
        settings_action = QAction('Layout Settings', self)
        settings_action.triggered.connect(self.show_layout_settings)
        visualize_menu.addAction(settings_action)
    
    def connect_signals(self):
        """Connect all signals and slots"""
        # Editor buttons
        self.visualize_button.clicked.connect(self.visualize_petri_net)
        self.clear_button.clicked.connect(self.text_editor.clear)
        
        # Layout controls
        self.enable_layout_checkbox.stateChanged.connect(self.toggle_layout)
        self.apply_layout_button.clicked.connect(self.run_full_layout)
        
        # Zoom controls
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.reset_view_button.clicked.connect(self.reset_view)
        
        # Animation timer
        self.animation_timer.timeout.connect(self.update_layout_step)
    
    def new_file(self):
        """Create a new empty file"""
        self.text_editor.clear()
        self.scene.clear()
        self.parser.reset()
    
    def load_file(self):
        """Open dialog to load a Petri net"""
        # Get available nets
        nets = self.file_manager.get_available_nets()
        
        if not nets:
            QMessageBox.information(self, "No Nets", "No saved Petri nets found.")
            return
        
        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Petri Net", str(self.file_manager.nets_dir),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            self.load_petri_net_from_file(file_path)
    
    def save_file(self):
        """Open dialog to save the current Petri net"""
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
    
    def load_example(self):
        """Load an example process algebra expression"""
        example = """# Simple Process Algebra Example with Brackets
Process = (action.behavior).Process + choice.(done.STOP)
Query = event.(Process) + (function.going).Query
Main = (Process) | (Query)"""
        self.text_editor.setText(example)
    
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
                    # Load process definitions
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
                
                # Update the visualization
                self.update_visualization()
                
                # Set the source code in the editor if available
                if 'source_code' in data and data['source_code']:
                    self.text_editor.setText(data['source_code'])
                else:
                    # Try to generate process algebra code from the Petri net
                    try:
                        process_algebra_code = self.parser.export_to_process_algebra()
                        if process_algebra_code:
                            self.text_editor.setText(process_algebra_code)
                    except Exception as e:
                        print(f"Error generating process algebra code: {str(e)}")
                
                # Show success message
                QMessageBox.information(self, "Load Successful", f"Petri net loaded from '{file_path}'")
                
            except Exception as e:
                QMessageBox.critical(self, "Load Error", f"Error loading Petri net: {str(e)}")
        else:
            QMessageBox.critical(self, "Load Error", f"Could not load Petri net from '{file_path}'")
    
    def load_last_net(self):
        """Try to load the last opened Petri net"""
        last_net = self.file_manager.get_last_net()
        if last_net:
            self.load_petri_net_from_file(last_net)
    
    def visualize_petri_net(self):
        """Parse the current text and visualize the Petri net"""
        # Get the current text
        text = self.text_editor.toPlainText()
        
        if not text.strip():
            QMessageBox.information(self, "Empty Input", "Please enter a process algebra expression first.")
            return
        
        # Parse the text
        success = self.parser.parse(text)
        
        if success:
            # Store the parsed text in the petri_net dictionary
            if hasattr(self.parser, 'store_current_petri_net'):
                # Use the first process name as the net name
                net_name = next(iter(self.parser.main_processes)) if self.parser.main_processes else "Unnamed Net"
                self.parser.store_current_petri_net(net_name, text)
            
            # Update the visualization
            self.update_visualization()
        else:
            # Show parsing errors
            errors = self.parser.get_parsing_errors()
            error_message = "Unable to parse the process algebra expression:\n\n"
            for error in errors:
                error_message += f"• {error}\n"
            
            QMessageBox.warning(self, "Parsing Error", error_message)
    
    def update_visualization(self):
        """Update the Petri net visualization with current parser data"""
        # Clear and draw the Petri net
        self.scene.clear_and_draw_petri_net(self.parser)
        
        # Reset view to show all elements
        self.reset_view()
        
        # Start layout animation if enabled
        if self.enable_layout:
            self.layout_algorithm.initialize_layout(self.parser)
            self.animation_timer.start()
    
    def toggle_layout(self, state):
        """Toggle the force-directed layout animation"""
        self.enable_layout = (state == Qt.Checked)
        
        if self.enable_layout and self.parser:
            # Initialize layout and start animation
            self.layout_algorithm.initialize_layout(self.parser)
            self.animation_timer.start()
        else:
            # Stop animation
            self.animation_timer.stop()
    
    def update_layout_step(self):
        """Update a single step of the force-directed layout"""
        if self.enable_layout and self.parser and not self.node_being_dragged:
            # Update layout for a single iteration
            self.layout_algorithm.update_single_iteration(self.parser)
            
            # Redraw the scene to reflect the updated positions
            self.scene.clear_and_draw_petri_net(self.parser)
    
    def run_full_layout(self):
        """Run the full layout algorithm and redraw"""
        if self.parser and self.parser.places:
            # Apply full force-directed layout
            self.layout_algorithm.apply_layout(self.parser)
            
            # Redraw the scene
            self.scene.clear_and_draw_petri_net(self.parser)
            self.reset_view()
    
    def show_layout_settings(self):
        """Show the layout settings window"""
        # This will be implemented when we integrate with LayoutSettingsWindow
        pass
    
    def start_node_drag(self, node_type, node_id):
        """Handle the start of node dragging"""
        self.node_being_dragged = True
        
        # Pause the layout algorithm during drag
        self.animation_timer.stop()
        
        # Mark the node as fixed if not using force-directed layout
        if node_type == 'place':
            for place in self.parser.places:
                if place['id'] == node_id:
                    place['fixed'] = not self.enable_layout
                    break
        else:  # transition
            for transition in self.parser.transitions:
                if transition['id'] == node_id:
                    transition['fixed'] = not self.enable_layout
                    break
    
    def end_node_drag(self, node_type, node_id):
        """Handle the end of node dragging"""
        self.node_being_dragged = False
        
        # Update the node position from the graphics item
        if node_type == 'place' and node_id in self.scene.place_items:
            item = self.scene.place_items[node_id]
            center = item.sceneBoundingRect().center()
            
            for place in self.parser.places:
                if place['id'] == node_id:
                    place['x'] = center.x()
                    place['y'] = center.y()
                    break
        
        elif node_type == 'transition' and node_id in self.scene.transition_items:
            item = self.scene.transition_items[node_id]
            center = item.sceneBoundingRect().center()
            
            for transition in self.parser.transitions:
                if transition['id'] == node_id:
                    transition['x'] = center.x()
                    transition['y'] = center.y()
                    break
        
        # Redraw arcs to match updated positions
        self.scene.draw_arcs(self.parser)
        
        # Resume the layout animation if enabled
        if self.enable_layout:
            self.animation_timer.start()
    
    def node_position_changed(self, node_type, node_id):
        """Handle node position changes"""
        # Update the parser data with the new position
        if node_type == 'place':
            item = self.scene.place_items.get(node_id)
            if item:
                center = item.sceneBoundingRect().center()
                # Update the parser data
                for place in self.parser.places:
                    if place['id'] == node_id:
                        place['x'] = center.x()
                        place['y'] = center.y()
                        break
        
        elif node_type == 'transition':
            item = self.scene.transition_items.get(node_id)
            if item:
                center = item.sceneBoundingRect().center()
                # Update the parser data
                for transition in self.parser.transitions:
                    if transition['id'] == node_id:
                        transition['x'] = center.x()
                        transition['y'] = center.y()
                        break
        
        # Update arcs to match new positions
        self.scene.draw_arcs(self.parser)
    
    def zoom_in(self):
        """Zoom in the view"""
        self.view.scale(1.2, 1.2)
    
    def zoom_out(self):
        """Zoom out the view"""
        self.view.scale(0.8, 0.8)
    
    def reset_view(self):
        """Reset the view to fit all items"""
        self.view.resetTransform()
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
    
    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming"""
        if event.angleDelta().y() > 0:
            factor = 1.2
        else:
            factor = 0.8
        
        self.view.scale(factor, factor)
    # Add these methods to your MainWindow class

def resize_panes(self, left_ratio=0.4):
    """Resize the panes according to given ratio (left_ratio:1-left_ratio)"""
    total_width = self.splitter.width()
    left_width = int(total_width * left_ratio)
    right_width = total_width - left_width
    self.splitter.setSizes([left_width, right_width])

def add_resize_controls(self):
    """Add buttons to control pane sizing"""
    resize_layout = QHBoxLayout()
    
    self.resize_equal_button = QPushButton("Equal Split")
    self.resize_left_button = QPushButton("More Editor")
    self.resize_right_button = QPushButton("More Visualization")
    
    resize_layout.addWidget(self.resize_equal_button)
    resize_layout.addWidget(self.resize_left_button)
    resize_layout.addWidget(self.resize_right_button)
    
    # Add this layout to the main layout
    main_layout = self.layout()
    main_layout.addLayout(resize_layout)
    
    # Connect signals
    self.resize_equal_button.clicked.connect(lambda: self.resize_panes(0.5))
    self.resize_left_button.clicked.connect(lambda: self.resize_panes(0.7))
    self.resize_right_button.clicked.connect(lambda: self.resize_panes(0.3))

# Add to the View menu
def add_resize_menu_actions(self):
    """Add resize actions to the View menu"""
    view_menu = self.menuBar().addMenu('View')
    
    # Equal split action
    equal_action = QAction('Equal Split', self)
    equal_action.setShortcut('Ctrl+E')
    equal_action.triggered.connect(lambda: self.resize_panes(0.5))
    view_menu.addAction(equal_action)
    
    # More editor action
    left_action = QAction('More Editor Space', self)
    left_action.setShortcut('Ctrl+Left')
    left_action.triggered.connect(lambda: self.resize_panes(0.7))
    view_menu.addAction(left_action)
    
    # More visualization action
    right_action = QAction('More Visualization Space', self)
    right_action.setShortcut('Ctrl+Right')
    right_action.triggered.connect(lambda: self.resize_panes(0.3))
    view_menu.addAction(right_action)

# ResizeableMainWindow extension for automatic resizing on window resize
def resizeEvent(self, event):
    """Handle window resize event to maintain splitter proportions"""
    super().resizeEvent(event)
    
    # Calculate and maintain the current proportion
    if hasattr(self, '_splitter_ratio'):
        self.resize_panes(self._splitter_ratio)
    else:
        # First time - store initial ratio
        total_width = self.splitter.width()
        if total_width > 0:
            sizes = self.splitter.sizes()
            if len(sizes) >= 2 and total_width > 0:
                self._splitter_ratio = sizes[0] / total_width

# Connect splitter moved signal in __init__
def connect_splitter_signals(self):
    """Connect signals for splitter movements"""
    self.splitter.splitterMoved.connect(self.splitter_moved)

def splitter_moved(self, pos, index):
    """Handle splitter move to store the new ratio"""
    total_width = self.splitter.width()
    if total_width > 0:
        sizes = self.splitter.sizes()
        if len(sizes) >= 2:
            self._splitter_ratio = sizes[0] / total_width