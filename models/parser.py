# Accurate Process Algebra Parser that properly handles process references

import re
import math

class ProcessAlgebraParser:
    def __init__(self):
        self.places = []
        self.transitions = []
        self.arcs = []
        self.current_id = 0
        self.process_definitions = {}
        self.process_places = {}
    
    def reset(self):
        self.places = []
        self.transitions = []
        self.arcs = []
        self.current_id = 0
        self.process_definitions = {}
        self.process_places = {}
    
    def get_id(self):
        self.current_id += 1
        return self.current_id - 1
    
    def parse(self, text):
        self.reset()
        
        # Remove comments and whitespace
        lines = []
        for line in text.strip().split('\n'):
            if '#' in line:
                line = line[:line.find('#')]
            if line.strip():
                lines.append(line.strip())
        
        try:
            # First pass: collect all process definitions
            for line in lines:
                if '=' in line:
                    name, expr = line.split('=', 1)
                    name = name.strip()
                    expr = expr.strip()
                    self.process_definitions[name] = expr
                    
                    # Create place for process
                    place_id = self.get_id()
                    self.places.append({
                        'id': place_id,
                        'name': name,
                        'tokens': 1,
                        'x': 100,
                        'y': 100 + len(self.process_places) * 150,
                        'is_process': True,
                        'process': name
                    })
                    self.process_places[name] = place_id
            
            # Find main processes
            main_processes = self.find_main_processes()
            print(f"Main processes: {main_processes}")
            
            # Second pass: create Petri net for main processes only
            for i, process_name in enumerate(main_processes):
                if process_name in self.process_places:
                    self.build_petri_net(process_name, i)
            
            return True
        except Exception as e:
            import traceback
            print(f"Parsing error: {str(e)}")
            print(traceback.format_exc())
            return False
    
    def find_main_processes(self):
        """Find processes that don't appear on the right-hand side of other processes"""
        referenced_processes = set()
        
        for name, expr in self.process_definitions.items():
            for other_name in self.process_definitions:
                if other_name != name:
                    pattern = r'\b' + re.escape(other_name) + r'\b'
                    if re.search(pattern, expr):
                        referenced_processes.add(other_name)
        
        main_processes = [name for name in self.process_definitions.keys() 
                          if name not in referenced_processes]
        
        if not main_processes:
            main_processes = list(self.process_definitions.keys())
        
        return main_processes
    
    def build_petri_net(self, process_name, index):
        """Build the Petri net for a process definition"""
        place_id = self.process_places[process_name]
        expr = self.process_definitions[process_name]
        base_y = 100 + index * 150
        
        # Process the expression
        self.parse_expression(expr, place_id, process_name, base_y)
    
    def parse_expression(self, expr, place_id, process_name, base_y):
        """Parse a process algebra expression and build the Petri net"""
        expr = self.remove_outer_parentheses(expr)
        
        # Handle choice operator
        if '+' in expr and not self.is_in_parentheses(expr, expr.find('+')):
            choices = self.split_by_operator(expr, '+')
            for i, choice in enumerate(choices):
                self.parse_sequence(choice.strip(), place_id, process_name, base_y + i * 80)
        else:
            self.parse_sequence(expr, place_id, process_name, base_y)
    
    def parse_sequence(self, sequence, place_id, process_name, y_pos):
        """Parse a sequence like a.b.P"""
        sequence = self.remove_outer_parentheses(sequence)
        
        # Split the sequence by dot operator
        parts = self.split_by_operator(sequence, '.')
        
        # Keep track of current place for the sequence
        current_place_id = place_id
        x_offset = 0
        
        for i, part in enumerate(parts):
            part = part.strip()
            part = self.remove_outer_parentheses(part)
            
            if not part:
                continue
                
            # Special handling for STOP
            if part.upper() == 'STOP':
                # Create STOP place
                stop_place_id = self.get_id()
                self.places.append({
                    'id': stop_place_id,
                    'name': 'STOP',
                    'tokens': 0,
                    'x': self.get_place_x(current_place_id) + 150 + x_offset,
                    'y': y_pos,
                    'is_terminal': True,
                    'process': process_name
                })
                
                # Create silent transition
                transition_id = self.get_id()
                self.transitions.append({
                    'id': transition_id,
                    'name': 'τ',
                    'x': self.get_place_x(current_place_id) + 75 + x_offset,
                    'y': y_pos,
                    'is_silent': True
                })
                
                # Connect current place to transition
                self.arcs.append({
                    'source_id': current_place_id,
                    'target_id': transition_id,
                    'is_place_to_transition': True
                })
                
                # Connect transition to STOP place
                self.arcs.append({
                    'source_id': transition_id,
                    'target_id': stop_place_id,
                    'is_place_to_transition': False
                })
                
                # Update current place
                current_place_id = stop_place_id
                x_offset += 150
                continue
            
            # Check if this is a process reference
            if part in self.process_definitions:
                # Check if this is the last part in the sequence
                if i == len(parts) - 1:
                    # This is the last part - create recursive reference or
                    # expand the process definition
                    
                    # If reference to current process, create recursive loop
                    if part == process_name:
                        # Create transition for recursion
                        transition_id = self.get_id()
                        self.transitions.append({
                            'id': transition_id,
                            'name': 'τ',
                            'x': self.get_place_x(current_place_id) + 75 + x_offset,
                            'y': y_pos,
                            'is_recursion': True
                        })
                        
                        # Connect current place to transition
                        self.arcs.append({
                            'source_id': current_place_id,
                            'target_id': transition_id,
                            'is_place_to_transition': True
                        })
                        
                        # Connect transition back to process place
                        self.arcs.append({
                            'source_id': transition_id,
                            'target_id': place_id,
                            'is_place_to_transition': False
                        })
                    else:
                        # Reference to another process - expand it inline
                        ref_expr = self.process_definitions[part]
                        
                        # Expand the referenced process with correct actions
                        self.expand_process_reference(ref_expr, current_place_id, process_name, y_pos, x_offset)
                else:
                    # Process reference in middle of sequence - treat as normal action
                    # (because it needs to be followed by more actions)
                    self.create_action_transition(part, current_place_id, process_name, y_pos, x_offset)
                    
                    # Get the next place ID
                    next_place_id = self.get_id()
                    self.places.append({
                        'id': next_place_id,
                        'name': '',
                        'tokens': 0,
                        'x': self.get_place_x(current_place_id) + 150 + x_offset,
                        'y': y_pos,
                        'process': process_name
                    })
                    
                    # Update current place
                    current_place_id = next_place_id
                    x_offset += 150
            else:
                # This is a regular action
                transition_id = self.create_action_transition(part, current_place_id, process_name, y_pos, x_offset)
                
                # Create next place if this isn't the last part
                if i < len(parts) - 1:
                    next_place_id = self.get_id()
                    self.places.append({
                        'id': next_place_id,
                        'name': '',
                        'tokens': 0,
                        'x': self.get_place_x(current_place_id) + 150 + x_offset,
                        'y': y_pos,
                        'process': process_name
                    })
                    
                    # Connect transition to next place
                    self.arcs.append({
                        'source_id': transition_id,
                        'target_id': next_place_id,
                        'is_place_to_transition': False
                    })
                    
                    # Update current place
                    current_place_id = next_place_id
                else:
                    # This is the last part - create a terminal place
                    terminal_place_id = self.get_id()
                    self.places.append({
                        'id': terminal_place_id,
                        'name': '',
                        'tokens': 0,
                        'x': self.get_place_x(current_place_id) + 150 + x_offset,
                        'y': y_pos,
                        'process': process_name
                    })
                    
                    # Connect transition to terminal place
                    self.arcs.append({
                        'source_id': transition_id,
                        'target_id': terminal_place_id,
                        'is_place_to_transition': False
                    })
                
                x_offset += 150
    
    def expand_process_reference(self, expr, place_id, process_name, y_pos, x_offset=0):
        """Expand a process reference inline with its actions"""
        expr = self.remove_outer_parentheses(expr)
        
        # Handle choice operator
        if '+' in expr and not self.is_in_parentheses(expr, expr.find('+')):
            choices = self.split_by_operator(expr, '+')
            for i, choice in enumerate(choices):
                self.parse_sequence(choice.strip(), place_id, process_name, y_pos + i * 40)
        else:
            # Parse the first action in the sequence
            parts = self.split_by_operator(expr, '.')
            if parts:
                first_part = parts[0].strip()
                first_part = self.remove_outer_parentheses(first_part)
                
                if first_part:
                    # Create transition for first action
                    transition_id = self.create_action_transition(first_part, place_id, process_name, y_pos, x_offset)
                    
                    # Create next place
                    next_place_id = self.get_id()
                    self.places.append({
                        'id': next_place_id,
                        'name': '',
                        'tokens': 0,
                        'x': self.get_place_x(place_id) + 150 + x_offset,
                        'y': y_pos,
                        'process': process_name
                    })
                    
                    # Connect transition to next place
                    self.arcs.append({
                        'source_id': transition_id,
                        'target_id': next_place_id,
                        'is_place_to_transition': False
                    })
                    
                    # Continue with rest of sequence if any
                    if len(parts) > 1:
                        rest = '.'.join(parts[1:])
                        self.parse_sequence(rest, next_place_id, process_name, y_pos)
    
    def create_action_transition(self, action, place_id, process_name, y_pos, x_offset=0):
        """Create a transition for an action"""
        # Create transition
        transition_id = self.get_id()
        self.transitions.append({
            'id': transition_id,
            'name': action,
            'x': self.get_place_x(place_id) + 75 + x_offset,
            'y': y_pos,
            'process': process_name
        })
        
        # Connect place to transition
        self.arcs.append({
            'source_id': place_id,
            'target_id': transition_id,
            'is_place_to_transition': True
        })
        
        return transition_id
    
    def get_place_x(self, place_id):
        """Get the x coordinate of a place"""
        for place in self.places:
            if place['id'] == place_id:
                return place['x']
        return 100  # Default
    
    def remove_outer_parentheses(self, expr):
        """Remove outer parentheses from an expression"""
        expr = expr.strip()
        
        if expr.startswith('(') and expr.endswith(')'):
            # Check if these are matching outer parentheses
            open_count = 0
            for i, char in enumerate(expr):
                if char == '(':
                    open_count += 1
                elif char == ')':
                    open_count -= 1
                    if open_count == 0 and i == len(expr) - 1:
                        return expr[1:-1].strip()
                    if open_count == 0 and i < len(expr) - 1:
                        return expr
        
        return expr
    
    def is_in_parentheses(self, expr, pos):
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
    
    def split_by_operator(self, expr, operator):
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
    
    def get_parsing_errors(self):
        """Return any parsing errors"""
        return []
        
    def export_to_process_algebra(self):
        """Export the Petri net back to process algebra code"""
        result = []
        
        for name, expr in self.process_definitions.items():
            result.append(f"{name} = {expr}")
        
        return "\n".join(result)