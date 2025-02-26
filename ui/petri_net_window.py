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
    def on_petri_net_selected(self, expression):
        """Handle selection of a Petri net from the selector"""
        print(f"Selected Petri net: {expression}")
        
        # Parse the expression
        success = self.parser.parse(expression)
        
        if success:
            # Update the window title with the selected expression (shortened)
            display_expr = expression.split('\n')[0]
            if len(display_expr) > 40:
                display_expr = display_expr[:37] + "..."
            self.setWindowTitle(f"Petri Net: {display_expr}")
            
            # Update the visualization
            self.update_petri_net(self.parser)
            
            # Show the visualization screen
            self.show_visualization_screen()
            
            # Important: share the parsed process definitions with the selector
            # This ensures that the selector can show the named processes from the parser
            self.selector_window.parser = self.parser
        else:
            QMessageBox.warning(self, "Parsing Error", 
                            "Could not parse the selected process algebra expression.")

    
    
    def update_petri_net(self, parser, file_path=None):
        """Update the Petri net visualization with the parser data"""
        # Make sure we're using the correct scene type
        if not isinstance(self.scene, DraggableScene) and not isinstance(self.scene, PetriNetScene):
            print("Warning: Scene is not a PetriNetScene or DraggableScene instance")
            self.scene = DraggableScene(self)
            self.view.setScene(self.scene)
        
        # Clear and draw the Petri net
        self.scene.clear_and_draw_petri_net(parser)
        
        # Reset view to show all elements
        self.reset_view()
        
        # Start layout animation if enabled
        if self.enable_layout:
            self.layout_algorithm.initialize_layout(parser)
            self.animation_timer.start()
    
    def update_layout_parameters(self, params):
        """Update the layout algorithm parameters from settings window"""
        print(f"Received new layout parameters: {params}")
        
        # Update the algorithm with new parameters
        self.layout_algorithm.set_parameters(params)
        
        # If layout is enabled, immediately apply the new settings
        if self.enable_layout and self.parser:
            # When parameters change, reinitialize the layout with new settings
            self.layout_algorithm.initialize_layout(self.parser)
    
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
        else:
            for transition in self.parser.transitions:
                if transition['id'] == transition_id:
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