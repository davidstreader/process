# Update this in ui/petri_net_window.py

import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QGraphicsView, QCheckBox, 
                            QMessageBox, QGraphicsItem, QGraphicsScene)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor

from models.layout import ForceDirectedLayout
from models.parser import ProcessAlgebraParser
from ui.petri_net_scene import PetriNetScene, DraggableScene
from ui.petri_net_selector import PetriNetSelectorWindow

# Update imports in ui/petri_net_window.py

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QGraphicsView, QCheckBox, 
                            QMessageBox, QGraphicsItem, QGraphicsScene,
                            QDialog, QTextEdit)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor

# Make sure SaveDialog is defined before PetriNetWindow

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

class PetriNetWindow(QMainWindow):
    """Window for visualizing the Petri net with force-directed layout"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Petri Net Visualization")
        self.resize(800, 600)
        
        # Create main widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # Create initial selection message
        self.selection_label = QLabel("<h3>Please select a Petri net to visualize</h3>")
        self.selection_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.selection_label)
        
        # Add select button
        self.select_button = QPushButton("Select Petri Net")
        layout.addWidget(self.select_button)
        
        # Create graphics view and scene (initially hidden)
        self.view_widget = QWidget()
        view_layout = QVBoxLayout(self.view_widget)
        
        self.scene = DraggableScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.NoDrag)
        view_layout.addWidget(self.view)
        
        # Add zoom controls
        zoom_layout = QHBoxLayout()
        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_out_button = QPushButton("Zoom Out")
        self.reset_view_button = QPushButton("Reset View")
        zoom_layout.addWidget(self.zoom_in_button)
        zoom_layout.addWidget(self.zoom_out_button)
        zoom_layout.addWidget(self.reset_view_button)
        view_layout.addLayout(zoom_layout)
        
        # Add layout controls
        layout_control_layout = QHBoxLayout()
        self.enable_layout_checkbox = QCheckBox("Enable Spring Layout")
        self.apply_layout_button = QPushButton("Apply Full Layout")
        self.settings_button = QPushButton("Layout Settings")
        layout_control_layout.addWidget(self.enable_layout_checkbox)
        layout_control_layout.addWidget(self.apply_layout_button)
        layout_control_layout.addWidget(self.settings_button)
        view_layout.addLayout(layout_control_layout)
        
        # Add this to the PetriNetWindow.__init__ method, just after the layout_control_layout code
        # In the view_layout.addLayout(layout_control_layout) section

        # Add save button
        save_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Petri Net")
        save_layout.addWidget(self.save_button)
        view_layout.addLayout(save_layout)



        # Add "back to selection" button
        back_layout = QHBoxLayout()
        self.back_button = QPushButton("Back to Selection")
        back_layout.addWidget(self.back_button)
        view_layout.addLayout(back_layout)
        
        # Add the view widget to the main layout (initially hidden)
        layout.addWidget(self.view_widget)
        self.view_widget.setVisible(False)
        
        self.setCentralWidget(main_widget)
        
        # Set up force-directed layout
        self.layout_algorithm = ForceDirectedLayout()
        self.enable_layout = False
        self.parser = ProcessAlgebraParser()  # Create a parser instance
        self.node_being_dragged = False
        
        # Create Petri net selector
        self.selector_window = PetriNetSelectorWindow()
        
        # Set up animation timer
        self.animation_timer = QTimer(self)
        self.animation_timer.setInterval(50)  # 20 fps
        
        # Connect signals
        self.select_button.clicked.connect(self.show_selector)
        self.back_button.clicked.connect(self.show_selection_screen)
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.reset_view_button.clicked.connect(self.reset_view)
        self.enable_layout_checkbox.stateChanged.connect(self.toggle_layout)
        self.apply_layout_button.clicked.connect(self.run_full_layout)
        self.animation_timer.timeout.connect(self.update_layout_step)
        self.selector_window.net_selected.connect(self.on_petri_net_selected)
        # Then add this in the connection setup section:
        self.save_button.clicked.connect(self.save_current_petri_net)
        # Allow mouse wheel zooming
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
    
    def show_selector(self):
        """Show the Petri net selector window"""
        self.selector_window.show_selector()
    
    def show_selection_screen(self):
        """Show the initial selection screen"""
        self.animation_timer.stop()
        self.view_widget.setVisible(False)
        self.selection_label.setVisible(True)
        self.select_button.setVisible(True)
    
    def show_visualization_screen(self):
        """Show the visualization screen"""
        self.selection_label.setVisible(False)
        self.select_button.setVisible(False)
        self.view_widget.setVisible(True)
    #####
    # Update this method in ui/petri_net_window.py
    def on_petri_net_selected(self, expression):
        """Handle selection of a Petri net from the selector"""
        print(f"Selected Petri net: {expression}")
        
        # Parse the expression
        success = self.parser.parse(expression)
        
        if success:
            print(f"Successfully parsed Petri net with {len(self.parser.places)} places, {len(self.parser.transitions)} transitions")
            
            # Show parsing results for debugging
            print("Process definitions:")
            for name, expr in self.parser.process_definitions.items():
                print(f"  {name} = {expr}")
            
            print("Places:")
            for place in self.parser.places:
                print(f"  ID: {place['id']}, Name: {place['name']}, Process: {place.get('process', 'None')}")
            
            print("Transitions:")
            for transition in self.parser.transitions:
                print(f"  ID: {transition['id']}, Name: {transition['name']}, Process: {transition.get('process', 'None')}")
            
            print("Arcs:")
            for arc in self.parser.arcs:
                print(f"  Source: {arc['source_id']}, Target: {arc['target_id']}, Place->Trans: {arc['is_place_to_transition']}")
            
            # Update the window title with the selected expression (shortened)
            display_expr = expression.split('\n')[0]
            if len(display_expr) > 40:
                display_expr = display_expr[:37] + "..."
            self.setWindowTitle(f"Petri Net: {display_expr}")
            
            # Update the visualization
            self.update_petri_net(self.parser)
            
            # Show the visualization screen
            self.show_visualization_screen()
            
            # Make sure the window is visible and raised
            self.show()
            self.raise_()
        else:
            # Get parsing errors
            errors = self.parser.get_parsing_errors()
            error_message = "Unable to parse the process algebra expression:\n\n"
            for error in errors:
                error_message += f"• {error}\n"
            
            QMessageBox.warning(self, "Parsing Error", error_message)

            
        # Fix for ui/petri_net_window.py

    def update_petri_net(self, parser, file_path=None):
        """Update the Petri net visualization with the parser data"""
        # Store a reference to the parser for later use
        self.parser = parser
        
        # Make sure we're using the correct scene type
        if not isinstance(self.scene, DraggableScene) and not isinstance(self.scene, PetriNetScene):
            print("Warning: Scene is not a PetriNetScene or DraggableScene instance")
            self.scene = DraggableScene(self)
            self.view.setScene(self.scene)
        
        # Pass a reference to the parser to the scene
        self.scene.parser = parser
        
        # Clear and draw the Petri net using the parser data
        self.scene.clear_and_draw_petri_net(parser)
        
        # Reset view to show all elements
        self.reset_view()
        
        # Show the visualization screen - THIS WAS MISSING
        self.show_visualization_screen()
        
        # Start layout animation if enabled
        if self.enable_layout:
            self.layout_algorithm.initialize_layout(parser)
            self.animation_timer.start()
        
        # Update window to show we're viewing a Petri net
        if file_path:
            import os
            self.setWindowTitle(f"Petri Net: {os.path.basename(file_path)}")

    # Update UI state
        self.update_ui_state()
        
        # Fix for ui/editor_window.py - load_petri_net_from_file method
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
                
                # Ensure the parser is shared with the Petri net window
                if self.petri_net_window:
                    self.petri_net_window.parser = self.parser
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

    # Fix for ui/petri_net_scene.py - clear_and_draw_petri_net method
    def clear_and_draw_petri_net(self, parser):
        """Override to track related items"""
        # Clear tracking dictionaries
        self.node_related_items = {}
        
        # Debug: Print parser data to verify we're receiving it correctly
        print(f"Drawing Petri net with {len(parser.places)} places, {len(parser.transitions)} transitions")
        
        # Initialize node_related_items for all places and transitions BEFORE drawing
        for place in parser.places:
            place_id = place['id']
            self.node_related_items[f"p{place_id}"] = {
                "labels": [],
                "tokens": []
            }
        
        for transition in parser.transitions:
            transition_id = transition['id']
            self.node_related_items[f"t{transition_id}"] = {
                "labels": []
            }
        
        # Store a reference to the parser
        self.parser = parser
        
        # Clear the scene before drawing
        self.clear()
        self.place_items = {}
        self.transition_items = {}
        self.arc_items = {}
        
        # Draw places (circles)
        for place in parser.places:
            self.draw_place(place)
        
        # Draw transitions (rectangles)
        for transition in parser.transitions:
            self.draw_transition(transition)
        
        # Draw arcs (arrows)
        self.draw_arcs(parser)
        
        # Set scene rect to fit all items with padding
        if self.items():  # Only set if there are items to display
            self.setSceneRect(self.itemsBoundingRect().adjusted(-50, -50, 50, 50))
            print(f"Set scene rect to {self.sceneRect()}")
        else:
            print("Warning: No items to display in the scene")

    def   update_layout_parameters(self, params):
        """Update the layout algorithm parameters from settings window"""
        print(f"Received new layout parameters: {params}")
            
        # Update the algorithm with new parameters
        self.layout_algorithm.set_parameters(params)
            
         # If layout is enabled, immediately apply the new settings
        if self.enable_layout and self.parser:
              # When parameters change, reinitialize the layout with new settings
            self.layout_algorithm.initialize_layout(self.parser)
        
    
    
    # Add debugging to toggle_layout in ui/petri_net_window.py
    def toggle_layout(self, state):
        """Toggle the force-directed layout animation"""
        self.enable_layout = (state == Qt.Checked)
        
        print(f"Toggle layout: {self.enable_layout}, Parser has {len(self.parser.places) if self.parser else 0} places")
        
        if self.enable_layout and self.parser:
            # Initialize layout and start animation
            self.layout_algorithm.initialize_layout(self.parser)
            self.animation_timer.start()
            print("Layout animation started")
        else:
            # Stop animation
            self.animation_timer.stop()
            print("Layout animation stopped")


# Add this method to PetriNetWindow to ensure buttons are properly enabled/disabled
    def update_ui_state(self):
        """Update UI elements based on current state"""
        has_petri_net = hasattr(self, 'parser') and self.parser and len(self.parser.places) > 0
        
        # Enable/disable buttons that require a Petri net
        self.zoom_in_button.setEnabled(has_petri_net)
        self.zoom_out_button.setEnabled(has_petri_net)
        self.reset_view_button.setEnabled(has_petri_net)
        self.apply_layout_button.setEnabled(has_petri_net)
        self.settings_button.setEnabled(has_petri_net)
        self.save_button.setEnabled(has_petri_net)
        
        print(f"UI state updated, Petri net available: {has_petri_net}")


    def update_layout_step(self):
        """Update a single step of the force-directed layout"""
        if self.enable_layout and self.parser and not self.node_being_dragged:
            # Update layout for a single iteration
            self.layout_algorithm.update_single_iteration(self.parser)
            
            # Redraw the scene to reflect the updated positions
            self.scene.clear_and_draw_petri_net(self.parser)
    
    def update_arcs(self):
        """Redraw arcs to match current node positions"""
        if self.parser:
            # Update the coordinates in the parser from the graphics items
            for place_id, item in self.scene.place_items.items():
                for place in self.parser.places:
                    if place['id'] == place_id:
                        center = item.sceneBoundingRect().center()
                        place['x'] = center.x()
                        place['y'] = center.y()
                        break
            
            for transition_id, item in self.scene.transition_items.items():
                for transition in self.parser.transitions:
                    if transition['id'] == transition_id:
                        center = item.sceneBoundingRect().center()
                        transition['x'] = center.x()
                        transition['y'] = center.y()
                        break
            
            # Redraw the arcs
            self.scene.draw_arcs(self.parser)
    
    def run_full_layout(self):
        """Run the full layout algorithm and redraw"""
        if self.parser:
            # Apply full force-directed layout
            self.layout_algorithm.apply_layout(self.parser)
            
            # Redraw the scene
            self.scene.clear_and_draw_petri_net(self.parser)
            self.reset_view()
            
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
                if transition['id'] == node_id:  # Fixed: was using transition_id incorrectly
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
        self.update_arcs()
        
        # Resume the layout animation if enabled
        if self.enable_layout:
            self.animation_timer.start()
    
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

        # Add this method to the PetriNetWindow class in ui/petri_net_window.py

    def node_position_changed(self, node_type, node_id):
        """Handle node position changes"""
        # Make sure the parser is updated with the new position
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

    def save_current_petri_net(self):
        """Save the current Petri net to the stored nets"""
        if not self.parser or not hasattr(self.parser, 'store_current_petri_net'):
            QMessageBox.warning(self, "Save Error", "No parser available or parser doesn't support storing nets.")
            return
        
        if not self.parser.places and not self.parser.transitions:
            QMessageBox.warning(self, "Save Error", "No Petri net to save. Please visualize a valid process algebra expression first.")
            return
        
        # Get a name for the Petri net
        dialog = SaveDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name = dialog.get_name()
            if name:
                try:
                    # If we have a current_net already, update its name
                    expression = ""
                    for process_name, definition in self.parser.process_definitions.items():
                        expression += f"{process_name} = {definition}\n"
                    
                    # Store the current Petri net
                    net_id = self.parser.store_current_petri_net(name, expression)
                    QMessageBox.information(self, "Save Successful", f"Petri net saved as '{name}'")
                    
                    # Update the selector window with the new net
                    if hasattr(self.selector_window, 'populate_list'):
                        self.selector_window.populate_list()
                    
                except Exception as e:
                    QMessageBox.critical(self, "Save Error", f"Error saving Petri net: {str(e)}")
            else:
                QMessageBox.warning(self, "Save Error", "Please enter a name for the Petri net.")


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