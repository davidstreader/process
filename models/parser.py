# Updated ProcessAlgebraParser with proper parentheses handling

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
                        'is_process': True,
                        'process': name
                    })
                    
                    # Map the process name to its place ID
                    self.process_places[name] = initial_place_id
            
            # Second pass: parse expressions and build Petri nets
            process_index = 0
            for name, expr in self.process_definitions.items():
                # Get the corresponding place ID
                initial_place_id = self.process_places[name]
                
                # Parse the expression (no pre-expansion)
                self._parse_expression(expr, initial_place_id, name, 0, 100 + process_index * 150)
                process_index += 1
            
            # Process pending recursive connections
            for conn in self.pending_connections:
                print(f"pending_connection conn: {conn}")
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
            print(f"Parse End self.places: {self.places}")
            print(f"          self.trans: {self.transitions}")
            return True
        except Exception as e:
            import traceback
            print(f"Parsing error: {str(e)}")
            print(traceback.format_exc())
            return False
        print(f"Parse End self.places: {self.places}")
        print(f"Parse End self.transitions: {self.transitions}")

    def _parse_expression(self, expr, source_place_id, process_name=None, depth=0, base_y=100):
        """Parse a process algebra expression and build the Petri net structure"""
        # Remove outer parentheses if present
        print(f"_parse_expression expr: {expr}")
        expr = self._remove_outer_parentheses(expr)
        
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
                # The first part is an action or parenthesized expression
                first_part = parts[0].strip()
                
                # Handle possible parentheses in the first part
                first_part = self._remove_outer_parentheses(first_part)
                
                # Create a transition for this action
                transition_id = self.get_id()
                self.transitions.append({
                    'id': transition_id,
                    'name': first_part,
                    'x': self._get_place_by_id(source_place_id)['x'] + 100,  # Position based on source place
                    'y': base_y,
                    'process': process_name
                })
                #print(f"Built Transitions: {self.transitions}")
                # Connect source place to this transition
                self.arcs.append({
                    'source_id': source_place_id,
                    'target_id': transition_id,
                    'is_place_to_transition': True
                })
                
                # Check if the next part is a process reference or continuation
                next_part = parts[1].strip()
                
                # Remove outer parentheses from next_part if present
                next_part_clean = self._remove_outer_parentheses(next_part)
                
                # Special handling for STOP
                if next_part_clean.upper() == "STOP":
                    # Create a terminal STOP place
                    stop_place_id = self.get_id()
                    self.places.append({
                        'id': stop_place_id,
                        'name': "STOP",
                        'tokens': 0,
                        'x': self._get_place_by_id(source_place_id)['x'] + 200,
                        'y': base_y,
                        'is_terminal': True,
                        'process': process_name
                    })
                    
                    # Connect transition to the STOP place
                    self.arcs.append({
                        'source_id': transition_id,
                        'target_id': stop_place_id,
                        'is_place_to_transition': False
                    })
                    return
                
                # Check if next_part is a direct process reference (without further sequence)
                elif next_part_clean in self.process_places:
                    # Get the target place ID for the process
                    target_place_id = self.process_places[next_part_clean]
                    
                    # Connect transition directly to the process place
                    self.arcs.append({
                        'source_id': transition_id,
                        'target_id': target_place_id,
                        'is_place_to_transition': False
                    })
                    return
                else:
                    # Regular continuation with an intermediate place
                    next_place_id = self.get_id()
                    self.places.append({
                        'id': next_place_id,
                        #'name': f"p{next_place_id}",
                        'name': f"",
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
                    print(f"remaining: {remaining}")
                    #print(f"self.places: {self.places}")
                return
        
        # Handle atomic actions or process references
        expr = expr.strip()
        if expr:
            # Handle possible parentheses
            expr = self._remove_outer_parentheses(expr)
            print(f"HOPEFULL expr: {expr}") 
            print(f"{self.process_places}")
            # Special handling for STOP as a standalone expression
            if expr.upper() == "STOP":
                # Create a terminal STOP place if not already connected to one
                stop_place_id = self.get_id()
                self.places.append({
                    'id': stop_place_id,
                    'name': "STOP",
                    'tokens': 0,
                    'x': self._get_place_by_id(source_place_id)['x'] + 100,
                    'y': base_y,
                    'is_terminal': True,
                    'pcess': process_name
                })
                
                # Create a transition to the STOP place
                transition_id = self.get_id()
                self.transitions.append({
                    'id': transition_id,
                    'name': "τ",  # Silent transition
                    'x': self._get_place_by_id(source_place_id)['x'] + 50,
                    'y': base_y,
                    'is_silent': True
                })
                
                # Connect source place to transition
                self.arcs.append({
                    'source_id': source_place_id,
                    'target_id': transition_id,
                    'is_place_to_transition': True
                })
                
                # Connect transition to STOP place
                self.arcs.append({
                    'source_id': transition_id,
                    'target_id': stop_place_id,
                    'is_place_to_transition': False
                })
                return
            
            # Check if this is a reference to a defined process
            elif expr in self.process_places:
                # now copy the places and transitions from expr process to 
                # the current process
                print(f"HOPE expr: {expr}")
                # Create a transition to the process place
                transition_id = self.get_id()
                self.transitions.append({
                    'id': transition_id,
                    'name': f"→{expr}",  # Arrow to indicate process jump
                    'x': self._get_place_by_id(source_place_id)['x'] + 50,
                    'y': base_y,
                    'is_recursion': True
                })
                
                # Connect source place to transition
                self.arcs.append({
                    'source_id': source_place_id,
                    'target_id': transition_id,
                    'is_place_to_transition': True
                })
                
                # Connect transition to the target process place
                target_place_id = self.process_places[expr]
                self.arcs.append({
                    'source_id': transition_id,
                    'target_id': target_place_id,
                    'is_place_to_transition': False
                })
                return
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
                    'name': "STOP" if expr.upper() == "STOP" else f"",
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
    
    def _remove_outer_parentheses(self, expr):
        """Remove outer parentheses from an expression if present"""
        expr = expr.strip()
        
        # Check if the expression is surrounded by parentheses
        if expr.startswith('(') and expr.endswith(')'):
            # Verify that these are matching outer parentheses
            open_count = 0
            for i, char in enumerate(expr):
                if char == '(':
                    open_count += 1
                elif char == ')':
                    open_count -= 1
                    # If we've found the matching closing parenthesis for the first opening one
                    # and it's the last character, then we can remove the outer parentheses
                    if open_count == 0 and i == len(expr) - 1:
                        return expr[1:-1].strip()
                    # If we close all parentheses before the end, these aren't outer parentheses
                    if open_count == 0 and i < len(expr) - 1:
                        return expr
        
        return expr
    
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
        
    def _expand_process_references(self, expr):
        """Expand process references in an expression with their definitions"""
        # We don't expand recursive self-references, only references to other processes
        
        # Track which processes have been expanded to avoid infinite recursion
        expanded = {}
        
        def expand_nonrecursive_refs(expression, current_process=None):
            """Inner function to expand references without causing recursion"""
            # No need to re-expand if we've already processed this expression
            if expression in expanded:
                return expanded[expression]
                
            result = expression
            changed = False
            
            # For each process name in our definitions
            for process_name, process_expr in self.process_definitions.items():
                # Skip self-references to avoid infinite recursion
                if process_name == current_process:
                    continue
                    
                # Look for standalone process names (not part of other identifiers)
                pattern = r'\b' + re.escape(process_name) + r'\b'
                
                # Check if we have a match
                if re.search(pattern, result):
                    # Don't replace the process if it would cause infinite recursion
                    # Instead, leave the process name as is - it will be handled during parsing
                    result = re.sub(pattern, process_name, result)
                    changed = True
            
            # Remember this expansion to avoid redundant work
            expanded[expression] = result
            return result
            
        # Start expansion with no current process (root level)
        return expand_nonrecursive_refs(expr)
        
    def get_parsing_errors(self):
        """Return any parsing errors that occurred"""
        # This is just a placeholder to handle the AttributeError mentioned in the stack trace
        return []
        
    def export_to_process_algebra(self):
        """Export the Petri net back to process algebra code"""
        # This method would generate process algebra code from the Petri net
        # It's a placeholder for now and would need to be implemented
        result = []
        
        # Recreate the process definitions
        for name, _ in self.process_definitions.items():
            # Find the initial place for this process
            place_id = self.process_places.get(name)
            if place_id is not None:
                # Recreate the process expression
                expr = self._build_expression_from_place(place_id)
                if expr:
                    result.append(f"{name} = {expr}")
        print(f"export result: {result}")
        return "\n".join(result)
    
    def _build_expression_from_place(self, place_id):
        """Build a process algebra expression starting from a place"""
        # This is a placeholder and would need to be implemented
        # The idea is to follow the Petri net structure and rebuild the expressions
        return ""