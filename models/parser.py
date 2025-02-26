# Update this in models/parser.py

import re
import math

class ProcessAlgebraParser:
    """Parser for simple process algebra expressions and conversion to Petri nets"""
    
    def __init__(self):
        self.places = []
        self.transitions = []
        self.arcs = []
        self.current_id = 0
        self.process_definitions = {}  # Store process definitions for regeneration
        self.process_places = {}       # Maps process names to their place IDs
        self.pending_connections = []  # Store pending recursive connections
    
    def reset(self):
        """Reset all data structures"""
        self.places = []
        self.transitions = []
        self.arcs = []
        self.current_id = 0
        self.process_definitions = {}
        self.process_places = {}
        self.pending_connections = []
    
    def get_id(self):
        """Get a unique ID for new elements"""
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
            # First pass: register all process definitions
            for line in lines:
                if '=' in line:
                    # Process definition: P = a.b + c.d
                    name, expr = line.split('=', 1)
                    name = name.strip()
                    expr = expr.strip()
                    
                    # Store the process definition
                    self.process_definitions[name] = expr
                    
                    # Create initial place for the process
                    initial_place_id = self.get_id()
                    self.places.append({
                        'id': initial_place_id,
                        'name': name,
                        'tokens': 1,  # Start with a token
                        'x': 100,     # Initial x position
                        'y': 100 + len(self.process_places) * 150,  # Position based on number of processes
                        'is_process': True
                    })
                    
                    # Map the process name to its place ID
                    self.process_places[name] = initial_place_id
            
            # Second pass: parse expressions and build Petri nets
            process_index = 0
            for line in lines:
                if '=' in line:
                    name, expr = line.split('=', 1)
                    name = name.strip()
                    expr = expr.strip()
                    
                    # Get the corresponding place ID
                    initial_place_id = self.process_places[name]
                    
                    # Parse the expression
                    self._parse_expression(expr, initial_place_id, name, 0, 100 + process_index * 150)
                    process_index += 1
            
            # Process pending recursive connections
            for conn in self.pending_connections:
                source_place_id, target_process_name = conn
                
                if target_process_name in self.process_places:
                    target_place_id = self.process_places[target_process_name]
                    
                    # Create a transition for the connection
                    transition_id = self.get_id()
                    self.transitions.append({
                        'id': transition_id,
                        'name': f"→{target_process_name}",  # Arrow to indicate recursion
                        'x': self._get_place_by_id(source_place_id)['x'] + 100,
                        'y': self._get_place_by_id(source_place_id)['y'],
                        'is_recursion': True
                    })
                    
                    # Connect source place to this transition
                    self.arcs.append({
                        'source_id': source_place_id,
                        'target_id': transition_id,
                        'is_place_to_transition': True
                    })
                    
                    # Connect transition to the target process place
                    self.arcs.append({
                        'source_id': transition_id,
                        'target_id': target_place_id,
                        'is_place_to_transition': False
                    })
            
            return True
        except Exception as e:
            import traceback
            print(f"Parsing error: {str(e)}")
            print(traceback.format_exc())
            return False
    
    def _parse_expression(self, expr, source_place_id, process_name=None, depth=0, base_y=100):
        """Parse a process algebra expression and build the Petri net structure"""
        # Handle choice operator (+) first to split the expression
        if '+' in expr and not self._is_in_parentheses(expr, expr.find('+')):
            choices = self._split_by_operator(expr, '+')
            for i, choice in enumerate(choices):
                # Create a separate branch for each choice
                self._parse_expression(choice.strip(), source_place_id, process_name, depth, base_y + i * 80)
            return
        
        # Handle sequential composition (.)
        if '.' in expr and not self._is_in_parentheses(expr, expr.find('.')):
            parts = self._split_by_first_operator(expr, '.')
            if len(parts) >= 2:
                # The first part is an action
                action = parts[0].strip()
                
                # Create a transition for this action
                transition_id = self.get_id()
                self.transitions.append({
                    'id': transition_id,
                    'name': action,
                    'x': self._get_place_by_id(source_place_id)['x'] + 100,  # Position based on source place
                    'y': base_y,
                    'process': process_name
                })
                
                # Connect source place to this transition
                self.arcs.append({
                    'source_id': source_place_id,
                    'target_id': transition_id,
                    'is_place_to_transition': True
                })
                
                # Check if the next part is a process reference or continuation
                next_part = parts[1].strip()
                
                # If this is a direct process reference at the end (like a.b.P)
                if next_part in self.process_places and len(parts) == 2:
                    # Direct connection back to a process place
                    target_place_id = self.process_places[next_part]
                    
                    # Connect transition directly to the process place
                    self.arcs.append({
                        'source_id': transition_id,
                        'target_id': target_place_id,
                        'is_place_to_transition': False
                    })
                else:
                    # Regular continuation with an intermediate place
                    next_place_id = self.get_id()
                    self.places.append({
                        'id': next_place_id,
                        'name': f"p{next_place_id}",
                        'tokens': 0,
                        'x': self._get_place_by_id(source_place_id)['x'] + 200,  # Position based on source place
                        'y': base_y,
                        'process': process_name
                    })
                    
                    # Connect transition to the new place
                    self.arcs.append({
                        'source_id': transition_id,
                        'target_id': next_place_id,
                        'is_place_to_transition': False
                    })
                    
                    # Process the rest of the expression
                    remaining = '.'.join(parts[1:])
                    self._parse_expression(remaining, next_place_id, process_name, depth + 1, base_y)
                
                return
        
        # Handle atomic actions or process references
        expr = expr.strip()
        if expr:
            # Check if this is a reference to a defined process
            if expr in self.process_places:
                # Add this to pending connections to be processed later
                self.pending_connections.append((source_place_id, expr))
            else:
                # Regular action (or undefined process - treat as action)
                transition_id = self.get_id()
                self.transitions.append({
                    'id': transition_id,
                    'name': expr,
                    'x': self._get_place_by_id(source_place_id)['x'] + 100,
                    'y': base_y,
                    'process': process_name
                })
                
                # Connect source place to this transition
                self.arcs.append({
                    'source_id': source_place_id,
                    'target_id': transition_id,
                    'is_place_to_transition': True
                })
                
                # Create a terminal place if this is the end of a sequence
                terminal_place_id = self.get_id()
                self.places.append({
                    'id': terminal_place_id,
                    'name': "STOP" if expr.upper() == "STOP" else f"p{terminal_place_id}",
                    'tokens': 0,
                    'x': self._get_place_by_id(source_place_id)['x'] + 200,
                    'y': base_y,
                    'process': process_name
                })
                
                # Connect transition to the terminal place
                self.arcs.append({
                    'source_id': transition_id,
                    'target_id': terminal_place_id,
                    'is_place_to_transition': False
                })
    
    def _get_place_by_id(self, place_id):
        """Get a place by its ID"""
        for place in self.places:
            if place['id'] == place_id:
                return place
        return {'x': 100, 'y': 100}  # Default if not found
    
    def _is_in_parentheses(self, expr, pos):
        """Check if the character at position is inside parentheses"""
        if pos < 0 or pos >= len(expr):
            return False
        
        open_count = 0
        for i in range(pos):
            if expr[i] == '(':
                open_count += 1
            elif expr[i] == ')':
                open_count -= 1
        
        return open_count > 0
    
    def _split_by_operator(self, expr, operator):
        """Split expression by an operator, respecting parentheses"""
        result = []
        start = 0
        paren_level = 0
        
        for i, char in enumerate(expr):
            if char == '(':
                paren_level += 1
            elif char == ')':
                paren_level -= 1
            elif char == operator and paren_level == 0:
                result.append(expr[start:i])
                start = i + 1
        
        # Add the last part
        if start < len(expr):
            result.append(expr[start:])
        
        return result
    
    def _split_by_first_operator(self, expr, operator):
        """Split expression by the first occurrence of an operator, respecting parentheses"""
        paren_level = 0
        
        for i, char in enumerate(expr):
            if char == '(':
                paren_level += 1
            elif char == ')':
                paren_level -= 1
            elif char == operator and paren_level == 0:
                return [expr[:i], expr[i+1:]]
        
        # If no operator found, return the entire expression
        return [expr]