from PyQt5.QtWidgets import (QGraphicsItem, QGraphicsEllipseItem, 
                             QGraphicsRectItem, QToolTip)
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor

class DraggablePlaceItem(QGraphicsEllipseItem):
    """Interactive and draggable Place node for Petri nets"""
    
    def __init__(self, x, y, radius, place_data, parent=None):
        super().__init__(x - radius, y - radius, 2 * radius, 2 * radius, parent)
        self.place_data = place_data  # Store reference to the original data
        self.radius = radius
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        
        # Default style
        self.setPen(QPen(Qt.black, 2))
        self.setBrush(QBrush(QColor(240, 240, 255)))
        self.setZValue(1)  # Places above arcs
        
        # State tracking
        self.hover = False
        self.dragging = False
    
    def itemChange(self, change, value):
        """Handle item changes, particularly position changes"""
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            # Update the place data coordinates when the item is moved
            new_pos = value.toPointF()
            self.place_data['x'] = new_pos.x() + self.radius
            self.place_data['y'] = new_pos.y() + self.radius
            
            # Notify scene/parent that position changed for arc updates
            if self.scene() and hasattr(self.scene(), 'parent') and self.scene().parent:
                if hasattr(self.scene().parent, 'node_position_changed'):
                    self.scene().parent.node_position_changed('place', self.place_data['id'])
        
        return super().itemChange(change, value)
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        self.dragging = True
        self.setBrush(QBrush(QColor(255, 255, 150)))  # Highlight when dragging
        super().mousePressEvent(event)
        
        # Notify scene of drag start
        if self.scene() and hasattr(self.scene(), 'parent') and self.scene().parent:
            if hasattr(self.scene().parent, 'start_node_drag'):
                self.scene().parent.start_node_drag('place', self.place_data['id'])
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release after dragging"""
        self.dragging = False
        self.setBrush(QBrush(QColor(240, 240, 255)) if not self.hover else QBrush(QColor(220, 220, 255)))
        super().mouseReleaseEvent(event)
        
        # Notify scene of drag end
        if self.scene() and hasattr(self.scene(), 'parent') and self.scene().parent:
            if hasattr(self.scene().parent, 'end_node_drag'):
                self.scene().parent.end_node_drag('place', self.place_data['id'])
    
    def hoverEnterEvent(self, event):
        """Handle mouse hover enter event"""
        self.hover = True
        self.setBrush(QBrush(QColor(220, 220, 255)))  # Lighter color when hovering
        self.setCursor(Qt.OpenHandCursor)
        super().hoverEnterEvent(event)
        
        # Show tooltip with place information
        tooltip = f"<b>Place: {self.place_data['name']}</b><br>"
        tooltip += f"ID: {self.place_data['id']}<br>"
        tooltip += f"Tokens: {self.place_data['tokens']}<br>"
        tooltip += f"Position: ({self.place_data['x']:.1f}, {self.place_data['y']:.1f})"
        QToolTip.showText(event.screenPos(), tooltip)
    
    def hoverLeaveEvent(self, event):
        """Handle mouse hover leave event"""
        self.hover = False
        self.setBrush(QBrush(QColor(240, 240, 255)))  # Return to normal color
        self.setCursor(Qt.ArrowCursor)
        super().hoverLeaveEvent(event)
        
        # Hide tooltip
        QToolTip.hideText()

class DraggableTransitionItem(QGraphicsRectItem):
    """Interactive and draggable Transition node for Petri nets"""
    
    def __init__(self, x, y, width, height, transition_data, parent=None):
        super().__init__(x - width/2, y - height/2, width, height, parent)
        self.transition_data = transition_data  # Store reference to the original data
        self.width = width
        self.height = height
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        
        # Default style
        self.setPen(QPen(Qt.black, 2))
        self.setBrush(QBrush(QColor(220, 220, 220)))
        self.setZValue(1)  # Transitions above arcs
        
        # State tracking
        self.hover = False
        self.dragging = False
    
    def itemChange(self, change, value):
        """Handle item changes, particularly position changes"""
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            # Update the transition data coordinates when the item is moved
            new_pos = value.toPointF()
            self.transition_data['x'] = new_pos.x() + self.width/2
            self.transition_data['y'] = new_pos.y() + self.height/2
            
            # Notify scene/parent that position changed for arc updates
            if self.scene() and hasattr(self.scene(), 'parent') and self.scene().parent:
                if hasattr(self.scene().parent, 'node_position_changed'):
                    self.scene().parent.node_position_changed('transition', self.transition_data['id'])
        
        return super().itemChange(change, value)
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        self.dragging = True
        self.setBrush(QBrush(QColor(255, 255, 150)))  # Highlight when dragging
        super().mousePressEvent(event)
        
        # Notify scene of drag start
        if self.scene() and hasattr(self.scene(),