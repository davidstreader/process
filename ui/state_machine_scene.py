# Add this to a new file: ui/state_machine_scene.py

from PyQt5.QtWidgets import (QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem,
                            QGraphicsRectItem, QGraphicsLineItem, QGraphicsTextItem,
                            QToolTip)
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPen, QBrush, QColor, QTransform
import math

class StateMachineScene(QGraphicsScene):
    """Graphics scene for rendering state machines derived from Petri nets"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state_radius = 30
        self.arrow_size = 10
        self.parent_window = parent
        
        # Track items for interaction
        self.state_items = {}
        self.transition_items = {}
        
    def clear_and_draw_state_machine(self, state_machine):
        """Clear the scene and draw the state machine"""
        # Clear the scene
        self.clear()
        self.state_items = {}
        self.transition_items = {}
        
        # Debug: Print what we're drawing
        print(f"Drawing state machine with {len(state_machine['states'])} states, {len(state_machine['edges'])} transitions")
        
        # Position states in a circle
        self._position_states_in_circle(state_machine['states'])
        
        # Draw states (circles)
        for state in state_machine['states']:
            self.draw_state(state)
        
        # Draw transitions (arrows)
        for edge in state_machine['edges']:
            self.draw_transition(edge, state_machine['states'])
            
        # Add title
        title = QGraphicsTextItem(state_machine['name'])
        title.setPos(0, -50)
        title.setDefaultTextColor(QColor(0, 0, 128))
        font = title.font()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        self.addItem(title)
        
        # Set scene rect to fit all items with padding
        self.setSceneRect(self.itemsBoundingRect().adjusted(-50, -50, 50, 50))
    
    def _position_states_in_circle(self, states):
        """Position states in a circle layout"""
        num_states = len(states)
        radius = max(150, num_states * 40)  # Adjust circle size based on state count
        center_x, center_y = 0, 0
        
        # First pass: assign positions
        for i, state in enumerate(states):
            angle = 2 * math.pi * i / num_states
            state['x'] = center_x + radius * math.cos(angle)
            state['y'] = center_y + radius * math.sin(angle)
    
    def draw_state(self, state):
        """Draw a state in the state machine"""
        # Create state circle
        ellipse = QGraphicsEllipseItem(
            state['x'] - self.state_radius, 
            state['y'] - self.state_radius,
            2 * self.state_radius, 
            2 * self.state_radius
        )
        
        # Style the state differently if it's initial
        if state.get('is_initial', False):
            ellipse.setPen(QPen(QColor(0, 100, 0), 3))
            ellipse.setBrush(QBrush(QColor(200, 255, 200)))
        else:
            ellipse.setPen(QPen(Qt.black, 2))
            ellipse.setBrush(QBrush(QColor(240, 240, 255)))
        
        self.addItem(ellipse)
        self.state_items[state['id']] = ellipse
        
        # Add state ID
        id_text = QGraphicsTextItem(f"S{state['id']}")
        id_text.setPos(state['x'] - id_text.boundingRect().width() / 2,
                       state['y'] - 10)
        font = id_text.font()
        font.setBold(True)
        id_text.setFont(font)
        self.addItem(id_text)
        
        # Add places text (below the state)
        if 'place_names' in state and state['place_names']:
            places_text = ", ".join(state['place_names'])
        else:
            places_text = ", ".join([f"P{p}" for p in state['places']])
            
        places_item = QGraphicsTextItem(places_text)
        places_item.setPos(state['x'] - places_item.boundingRect().width() / 2,
                           state['y'] + self.state_radius + 5)
        self.addItem(places_item)
        
        return ellipse
    
    def draw_transition(self, edge, states):
        """Draw a transition between states"""
        source_id = edge['source']
        target_id = edge['target']
        name = edge['name']
        
        # Find the source and target states
        source_state = next((s for s in states if s['id'] == source_id), None)
        target_state = next((s for s in states if s['id'] == target_id), None)
        
        if not source_state or not target_state:
            print(f"Could not find states for edge {source_id} -> {target_id}")
            return
        
        # Get start and end points
        start_x, start_y = source_state['x'], source_state['y']
        end_x, end_y = target_state['x'], target_state['y']
        
        # Calculate direction vector
        dx = end_x - start_x
        dy = end_y - start_y
        
        # Handle self-loops
        if source_id == target_id:
            return self._draw_self_loop(source_state, name)
        
        # Normalize vector
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            dx /= length
            dy /= length
        
        # Adjust start and end points to be on the boundaries of states
        start_x += dx * self.state_radius
        start_y += dy * self.state_radius
        end_x -= dx * self.state_radius
        end_y -= dy * self.state_radius
        
        # Draw the line
        line = QGraphicsLineItem(start_x, start_y, end_x, end_y)
        line.setPen(QPen(Qt.black, 1.5))
        self.addItem(line)
        
        # Draw the arrow head
        arrow_items = self._draw_arrow_head(end_x, end_y, dx, dy)
        
        # Add label for the transition
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        
        # Offset the label perpendicular to the line
        perp_dx = -dy * 15  # Perpendicular offset
        perp_dy = dx * 15
        
        label = QGraphicsTextItem(name)
        label.setPos(mid_x + perp_dx - label.boundingRect().width() / 2,
                     mid_y + perp_dy - label.boundingRect().height() / 2)
        
        # Add background to make text more readable
        rect = label.boundingRect()
        bg_rect = QGraphicsRectItem(
            rect.x(), rect.y(), 
            rect.width(), rect.height()
        )
        bg_rect.setBrush(QBrush(QColor(255, 255, 255, 200)))
        bg_rect.setPen(QPen(Qt.NoPen))
        bg_rect.setPos(mid_x + perp_dx - label.boundingRect().width() / 2,
                      mid_y + perp_dy - label.boundingRect().height() / 2)
        self.addItem(bg_rect)
        self.addItem(label)
    
    def _draw_self_loop(self, state, name):
        """Draw a self-loop transition"""
        # Define the loop arc
        x, y = state['x'], state['y']
        r = self.state_radius
        
        # Draw an arc above the state
        from PyQt5.QtGui import QPainterPath
        
        path = QPainterPath()
        path.moveTo(x, y - r)  # Start at top of state
        path.arcTo(x - r - 20, y - r - 40, 2 * r + 40, 40, 180, -180)  # Arc above state
        
        # Create path item
        from PyQt5.QtWidgets import QGraphicsPathItem
        path_item = QGraphicsPathItem(path)
        path_item.setPen(QPen(Qt.black, 1.5))
        self.addItem(path_item)
        
        # Add arrow head
        self._draw_arrow_head(x, y - r, 0, -1)
        
        # Add label
        label = QGraphicsTextItem(name)
        label.setPos(x - label.boundingRect().width() / 2, y - r - 40)
        
        # Add label background
        rect = label.boundingRect()
        bg_rect = QGraphicsRectItem(
            rect.x(), rect.y(), 
            rect.width(), rect.height()
        )
        bg_rect.setBrush(QBrush(QColor(255, 255, 255, 200)))
        bg_rect.setPen(QPen(Qt.NoPen))
        bg_rect.setPos(x - label.boundingRect().width() / 2, y - r - 40)
        self.addItem(bg_rect)
        self.addItem(label)
    
    def _draw_arrow_head(self, end_x, end_y, dx, dy):
        """Draw arrow head at the end of a transition"""
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