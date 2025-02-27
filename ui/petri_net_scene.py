# Update this in ui/petri_net_scene.py

import math
from PyQt5.QtWidgets import (QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem,
                            QGraphicsRectItem, QGraphicsLineItem, QGraphicsTextItem,
                            QToolTip)
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPen, QBrush, QColor, QTransform

class PetriNetScene(QGraphicsScene):
    """Graphics scene for rendering Petri nets"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.place_radius = 20
        self.transition_width = 40
        self.transition_height = 40
        self.arrow_size = 10
        self.parent_window = parent
        
        # Track items for interaction
        self.place_items = {}
        self.transition_items = {}
        self.arc_items = {}    # Store arc line items for redrawing
        self.parser = None     # Store reference to parser for arc redrawing
    
    def clear_and_draw_petri_net(self, parser):
        """Clear the scene and draw the Petri net from parser data"""
        self.clear()
        self.place_items = {}
        self.transition_items = {}
        self.arc_items = {}
        self.parser = parser   # Store reference to parser
        
        # Draw places (circles)
        for place in parser.places:
            self.draw_place(place)
        
        # Draw transitions (rectangles)
        for transition in parser.transitions:
            self.draw_transition(transition)
        
        # Draw arcs (arrows)
        self.draw_arcs(parser)
        
        # Set scene rect to fit all items with padding
        self.setSceneRect(self.itemsBoundingRect().adjusted(-50, -50, 50, 50))
    
    def draw_place(self, place):
        """Draw a place in the Petri net"""
        # Create place circle
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
        ellipse.setFlag(QGraphicsItem.ItemSendsGeometryChanges)  # Important for movement tracking
        
        # Store reference to the original data
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
        
        # Add tokens if any
        if place.get('tokens', 0) > 0:
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
        
        return ellipse
    
    def draw_transition(self, transition):
        """Draw a transition in the Petri net"""
        # Create transition rectangle
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
        rect.setFlag(QGraphicsItem.ItemSendsGeometryChanges)  # Important for movement tracking
        
        # Store reference to the original data
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
        
        return rect
    
    def itemChange(self, change, value):
        """Handle changes to items in the scene"""
        return super().itemChange(change, value)
    
    def mousePressEvent(self, event):
        """Handle mouse press on scene items"""
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release after drag"""
        # Check if we need to redraw arcs
        if hasattr(self, 'last_moved_item') and self.last_moved_item:
            # Redraw all arcs when a node is released
            self.redraw_arcs()
            self.last_moved_item = None
        
        super().mouseReleaseEvent(event)
    
    def draw_arcs(self, parser):
        """Draw arcs between places and transitions"""
        # Clear any existing arc items
        for arc_id in self.arc_items:
            for item in self.arc_items[arc_id]:
                if item in self.items():
                    self.removeItem(item)
        self.arc_items = {}
        
        # Draw each arc
        for i, arc in enumerate(parser.arcs):
            source_id = arc['source_id']
            target_id = arc['target_id']
            
            # Initialize coordinates
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
            
            # Skip if coordinates not found
            if start_x == 0 and start_y == 0:
                continue
            if end_x == 0 and end_y == 0:
                continue
            
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
            arc_id = f"{source_id}_{target_id}"
            self.arc_items[arc_id] = []
            
            line = QGraphicsLineItem(start_x, start_y, end_x, end_y)
            line.setPen(QPen(Qt.black, 1.5))
            self.addItem(line)
            self.arc_items[arc_id].append(line)
            
            # Draw the arrow head
            arrow_items = self.draw_arrow_head(end_x, end_y, dx, dy)
            self.arc_items[arc_id].extend(arrow_items)
    
    def draw_arrow_head(self, end_x, end_y, dx, dy):
        """Draw arrow head at the end of an arc"""
        arrow_items = []
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
        self.addItem(arrow1)
        self.addItem(arrow2)
        
        arrow_items.append(arrow1)
        arrow_items.append(arrow2)
        
        return arrow_items
    
    def redraw_arcs(self):
        """Redraw all arcs after a node has moved"""
        if not self.parser:
            return
        
        # Update the parser data with current node positions
        for place_id, item in self.place_items.items():
            for place in self.parser.places:
                if place['id'] == place_id:
                    center = item.sceneBoundingRect().center()
                    place['x'] = center.x()
                    place['y'] = center.y()
                    break
        
        for transition_id, item in self.transition_items.items():
            for transition in self.parser.transitions:
                if transition['id'] == transition_id:
                    center = item.sceneBoundingRect().center()
                    transition['x'] = center.x()
                    transition['y'] = center.y()
                    break
        
        # Redraw arcs
        self.draw_arcs(self.parser)
        
          
class DraggableScene(PetriNetScene):
    """Enhanced PetriNetScene with draggable elements and arc redrawing"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dragged_item = None
        self.last_position = None
        # Track related items (labels, tokens) for each node
        self.node_related_items = {}  # {node_id: {type: [items]}}
    
    def clear_and_draw_petri_net(self, parser):
        """Override to track related items"""
        # Clear tracking dictionaries
        self.node_related_items = {}
        
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
        
        # Call the parent implementation after initialization
        super().clear_and_draw_petri_net(parser)
    
    def draw_place(self, place):
        """Enhanced place drawing to track labels and tokens"""
        # Create the place circle
        ellipse = self._create_place_item(place)
        self.addItem(ellipse)
        self.place_items[place['id']] = ellipse
        
        # Add place name
        text = QGraphicsTextItem(place['name'])
        text.setPos(place['x'] - text.boundingRect().width() / 2,
                    place['y'] - self.place_radius - 20)
        self.addItem(text)
        
        # Track the label
        place_key = f"p{place['id']}"
        # Ensure the dictionary entry exists
        if place_key not in self.node_related_items:
            self.node_related_items[place_key] = {"labels": [], "tokens": []}
            
        self.node_related_items[place_key]["labels"].append(text)
        
        # Add tokens if any
        if place.get('tokens', 0) > 0:
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
            
            # Track the token
            self.node_related_items[place_key]["tokens"].append(token)
        
        return ellipse
    
    def draw_transition(self, transition):
        """Enhanced transition drawing to track labels"""
        # Create the transition rectangle
        rect = self._create_transition_item(transition)
        self.addItem(rect)
        self.transition_items[transition['id']] = rect
        
        # Add transition name
        text = QGraphicsTextItem(transition['name'])
        text.setPos(transition['x'] - text.boundingRect().width() / 2,
                   transition['y'] - self.transition_height / 2 - 20)
        self.addItem(text)
        
        # Track the label
        transition_key = f"t{transition['id']}"
        # Ensure the dictionary entry exists
        if transition_key not in self.node_related_items:
            self.node_related_items[transition_key] = {"labels": []}
            
        self.node_related_items[transition_key]["labels"].append(text)
        
        return rect
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging nodes"""
        item = self.itemAt(event.scenePos(), QTransform())
        
        # Store the dragged item if it's a place or transition
        if hasattr(item, 'node_type'):
            self.dragged_item = item
            self.last_position = event.scenePos()
            
            # Highlight the selected item
            if item.node_type == 'place':
                item.setBrush(QBrush(QColor(255, 255, 150)))
            else:
                item.setBrush(QBrush(QColor(255, 220, 150)))
            
            # Notify parent window if needed
            if self.parent_window and hasattr(self.parent_window, 'start_node_drag'):
                self.parent_window.start_node_drag(item.node_type, item.node_id)
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse movement during dragging"""
        # Let Qt handle the actual movement
        super().mouseMoveEvent(event)
        
        # Update related items if a node is being dragged
        if self.dragged_item:
            self.update_related_items_position()
            
            # Store the last moved item for redrawing arcs
            self.last_moved_item = self.dragged_item
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release after dragging"""
        if self.dragged_item:
            # Reset highlight
            if self.dragged_item.node_type == 'place':
                self.dragged_item.setBrush(QBrush(QColor(240, 240, 255)))
            else:
                self.dragged_item.setBrush(QBrush(QColor(220, 220, 220)))
            
            # Update the data model with new position
            if self.dragged_item.node_type == 'place':
                center = self.dragged_item.sceneBoundingRect().center()
                self.dragged_item.place_data['x'] = center.x()
                self.dragged_item.place_data['y'] = center.y()
            else:
                center = self.dragged_item.sceneBoundingRect().center()
                self.dragged_item.transition_data['x'] = center.x()
                self.dragged_item.transition_data['y'] = center.y()
            
            # Final update of related items
            self.update_related_items_position()
            
            # Redraw all arcs to update connections
            self.redraw_arcs()
            
            # Notify parent window if needed
            if self.parent_window and hasattr(self.parent_window, 'end_node_drag'):
                self.parent_window.end_node_drag(self.dragged_item.node_type, 
                                                self.dragged_item.node_id)
            
            self.dragged_item = None
            self.last_position = None
        
        super().mouseReleaseEvent(event)
    
    def update_related_items_position(self):
        """Update positions of labels and tokens when a node is dragged"""
        if not self.dragged_item:
            return
        
        # Get the node type and ID
        node_type = self.dragged_item.node_type
        node_id = self.dragged_item.node_id
        node_key = f"{'p' if node_type == 'place' else 't'}{node_id}"
        
        # Get the new center position of the node
        center = self.dragged_item.sceneBoundingRect().center()
        x, y = center.x(), center.y()
        
        # Update label positions
        if node_key in self.node_related_items and 'labels' in self.node_related_items[node_key]:
            for label in self.node_related_items[node_key]['labels']:
                # Position the label above the node
                label.setPos(x - label.boundingRect().width() / 2, 
                             y - (self.place_radius if node_type == 'place' else self.transition_height/2) - 20)
        
        # Update token positions (for places only)
        if node_type == 'place' and node_key in self.node_related_items and 'tokens' in self.node_related_items[node_key]:
            for token in self.node_related_items[node_key]['tokens']:
                # Token should be centered within the place
                token_radius = token.rect().width() / 2
                token.setPos(x - token_radius, y - token_radius)
    
    def _create_place_item(self, place):
        """Create a draggable place item"""
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
        
        # Store reference to the original data
        ellipse.place_data = place
        ellipse.node_type = 'place'
        ellipse.node_id = place['id']
        
        return ellipse
    
    def _create_transition_item(self, transition):
        """Create a draggable transition item"""
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
        
        # Store reference to the original data
        rect.transition_data = transition
        rect.node_type = 'transition'
        rect.node_id = transition['id']
        
        return rect