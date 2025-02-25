import math
from PyQt5.QtWidgets import (QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem,
                            QGraphicsRectItem, QGraphicsLineItem, QGraphicsTextItem,
                            QToolTip, QGraphicsSceneMouseEvent)
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPen, QBrush, QColor, QTransform, QFont

class PetriNetScene(QGraphicsScene):
    """Graphics scene for rendering interactive Petri nets"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.place_radius = 20
        self.transition_width = 40
        self.transition_height = 40
        self.arrow_size = 10
        self.parent_window = parent
        
        # Keep track of interactive items
        self.place_items = {}  # Maps place IDs to their QGraphicsItems
        self.transition_items = {}  # Maps transition IDs to their QGraphicsItems
        self.text_items = {}  # Maps node IDs to their label items
        self.token_items = {}  # Maps place IDs to their token items
        
        # Drag state tracking
        self.dragged_item = None
        self.dragged_item_type = None
        self.dragged_item_id = None
        self.drag_start_pos = None
    
    def clear_and_draw_petri_net(self, parser):
        """Clear the scene and draw the Petri net from the parser data"""
        self.clear()
        self.place_items.clear()
        self.transition_items.clear()
        self.text_items.clear()
        self.token_items.clear()
        
        # Draw places (circles)
        for place in parser.places:
            # Create the place circle
            ellipse = QGraphicsEllipseItem(
                place['x'] - self.place_radius, 
                place['y'] - self.place_radius,
                2 * self.place_radius, 
                2 * self.place_radius
            )
            ellipse.setPen(QPen(Qt.black, 2))
            ellipse.setBrush(QBrush(QColor(240, 240, 255)))
            
            # Make it interactive
            ellipse.setFlag(QGraphicsItem.ItemIsMovable)
            ellipse.setFlag(QGraphicsItem.ItemIsSelectable)
            ellipse.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
            ellipse.setAcceptHoverEvents(True)
            
            # Store the place data in the item for easy access
            ellipse.place_data = place
            ellipse.node_type = 'place'
            ellipse.node_id = place['id']
            
            self.addItem(ellipse)
            self.place_items[place['id']] = ellipse
            
            # Add place name
            text = QGraphicsTextItem(place['name'])
            text.setPos(place['x'] - text.boundingRect().width() / 2,
                        place['y'] - self.place_radius - 20)
            self.addItem(text)
            self.text_items[f"p{place['id']}"] = text
            
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
                self.token_items[place['id']] = token
        
        # Draw transitions (rectangles)
        for transition in parser.transitions:
            # Create the transition rectangle
            rect = QGraphicsRectItem(
                transition['x'] - self.transition_width / 2,
                transition['y'] - self.transition_height / 2,
                self.transition_width,
                self.transition_height
            )
            rect.setPen(QPen(Qt.black, 2))
            rect.setBrush(QBrush(QColor(220, 220, 220)))
            
            # Make it interactive
            rect.setFlag(QGraphicsItem.ItemIsMovable)
            rect.setFlag(QGraphicsItem.ItemIsSelectable)
            rect.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
            rect.setAcceptHoverEvents(True)
            
            # Store the transition data in the item
            rect.transition_data = transition
            rect.node_type = 'transition'
            rect.node_id = transition['id']
            
            self.addItem(rect)
            self.transition_items[transition['id']] = rect
            
            # Add transition name
            text = QGraphicsTextItem(transition['name'])
            text.setPos(transition['x'] - text.boundingRect().width() / 2,
                       transition['y'] - self.transition_height / 2 - 20)
            self.addItem(text)
            self.text_items[f"t{transition['id']}"] = text
        
        # Draw arcs (arrows)
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
            line.setZValue(-1)  # Make lines appear below nodes
            self.addItem(line)
            
            # Draw the arrow head
            self.draw_arrow_head(end_x, end_y, dx, dy)
    
    def draw_arrow_head(self, end_x, end_y, dx, dy):
        """Draw arrow head at the end of an arc"""
        arrow_angle = 25  # degrees
        arrow_length = self.arrow_size
        
        # Calculate arrow points
        angle1 = arrow_angle * (math.pi / 180)
        angle2 = -arrow_angle * (math.pi / 180)
        
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
        arrow1.setZValue(-1)  # Make arrow below nodes
        arrow2.setZValue(-1)
        self.addItem(arrow1)
        self.addItem(arrow2)
    
    def mousePressEvent(self, event):
        """Handle mouse press events for dragging nodes"""
        item = self.itemAt(event.scenePos(), QTransform())
        
        if item and hasattr(item, 'node_type'):
            # Store the selected item for dragging
            self.dragged_item = item
            self.dragged_item_type = item.node_type
            self.dragged_item_id = item.node_id
            self.drag_start_pos = event.scenePos()
            
            # Highlight selected item
            if self.dragged_item_type == 'place':
                item.setBrush(QBrush(QColor(255, 255, 150)))  # Yellow highlight
            else:
                item.setBrush(QBrush(QColor(255, 220, 150)))  # Orange highlight
            
            # Display tooltip with node information
            if self.dragged_item_type == 'place':
                place = item.place_data
                tooltip = f"<b>Place: {place['name']}</b><br>"
                tooltip += f"ID: {place['id']}<br>"
                tooltip += f"Tokens: {place['tokens']}<br>"
                tooltip += f"Position: ({place['x']:.1f}, {place['y']:.1f})"
            else:
                transition = item.transition_data
                tooltip = f"<b>Transition: {transition['name']}</b><br>"
                tooltip += f"ID: {transition['id']}<br>"
                tooltip += f"Position: ({transition['x']:.1f}, {transition['y']:.1f})"
            
            QToolTip.showText(event.screenPos(), tooltip)
            
            # If parent window has a drag handler, notify it
            if self.parent_window and hasattr(self.parent_window, 'start_node_drag'):
                self.parent_window.start_node_drag(self.dragged_item_type, self.dragged_item_id)
        
        # Handle the event using the normal mechanism
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events after dragging"""
        if self.dragged_item:
            # Update the data model with the new position
            if self.dragged_item_type == 'place':
                place_data = self.dragged_item.place_data
                # Center position is offset from top-left by radius
                place_data['x'] = self.dragged_item.scenePos().x() + self.place_radius
                place_data['y'] = self.dragged_item.scenePos().y() + self.place_radius
                
                # Reset the highlight
                self.dragged_item.setBrush(QBrush(QColor(240, 240, 255)))
                
            elif self.dragged_item_type == 'transition':
                transition_data = self.dragged_item.transition_data
                # Center position is offset from top-left by half width/height
                transition_data['x'] = self.dragged_item.scenePos().x() + self.transition_width / 2
                transition_data['y'] = self.dragged_item.scenePos().y() + self.transition_height / 2
                
                # Reset the highlight
                self.dragged_item.setBrush(QBrush(QColor(220, 220, 220)))
            
            # Also update the position of the label
            if self.dragged_item_type == 'place':
                text_item = self.text_items.get(f"p{self.dragged_item_id}")
                if text_item:
                    text_item.setPos(
                        self.dragged_item.place_data['x'] - text_item.boundingRect().width() / 2,
                        self.dragged_item.place_data['y'] - self.place_radius - 20
                    )
                
                # Update token position if any
                token_item = self.token_items.get(self.dragged_item_id)
                if token_item:
                    token_radius = 5
                    token_item.setPos(
                        self.dragged_item.place_data['x'] - token_radius,
                        self.dragged_item.place_data['y'] - token_radius
                    )
            
            elif self.dragged_item_type == 'transition':
                text_item = self.text_items.get(f"t{self.dragged_item_id}")
                if text_item:
                    text_item.setPos(
                        self.dragged_item.transition_data['x'] - text_item.boundingRect().width() / 2,
                        self.dragged_item.transition_data['y'] - self.transition_height / 2 - 20
                    )
            
            # Notify parent window that dragging has ended
            if self.parent_window and hasattr(self.parent_window, 'end_node_drag'):
                self.parent_window.end_node_drag(self.dragged_item_type, self.dragged_item_id)
                
                # Request a redraw of arcs to match new node positions
                if hasattr(self.parent_window, 'update_arcs'):
                    self.parent_window.update_arcs()
            
            # Clear the dragging state
            self.dragged_item = None
            self.dragged_item_type = None
            self.dragged_item_id = None
            self.drag_start_pos = None
        
        # Handle the event using the normal mechanism
        super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events during dragging"""
        # First, let the parent class handle the actual movement
        super().mouseMoveEvent(event)
        
        # Then update any labels or tokens that should move with nodes
        if self.dragged_item and self.drag_start_pos:
            # Update tooltip position
            if self.dragged_item_type == 'place':
                place_data = self.dragged_item.place_data
                tooltip = f"<b>Place: {place_data['name']}</b><br>"
                tooltip += f"ID: {place_data['id']}<br>"
                tooltip += f"Tokens: {place_data['tokens']}<br>"
                tooltip += f"Position: ({place_data['x']:.1f}, {place_data['y']:.1f})"
            else:
                transition_data = self.dragged_item.transition_data
                tooltip = f"<b>Transition: {transition_data['name']}</b><br>"
                tooltip += f"ID: {transition_data['id']}<br>"
                tooltip += f"Position: ({transition_data['x']:.1f}, {transition_data['y']:.1f})"
            
            QToolTip.showText(event.screenPos(), tooltip)
    
    def hoverEnterEvent(self, event):
        """Show tooltip when hovering over nodes"""
        item = self.itemAt(event.scenePos(), QTransform())
        
        if item and hasattr(item, 'node_type'):
            if item.node_type == 'place':
                place_data = item.place_data
                tooltip = f"<b>Place: {place_data['name']}</b><br>"
                tooltip += f"ID: {place_data['id']}<br>"
                tooltip += f"Tokens: {place_data['tokens']}"
            else:
                transition_data = item.transition_data
                tooltip = f"<b>Transition: {transition_data['name']}</b><br>"
                tooltip += f"ID: {transition_data['id']}"
            
            QToolTip.showText(event.screenPos(), tooltip)
            
        super().hoverEnterEvent(event)
    
    def update_node_positions(self, parser):
        """Update graphics items positions based on the parser data model"""
        # Update places
        for place in parser.places:
            place_item = self.place_items.get(place['id'])
            if place_item:
                place_item.setPos(
                    place['x'] - self.place_radius,
                    place['y'] - self.place_radius
                )
                
                # Update the associated text label
                text_item = self.text_items.get(f"p{place['id']}")
                if text_item:
                    text_item.setPos(
                        place['x'] - text_item.boundingRect().width() / 2,
                        place['y'] - self.place_radius - 20
                    )
                
                # Update token position if any
                token_item = self.token_items.get(place['id'])
                if token_item:
                    token_radius = 5
                    token_item.setPos(
                        place['x'] - token_radius,
                        place['y'] - token_radius
                    )
        
        # Update transitions
        for transition in parser.transitions:
            transition_item = self.transition_items.get(transition['id'])
            if transition_item:
                transition_item.setPos(
                    transition['x'] - self.transition_width / 2,
                    transition['y'] - self.transition_height / 2
                )
                
                # Update the associated text label
                text_item = self.text_items.get(f"t{transition['id']}")
                if text_item:
                    text_item.setPos(
                        transition['x'] - text_item.boundingRect().width() / 2,
                        transition['y'] - self.transition_height / 2 - 20
                    )
        
        # Redraw arcs to match updated positions
        self.clear()
        self.clear_and_draw_petri_net(parser)
