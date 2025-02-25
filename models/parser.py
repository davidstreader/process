import json
import re

class ProcessAlgebraParser:
    """Parser for simple process algebra expressions and conversion to Petri nets"""
    
    def __init__(self):
        self.places = []
        self.transitions = []
        self.arcs = []
        self.current_id = 0
        self.process_definitions = {}  # Store process definitions for regeneration
    
    def reset(self):
        self.places = []
        self.transitions = []
        self.arcs = []
        self.current_id = 0
        self.process_definitions = {}
    
    def get_id(self):
        self.current_id += 1
        return self.current_id - 1
    
    def parse(self, text):
        """Parse the process algebra text and convert to Petri net"""
        self.reset()
        
        # Remove comments and whitespace and split by lines
        lines = []
        for line in text.strip().split('\n'):
            # Remove comments (anything after #)
            if '#' in line:
                line = line[:line.find('#')]
            
            # Skip empty lines
            if line.strip():
                lines.append(line.strip())
        
        try:
            for line in lines:
                if '=' in line:
                    # Process definition
                    name, expr = line.split('=', 1)
                    name = name.strip()
                    expr = expr.strip()
                    
                    # Store the process definition for regeneration
                    self.process_definitions[name] = expr
                    
                    # Create initial place
                    initial_place_id = self.get_id()
                    self.places.append({
                        'id': initial_place_id,
                        'name': name,
                        'tokens': 1,
                        'x': 50,
                        'y': 50 + 80 * len(self.places),
                        'is_process': True  # Mark this as a process place
                    })
                    
                    # Parse the right side of the equation
                    self._parse_expression(expr, initial_place_id, name)
            
            # Basic layout adjustment
            self._adjust_layout()
            
            return True
        except Exception as e:
            print(f"Parsing error: {str(e)}")
            return False
    
    def _parse_expression(self, expr, source_place_id, process_name=None, depth=0):
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
                'y': 50 + 80 * len(self.transitions) % 5,
                'process': process_name  # Store which process this belongs to
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
                'y': 50 + 80 * (len(self.places) % 5),
                'process': process_name  # Store which process this belongs to
            })
            
            # Connect transition to the new place
            self.arcs.append({
                'source_id': transition_id,
                'target_id': new_place_id,
                'is_place_to_transition': False
            })
            
            # Process the rest recursively
            if len(parts) > 1 and parts[1].strip():
                self._parse_expression(parts[1].strip(), new_place_id, process_name, depth + 1)
                
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
                        'y': 50 + 80 * len(self.transitions) % 5,
                        'process': process_name  # Store which process this belongs to
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
                        'y': 50 + 80 * (len(self.places) % 5),
                        'process': process_name  # Store which process this belongs to
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
                # Check if this is a reference to another process
                if expr in self.process_definitions:
                    # Create a recursive arc back to the process start place
                    for place in self.places:
                        if place.get('is_process') and place['name'] == expr:
                            # Create transition for the recursion
                            transition_id = self.get_id()
                            self.transitions.append({
                                'id': transition_id,
                                'name': f"→{expr}",  # Arrow indicates recursion
                                'x': 150 + 100 * depth,
                                'y': 50 + 80 * len(self.transitions) % 5,
                                'process': process_name,  # Store which process this belongs to
                                'is_recursion': True
                            })
                            
                            # Connect source place to this transition
                            self.arcs.append({
                                'source_id': source_place_id,
                                'target_id': transition_id,
                                'is_place_to_transition': True
                            })
                            
                            # Connect transition to the process place
                            self.arcs.append({
                                'source_id': transition_id,
                                'target_id': place['id'],
                                'is_place_to_transition': False
                            })
                            break
                else:
                    # Create transition for the action
                    transition_id = self.get_id()
                    self.transitions.append({
                        'id': transition_id,
                        'name': expr,
                        'x': 150 + 100 * depth,
                        'y': 50 + 80 * len(self.transitions) % 5,
                        'process': process_name  # Store which process this belongs to
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
                        'y': 50 + 80 * (len(self.places) % 5),
                        'process': process_name  # Store which process this belongs to
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
    
    def export_to_process_algebra(self):
        """Generate process algebra code from the current Petri net"""
        # This is a simplified approach and may not perfectly reconstruct the original code
        
        # Find all processes (places marked as processes)
        process_places = [p for p in self.places if p.get('is_process', False)]
        
        # Sort processes by y-coordinate to maintain original order
        process_places.sort(key=lambda p: p['y'])
        
        result = []
        
        for place in process_places:
            process_name = place['name']
            
            # Build expressions for this process
            expressions = self._build_expression_for_process(place['id'])
            
            if expressions:
                result.append(f"{process_name} = {' + '.join(expressions)}")
        
        return '\n'.join(result)
    
    def _build_expression_for_process(self, place_id):
        """Build expressions starting from this place"""
        expressions = []
        
        # Find all outgoing arcs from this place
        outgoing_arcs = [a for a in self.arcs if a['source_id'] == place_id and a['is_place_to_transition']]
        
        for arc in outgoing_arcs:
            transition_id = arc['target_id']
            
            # Find the transition
            transition = next((t for t in self.transitions if t['id'] == transition_id), None)
            if not transition:
                continue
            
            # Find the outgoing arc from this transition
            next_arc = next((a for a in self.arcs if a['source_id'] == transition_id and not a['is_place_to_transition']), None)
            if not next_arc:
                expressions.append(transition['name'])
                continue
            
            next_place_id = next_arc['target_id']
            
            # Check if this is recursion to a process
            next_place = next((p for p in self.places if p['id'] == next_place_id), None)
            if next_place and next_place.get('is_process', False):
                expressions.append(f"{transition['name']}.{next_place['name']}")
            else:
                # Continue building the expression recursively
                sub_expressions = self._build_expression_for_process(next_place_id)
                for sub_expr in sub_expressions:
                    expressions.append(f"{transition['name']}.{sub_expr}")
        
        return expressions
    
    def load_from_file(self, data):
        """Load Petri net from JSON file data"""
        self.reset()
        
        # Load the data
        self.places = data.get('places', [])
        self.transitions = data.get('transitions', [])
        self.arcs = data.get('arcs', [])
        
        # Calculate the next available ID
        max_place_id = max([p['id'] for p in self.places]) if self.places else -1
        max_trans_id = max([t['id'] for t in self.transitions]) if self.transitions else -1
        self.current_id = max(max_place_id, max_trans_id) + 1
        
        # Reconstruct process definitions for export
        self._reconstruct_process_definitions()
        
        return True
    
    def _reconstruct_process_definitions(self):
        """Reconstruct process definitions from the Petri net structure"""
        # Start by finding all process places (places with tokens)
        process_places = [p for p in self.places if p.get('tokens', 0) > 0]
        
        for place in process_places:
            process_name = place['name']
            
            # Build expression for this process
            expressions = self._build_expression_for_process(place['id'])
            
            if expressions:
                self.process_definitions[process_name] = ' + '.join(expressions)
