import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTextEdit, QPushButton, QLabel, 
                           QSplitter, QGraphicsView, QGraphicsScene, 
                           QGraphicsEllipseItem, QGraphicsRectItem, 
                           QGraphicsLineItem, QGraphicsTextItem, QMessageBox)
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPen, QBrush, QColor, QFont

class ProcessAlgebraParser:
    """Parser for simple process algebra expressions and conversion to Petri nets"""   
    def __init__(self):
        self.places = []
        self.transitions = []
        self.arcs = []
        self.current_id = 0
    
    def reset(self):
        self.places = []
        self.transitions = []
        self.arcs = []
        self.current_id = 0
    
    def get_id(self):
        self.current_id += 1
        return self.current_id - 1
    
    def parse(self, text):
        """Parse the process algebra text and convert to Petri net"""
        self.reset()
        
        # Remove whitespace and split by lines
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        
        try:
            for line in lines:
                if '=' in line:
                    # Process definition
                    name, expr = line.split('=', 1)
                    name = name.strip()
                    expr = expr.strip()
                    
                    # Create initial place
                    initial_place_id = self.get_id()
                    self.places.append({
                        'id': initial_place_id,
                        'name': name,
                        'tokens': 1,
                        'x': 50,
                        'y': 50 + 80 * len(self.places)
                    })
                    
                    # Parse the right side of the equation
                    self._parse_expression(expr, initial_place_id)
            
            # Basic layout adjustment
            self._adjust_layout()
            
            return True
        except Exception as e:
            print(f"Parsing error: {str(e)}")
            return False
    def export_to_process_algebra(self):
        """Export the current Petri net back to process algebra code"""
        if not self.places or not self.transitions or not self.arcs:
            return ""
        
        # Reconstruct process definitions from the Petri net
        process_code = {}
        
        # First, identify all process places (places with tokens)
        process_places = {}
        for place in self.places:
            if place.get('is_process', False) or place.get('tokens', 0) > 0:
                process_places[place['id']] = place['name']
        
        # For each process place, reconstruct its definition
        for place_id, process_name in process_places.items():
            # Get all outgoing arcs from this place
            outgoing_arcs = [arc for arc in self.arcs if arc['source_id'] == place_id and arc['is_place_to_transition']]
            
            # If no outgoing arcs, this is a terminal process
            if not outgoing_arcs:
                process_code[process_name] = "STOP"
                continue
            
            # Collect all branches from this process
            branches = []
            
            for arc in outgoing_arcs:
                transition_id = arc['target_id']
                
                # Find the transition
                transition = next((t for t in self.transitions if t['id'] == transition_id), None)
                if not transition:
                    continue
                
                # Get the action name
                action = transition['name']
                
                # Find where this transition leads to
                next_arcs = [arc for arc in self.arcs if arc['source_id'] == transition_id and not arc['is_place_to_transition']]
                
                if not next_arcs:
                    # Transition leads nowhere, treat as STOP
                    branches.append(f"{action}.STOP")
                else:
                    for next_arc in next_arcs:
                        target_place_id = next_arc['target_id']
                        target_place = next((p for p in self.places if p['id'] == target_place_id), None)
                        
                        if not target_place:
                            continue
                        
                        if target_place_id in process_places:
                            # This is a recursive reference to another process
                            branches.append(f"{action}.{process_places[target_place_id]}")
                        else:
                            # This is a continuation to another action sequence
                            # Find the next action from this place
                            continuation = self._get_continuation_from_place(target_place_id)
                            if continuation:
                                branches.append(f"{action}.{continuation}")
                            else:
                                branches.append(f"{action}.STOP")
            
            # Join all branches with choice operator
            if branches:
                process_code[process_name] = " + ".join(branches)
        
        # Combine all process definitions
        result = []
        for name, expr in process_code.items():
            result.append(f"{name} = {expr}")
        
        return "\n".join(result)

    def _get_continuation_from_place(self, place_id, visited=None):
        """Recursively get the continuation sequence from a place"""
        if visited is None:
            visited = set()
        
        if place_id in visited:
            return "STOP"  # Avoid infinite recursion
        
        visited.add(place_id)
        
        # Get all outgoing arcs from this place
        outgoing_arcs = [arc for arc in self.arcs if arc['source_id'] == place_id and arc['is_place_to_transition']]
        
        if not outgoing_arcs:
            return "STOP"
        
        # If multiple outgoing arcs, this is a choice point
        if len(outgoing_arcs) > 1:
            branches = []
            for arc in outgoing_arcs:
                transition_id = arc['target_id']
                transition = next((t for t in self.transitions if t['id'] == transition_id), None)
                if not transition:
                    continue
                
                next_arcs = [arc for arc in self.arcs if arc['source_id'] == transition_id and not arc['is_place_to_transition']]
                if not next_arcs:
                    branches.append(f"{transition['name']}.STOP")
                else:
                    for next_arc in next_arcs:
                        target_place_id = next_arc['target_id']
                        continuation = self._get_continuation_from_place(target_place_id, visited.copy())
                        branches.append(f"{transition['name']}.{continuation}")
            
            return " + ".join(branches)
        
        # Single outgoing arc - linear sequence
        transition_id = outgoing_arcs[0]['target_id']
        transition = next((t for t in self.transitions if t['id'] == transition_id), None)
        if not transition:
            return "STOP"
        
        next_arcs = [arc for arc in self.arcs if arc['source_id'] == transition_id and not arc['is_place_to_transition']]
        if not next_arcs:
            return f"{transition['name']}.STOP"
        
        target_place_id = next_arcs[0]['target_id']
        target_place = next((p for p in self.places if p['id'] == target_place_id), None)
        
        if not target_place:
            return f"{transition['name']}.STOP"
        
        # Check if this is a reference to a named process
        for place in self.places:
            if place['id'] == target_place_id and (place.get('is_process', False) or place.get('tokens', 0) > 0):
                return f"{transition['name']}.{place['name']}"
        
        # Continue recursively
        continuation = self._get_continuation_from_place(target_place_id, visited.copy())
        return f"{transition['name']}.{continuation}"



    def _parse_expression(self, expr, source_place_id, depth=0):
        # Basic sequential composition with '.'
        if '.' in expr:
            parts = expr.split('.', 1)
            
            # Process the first part (action)
            transition_id = self.get_id()
            action = parts[0].strip()
            
            # Create transition for the action
            self.transitions.append({
                'id': transition_id,
                'name': action,
                'x': 150 + 100 * depth,
                'y': 50 + 80 * len(self.transitions) % 5
            })
            
            # Connect source place to this transition
            self.arcs.append({
                'source_id': source_place_id,
                'target_id': transition_id,
                'is_place_to_transition': True
            })
            
            # Create a new place for the result of this action
            new_place_id = self.get_id()
            self.places.append({
                'id': new_place_id,
                'name': f"p{new_place_id}",
                'tokens': 0,
                'x': 250 + 100 * depth,
                'y': 50 + 80 * (len(self.places) % 5)
            })
            
            # Connect transition to the new place
            self.arcs.append({
                'source_id': transition_id,
                'target_id': new_place_id,
                'is_place_to_transition': False
            })
            
            # Process the rest recursively
            if len(parts) > 1 and parts[1].strip():
                self._parse_expression(parts[1].strip(), new_place_id, depth + 1)
                
        # Choice with '+'
        elif '+' in expr:
            parts = expr.split('+')
            
            for part in parts:
                part = part.strip()
                if part:
                    # For each choice, create a transition
                    transition_id = self.get_id()
                    
                    # Create transition for the action
                    self.transitions.append({
                        'id': transition_id,
                        'name': part,
                        'x': 150 + 100 * depth,
                        'y': 50 + 80 * len(self.transitions) % 5
                    })
                    
                    # Connect source place to this transition
                    self.arcs.append({
                        'source_id': source_place_id,
                        'target_id': transition_id,
                        'is_place_to_transition': True
                    })
                    
                    # Create a new place for the result
                    new_place_id = self.get_id()
                    self.places.append({
                        'id': new_place_id,
                        'name': f"p{new_place_id}",
                        'tokens': 0,
                        'x': 250 + 100 * depth,
                        'y': 50 + 80 * (len(self.places) % 5)
                    })
                    
                    # Connect transition to the new place
                    self.arcs.append({
                        'source_id': transition_id,
                        'target_id': new_place_id,
                        'is_place_to_transition': False
                    })
        
        # Atomic action (no operators)
        else:
            expr = expr.strip()
            if expr:
                # Create transition for the action
                transition_id = self.get_id()
                self.transitions.append({
                    'id': transition_id,
                    'name': expr,
                    'x': 150 + 100 * depth,
                    'y': 50 + 80 * len(self.transitions) % 5
                })
                
                # Connect source place to this transition
                self.arcs.append({
                    'source_id': source_place_id,
                    'target_id': transition_id,
                    'is_place_to_transition': True
                })
                
                # Create a new place for the result
                new_place_id = self.get_id()
                self.places.append({
                    'id': new_place_id,
                    'name': f"p{new_place_id}",
                    'tokens': 0,
                    'x': 250 + 100 * depth,
                    'y': 50 + 80 * (len(self.places) % 5)
                })
                
                # Connect transition to the new place
                self.arcs.append({
                    'source_id': transition_id,
                    'target_id': new_place_id,
                    'is_place_to_transition': False
                })
    
    def _adjust_layout(self):
        """Simple layout adjustment to avoid overlapping elements"""
        # This is a very basic layout algorithm
        # A more sophisticated algorithm would use proper graph layout techniques
        
        # Set y-coordinates to avoid overlap
        place_y = 50
        for place in self.places:
            place['y'] = place_y
            place_y += 80
        
        transition_y = 50
        for transition in self.transitions:
            transition['y'] = transition_y
            transition_y += 80

class PetriNetScene(QGraphicsScene):
    """Graphics scene for rendering the Petri net"""
    
    def __init__(self):
        super().__init__()
        self.place_radius = 20
        self.transition_width = 40
        self.transition_height = 40
        self.arrow_size = 10
    
    def clear_and_draw_petri_net(self, parser):
        """Clear the scene and draw the Petri net from the parser data"""
        self.clear()
        
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
            self.addItem(ellipse)
            
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
            self.addItem(rect)
            
            # Add transition name
            text = QGraphicsTextItem(transition['name'])
            text.setPos(transition['x'] - text.boundingRect().width() / 2,
                       transition['y'] - self.transition_height / 2 - 20)
            self.addItem(text)
        
        # Draw arcs (arrows)
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
            
            # Draw the arrow head
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
        
        # Set scene rect to fit all items with some padding
        self.setSceneRect(self.itemsBoundingRect().adjusted(-50, -50, 50, 50))

class TextEditorWindow(QMainWindow):
    """Window for entering process algebra text"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Process Algebra Editor")
        self.resize(500, 600)
        
        # Create main widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # Create text editor
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Enter process algebra expressions here...\nExample:\nP = a.b + c.d\nQ = e.f.P")
        layout.addWidget(QLabel("<b>Process Algebra Editor</b>"))
        layout.addWidget(self.text_edit)
        
        # Create buttons
        button_layout = QHBoxLayout()
        self.visualize_button = QPushButton("Visualize Petri Net")
        self.clear_button = QPushButton("Clear")
        button_layout.addWidget(self.visualize_button)
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)
        
        # Add example button
        self.example_button = QPushButton("Load Example")
        layout.addWidget(self.example_button)
        
        self.setCentralWidget(main_widget)
        
        # Connect signals
        self.clear_button.clicked.connect(self.text_edit.clear)
        
        # Set up the parser
        self.parser = ProcessAlgebraParser()
    
    def load_example(self):
        """Load an example process algebra expression"""
        example = """# Simple Process Algebra Example
P = a.b.P + c.d.STOP
Q = e.P + f.g.Q
MAIN = P | Q"""
        self.text_edit.setText(example)

class PetriNetWindow(QMainWindow):
    """Window for visualizing the Petri net"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Petri Net Visualization")
        self.resize(800, 600)
        
        # Create main widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # Create graphics view and scene
        self.scene = PetriNetScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        
        # Add zoom controls
        zoom_layout = QHBoxLayout()
        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_out_button = QPushButton("Zoom Out")
        self.reset_view_button = QPushButton("Reset View")
        zoom_layout.addWidget(self.zoom_in_button)
        zoom_layout.addWidget(self.zoom_out_button)
        zoom_layout.addWidget(self.reset_view_button)
        
        layout.addWidget(QLabel("<b>Petri Net Visualization</b>"))
        layout.addWidget(self.view)
        layout.addLayout(zoom_layout)
        
        self.setCentralWidget(main_widget)
        
        # Connect zoom signals
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.reset_view_button.clicked.connect(self.reset_view)
        
        # Allow mouse wheel zooming
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
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
    
    def update_petri_net(self, parser):
        """Update the Petri net visualization"""
        self.scene.clear_and_draw_petri_net(parser)
        self.reset_view()

import math
from PyQt5.QtGui import QPainter

def main():
    # Create the application
    app = QApplication(sys.argv)
    
    # Create both windows
    text_editor = TextEditorWindow()
    petri_net_window = PetriNetWindow()
    
    # Connect the visualize button to update the Petri net
    def visualize_petri_net(self):
        """Parse the text and visualize the Petri net"""
        text = self.text_edit.toPlainText()
        if text.strip():
            success = self.parser.parse(text)
            if success:
                self.petri_net_window.update_petri_net(self.parser)
                # Make sure Petri net window is visible
                self.petri_net_window.show()
                self.petri_net_window.show_visualization_screen()
                self.petri_net_window.raise_()
            else:
                QMessageBox.warning(self, "Parsing Error", 
                            "Could not parse the process algebra expression. Check syntax.")
    
    text_editor.visualize_button.clicked.connect(visualize_petri_net)
    text_editor.example_button.clicked.connect(text_editor.load_example)
    
    # Show both windows
    text_editor.show()
    
    # Start the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()