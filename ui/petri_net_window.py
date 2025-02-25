import sys
import os
from pathlib import Path

# Add parent directory to Python path to resolve module imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QGraphicsView, QCheckBox, QMessageBox,
                             QGraphicsItem, QGraphicsEllipseItem, QGraphicsRectItem,
                             QGraphicsLineItem, QGraphicsTextItem, QGraphicsScene, QToolTip)
from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QTransform

# Now import from models package
from models.layout import ForceDirectedLayout
from ui.petri_net_scene import PetriNetScene

class DraggableScene(PetriNetScene):
    """Enhanced Petri net scene with draggable nodes and tooltips"""
    
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.dragged_item = None
        self.dragged_item_type = None
        self.dragged_item_id = None
        self.place_items = {}  # Maps place IDs to their QGraphicsItems
        self.transition_items = {}  # Maps transition IDs to their QGraphicsItems
        
    def clear_and_draw_petri_net(self, parser):
        """Clear the scene and draw the Petri net with draggable items"""
        self.clear()
        self.place_items = {}
        self.transition_items = {}
        
        # Draw places (circles)
        for place in parser.places:
            ellipse = QGraphicsEllipseItem(
                place['x'] - self.place_radius, 
                place['y'] - self.place_radius,
                2 * self.place_radius, 
                2 * self.place_radius
            )
            ellipse.setPen(QPen(Qt.black, 2))
            ellipse.setBrush(QBrush(QColor(240, 240, 255)))
            ellipse.setFlag(QGraphicsItem.ItemIsMovable)
            ellipse.setFlag(QGraphicsItem.ItemIsSelectable)
            ellipse.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
            ellipse.setAcceptHoverEvents(True)
            
            # Store place data in the item for access during hover/drag
            ellipse.place_data = place
            self.addItem(ellipse)
            
            # Map this item to its ID for later reference
            self.place_items[place['id']] = ellipse
            
            # Add place name
            text = QGraphicsTextItem(place['name'])
            text.setPos(place['x'] - text.boundingRect().width() / 2,
                        place['y'] - self.place_radius - 20)
            self.addItem(text)
            
            # Add tokens (black dots)
            if place['tokens'] > 0:
                token_radius = 5
                token = QGraphicsEllipseItem(
                    place['x'] - token_radius,
                    place['y'] - token_radius,
                    2 * token_radius,
                    2 * token_radius
                )
                token.setPen(QPen(Qt.black, 1))
                token.setBrush(QBrush(Qt.black))
                self.addItem(token)
        
        # Draw transitions (rectangles)
        for transition in parser.transitions:
            rect = QGraphicsRectItem(
                transition['x'] - self.transition_width / 2,
                transition['y'] - self.transition_height / 2,
                self.transition_width,
                self.transition_height
            )
            rect.setPen(QPen(Qt.black, 2))
            rect.setBrush(QBrush(QColor(220, 220, 220)))
            rect.setFlag(QGraphicsItem.ItemIsMovable)
            rect.setFlag(QGraphicsItem.ItemIsSelectable)
            rect.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
            rect.setAcceptHoverEvents(True)
            
            # Store transition data in the item for access during hover/drag
            rect.transition_data = transition
            self.addItem(rect)
            
            # Map this item to its ID for later reference
            self.transition_items[transition['id']] = rect
            
            # Add transition name
            text = QGraphicsTextItem(transition['name'])
            text.setPos(transition['x'] - text.boundingRect().width() / 2,
                       transition['y'] - self.transition_height / 2 - 20)
            self.addItem(text)
        
        # Draw arcs (arrows) - same as before
        self.draw_arcs(parser)
        
        # Set scene rect to fit all items with some padding
        self.setSceneRect(self.itemsBoundingRect().adjusted(-50, -50, 50, 50))
    
    def draw_arcs(self, parser):
        """Draw arcs between places and transitions"""
        for arc in parser.arcs:
            source_id = arc['source_id']
            target_id = arc['target_id']
            
            start_x, start_y = 0, 0
            end_x, end_y = 0, 0
            
            # Get start and end coordinates
            if arc['is_place_to_transition']:
                # From place to transition
                for place in parser.places:
                    if place['id'] == source_id:
                        start_x, start_y = place['x'], place['y']
                        break
                
                for transition in parser.transitions:
                    if transition['id'] == target_id:
                        end_x, end_y = transition['x'], transition['y']
                        break
            else:
                # From transition to place
                for transition in parser.transitions:
                    if transition['id'] == source_id:
                        start_x, start_y = transition['x'], transition['y']
                        break
                
                for place in parser.places:
                    if place['id'] == target_id:
                        end_x, end_y = place['x'], place['y']
                        break
            
            # Calculate direction vector
            dx = end_x - start_x
            dy = end_y - start_y
            
            # Normalize vector
            length = (dx**2 + dy**2)**0.5
            if length > 0:
                dx /= length
                dy /= length
            
            # Adjust start and end points to be on the boundaries of nodes
            if arc['is_place_to_transition']:
                start_x += dx * self.place_radius
                start_y += dy * self.place_radius
                end_x -= dx * self.transition_width / 2
                end_y -= dy * self.transition_height / 2
            else:
                start_x += dx * self.transition_width / 2
                start_y += dy * self.transition_height / 2
                end_x -= dx * self.place_radius
                end_y -= dy * self.place_radius
            
            # Draw the line
            line = QGraphicsLineItem(start_x, start_y, end_x, end_y)
            line.setPen(QPen(Qt.black, 1.5))
            self.addItem(line)
            
            # Draw the arrow head (same as before)
            self.draw_arrow_head(end_x, end_y, dx, dy)
    
    def draw_arrow_head(self, end_x, end_y, dx, dy):
        """Draw arrow head at the end of an arc"""
        import math
        
        arrow_angle = 25  # degrees
        arrow_length = self.arrow_size
        
        # Calculate arrow points
        angle1 = arrow_angle * (3.14159 / 180)
        angle2 = -arrow_angle * (3.14159 / 180)
        
        arrow_dx1 = dx * math.cos(angle1) - dy * math.sin(angle1)
        arrow_dy1 = dx * math.sin(angle1) + dy * math.cos(angle1)
        
        arrow_dx2 = dx * math.cos(angle2) - dy * math.sin(angle2)
        arrow_dy2 = dx * math.sin(angle2) + dy * math.cos(angle2)
        
        arrow_point1_x = end_x - arrow_length * arrow_dx1
        arrow_point1_y = end_y - arrow_length * arrow_dy1
        
        arrow_point2_x = end_x - arrow_length * arrow_dx2
        arrow_point2_y = end_y - arrow_length * arrow_dy2
        
        # Draw the arrow head
        arrow1 = QGraphicsLineItem(end_x, end_y, arrow_point1_x, arrow_point1_y)
        arrow2 = QGraphicsLineItem(end_x, end_y, arrow_point2_x, arrow_point2_y)
        arrow1.setPen(QPen(Qt.black, 1.5))
        arrow2.setPen(QPen(Qt.black, 1.5))
        self.addItem(arrow1)
        self.addItem(arrow2)
    
    def mousePressEvent(self, event):
        """Handle mouse press events for dragging nodes"""
        item = self.itemAt(event.scenePos(), QTransform())
        
        # Check if the item is a place or transition
        if item and (hasattr(item, 'place_data') or hasattr(item, 'transition_data')):
            self.dragged_item = item
            
            if hasattr(item, 'place_data'):
                self.dragged_item_type = 'place'
                self.dragged_item_id = item.place_data['id']
            else:
                self.dragged_item_type = 'transition'
                self.dragged_item_id = item.transition_data['id']
                
            # Highlight the selected item
            item.setBrush(QBrush(QColor(255, 255, 150)))
            
            # Display detailed information tooltip
            self.show_item_tooltip(item, event.screenPos())
            
            # Let the parent handle the dragging
            if self.parent and hasattr(self.parent, 'start_node_drag'):
                self.parent.start_node_drag(self.dragged_item_type, self.dragged_item_id)
        
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events after dragging"""
        if self.dragged_item:
            # Update the node position in the data model
            if self.dragged_item_type == 'place' and hasattr(self.dragged_item, 'place_data'):
                self.dragged_item.place_data['x'] = self.dragged_item.scenePos().x() + self.place_radius
                self.dragged_item.place_data['y'] = self.dragged_item.scenePos().y() + self.place_radius
                
                # Reset the brush
                self.dragged_item.setBrush(QBrush(QColor(240, 240, 255)))
                
            elif self.dragged_item_type == 'transition' and hasattr(self.dragged_item, 'transition_data'):
                self.dragged_item.transition_data['x'] = self.dragged_item.scenePos().x() + self.transition_width / 2
                self.dragged_item.transition_data['y'] = self.dragged_item.scenePos().y() + self.transition_height / 2
                
                # Reset the brush
                self.dragged_item.setBrush(QBrush(QColor(220, 220, 220)))
            
            # Notify the parent that the drag is complete
            if self.parent and hasattr(self.parent, 'end_node_drag'):
                self.parent.end_node_drag(self.dragged_item_type, self.dragged_item_id)
            
            self.dragged_item = None
            self.dragged_item_type = None
            self.dragged_item_id = None
            
            # Need to redraw arcs to match new node positions
            if self.parent and hasattr(self.parent, 'update_arcs'):
                self.parent.update_arcs()
        
        super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events during dragging"""
        super().mouseMoveEvent(event)
        
        # Update the tooltip position if an item is being dragged
        if self.dragged_item:
            self.show_item_tooltip(self.dragged_item, event.screenPos())
    
    def hoverEnterEvent(self, event):
        """Handle hover enter events to show tooltips"""
        item = self.itemAt(event.scenePos(), QTransform())
        
        if item and (hasattr(item, 'place_data') or hasattr(item, 'transition_data')):
            self.show_item_tooltip(item, event.screenPos())
    
    def show_item_tooltip(self, item, pos):
        """Show a tooltip with node information"""
        if hasattr(item, 'place_data'):
            place = item.place_data
            tooltip = f"<b>Place: {place['name']}</b><br>"
            tooltip += f"ID: {place['id']}<br>"
            tooltip += f"Tokens: {place['tokens']}<br>"
            tooltip += f"Position: ({place['x']:.1f}, {place['y']:.1f})"
            
        elif hasattr(item, 'transition_data'):
            transition = item.transition_data
            tooltip = f"<b>Transition: {transition['name']}</b><br>"
            tooltip += f"ID: {transition['id']}<br>"
            tooltip += f"Position: ({transition['x']:.1f}, {transition['y']:.1f})"
        
        QToolTip.showText(pos, tooltip)

class PetriNetWindow(QMainWindow):
    """Window for visualizing the Petri net with force-directed layout"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Petri Net Visualization")
        self.resize(800, 600)
        
        # Create main widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # Create graphics view and scene
        self.scene = DraggableScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.NoDrag)  # We'll handle dragging ourselves
        
        # Add zoom controls
        zoom_layout = QHBoxLayout()
        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_out_button = QPushButton("Zoom Out")
        self.reset_view_button = QPushButton("Reset View")
        zoom_layout.addWidget(self.zoom_in_button)
        zoom_layout.addWidget(self.zoom_out_button)
        zoom_layout.addWidget(self.reset_view_button)
        
        # Add layout controls
        layout_control_layout = QHBoxLayout()
        self.enable_layout_checkbox = QCheckBox("Enable Spring Layout")
        self.apply_layout_button = QPushButton("Apply Full Layout")
        self.settings_button = QPushButton("Layout Settings")
        layout_control_layout.addWidget(self.enable_layout_checkbox)
        layout_control_layout.addWidget(self.apply_layout_button)
        layout_control_layout.addWidget(self.settings_button)
        
        # Add controls to main layout
        layout.addWidget(QLabel("<b>Petri Net Visualization</b>"))
        layout.addWidget(self.view)
        layout.addLayout(zoom_layout)
        layout.addLayout(layout_control_layout)
        
        self.setCentralWidget(main_widget)
        
        # Set up force-directed layout
        self.layout_algorithm = ForceDirectedLayout()
        self.enable_layout = False
        self.parser = None
        self.node_being_dragged = False
        self.node_drag_type = None
        self.node_drag_id = None
        
        # Set up animation timer
        self.animation_timer = QTimer(self)
        self.animation_timer.setInterval(50)  # 20 fps
        
        # Connect signals
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.reset_view_button.clicked.connect(self.reset_view)
        self.enable_layout_checkbox.stateChanged.connect(self.toggle_layout)
        self.apply_layout_button.clicked.connect(self.run_full_layout)
        self.animation_timer.timeout.connect(self.update_layout_step)
        
        # Allow mouse wheel zooming
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
    
    def update_petri_net(self, parser):
        """Update the Petri net visualization with the parser data"""
        self.parser = parser
        self.scene.clear_and_draw_petri_net(parser)
        self.reset_view()
        
        # Start the layout animation if enabled
        if self.enable_layout:
            self.animation_timer.start()
    
    def update_layout_parameters(self, params):
        """Update the layout algorithm parameters"""
        self.layout_algorithm.set_parameters(params)
    
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
            
            # Redraw the scene
            self.update_node_positions()
            self.scene.clear_and_draw_petri_net(self.parser)
    
    def update_node_positions(self):
        """Update the UI node positions from the parser data"""
        for place in self.parser.places:
            if place['id'] in self.scene.place_items:
                item = self.scene.place_items[place['id']]
                item.setPos(place['x'] - self.scene.place_radius, 
                            place['y'] - self.scene.place_radius)
        
        for transition in self.parser.transitions:
            if transition['id'] in self.scene.transition_items:
                item = self.scene.transition_items[transition['id']]
                item.setPos(transition['x'] - self.scene.transition_width / 2, 
                            transition['y'] - self.scene.transition_height / 2)
    
    def update_arcs(self):
        """Redraw arcs to match current node positions"""
        if self.parser:
            # Update the coordinates in the parser from the graphics items
            for place_id, item in self.scene.place_items.items():
                for place in self.parser.places:
                    if place['id'] == place_id:
                        place['x'] = item.scenePos().x() + self.scene.place_radius
                        place['y'] = item.scenePos().y() + self.scene.place_radius
                        break
            
            for transition_id, item in self.scene.transition_items.items():
                for transition in self.parser.transitions:
                    if transition['id'] == transition_id:
                        transition['x'] = item.scenePos().x() + self.scene.transition_width / 2
                        transition['y'] = item.scenePos().y() + self.scene.transition_height / 2
                        break
            
            # Just redraw the arcs portion
            self.scene.clear()
            self.scene.clear_and_draw_petri_net(self.parser)
    
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
        self.node_drag_type = node_type
        self.node_drag_id = node_id
        
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
                if transition['id'] == node_id:
                    transition['fixed'] = not self.enable_layout
                    break
    
    def end_node_drag(self, node_type, node_id):
        """Handle the end of node dragging"""
        self.node_being_dragged = False
        
        # Update the node position from the graphics item
        if node_type == 'place' and node_id in self.scene.place_items:
            item = self.scene.place_items[node_id]
            for place in self.parser.places:
                if place['id'] == node_id:
                    place['x'] = item.scenePos().x() + self.scene.place_radius
                    place['y'] = item.scenePos().y() + self.scene.place_radius
                    break
        
        elif node_type == 'transition' and node_id in self.scene.transition_items:
            item = self.scene.transition_items[node_id]
            for transition in self.parser.transitions:
                if transition['id'] == node_id:
                    transition['x'] = item.scenePos().x() + self.scene.transition_width / 2
                    transition['y'] = item.scenePos().y() + self.scene.transition_height / 2
                    break
        
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
        """Reset the view"""
        self.view.resetTransform()
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
    
    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming"""
        if event.angleDelta().y() > 0:
            factor = 1.2
        else:
            factor = 0.8
        
        self.view.scale(factor, factor)
