# Complete fixed version of the ProcessAlgebraParser

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
        self.referenced_processes = set()
        self.parsed_processes = set()
        self.parsing_errors = []
        self.main_processes = {}

    
    def reset(self):
        self.places = []
        self.transitions = []
        self.arcs = []
        self.current_id = 0
        self.process_definitions = {}
        self.process_places = {}
        self.referenced_processes = set()
        self.parsed_processes = set()
        self.parsing_errors = []
    
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
            #print(f"Process start placers: {self.process_definitions}")
            #print(f"Process places: {self.process_places}")
            # Find processes referenced by others
            for name, expr in self.process_definitions.items():
                for other_name in self.process_definitions:
                    if other_name != name:
                        pattern = r'\b' + re.escape(other_name) + r'\b'
                        if re.search(pattern, expr):
                            self.referenced_processes.add(other_name)
            print(f"Referenced processes: {self.referenced_processes}")
            # Find main processes (those not referenced)
            for name, expr in self.process_definitions.items():
                if name not in self.referenced_processes:
                     self.main_processes[name] = expr   
            #main_processes = [name for name in self.process_definitions.items() 
            #                if name not in self.referenced_processes]
            print(f"processes: {self.process_definitions}")
            print(f"Main processes: {self.main_processes}")
            
                
            #print(f"Main processes: {main_processes}")
            
            # Build the Petri net for each main process
            for i, process_name in enumerate(self.main_processes):
                if process_name in self.process_places:
                    self.build_petri_net(process_name, i)
                    
            # Now make sure all referenced processes are also parsed
            #self._build_all_referenced_processes()
            
            return True
        except Exception as e:
            import traceback
            error_msg = f"Parsing error: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            self.parsing_errors.append(error_msg)
            return False

    def _build_all_referenced_processes(self):
        """Build all referenced processes to ensure completeness"""
        # Make a list of all processes to ensure they're fully parsed
        all_processes = set(self.process_definitions.keys())
        for process_name in all_processes:
            if process_name not in self.parsed_processes and process_name in self.process_places:
                # Calculate a position based on existing processes
                position_index = len(self.parsed_processes)
                self.build_petri_net(process_name, position_index)
        
   


    def build_petri_net(self, process_name, index):
        """Build the Petri net for a process definition"""
        print(f"Building Petri net for process {process_name}")
        
        # Mark this process as parsed
        self.parsed_processes.add(process_name)
        
        place_id = self.process_places[process_name]
        expr = self.process_definitions[process_name]
        base_y = 100 + index * 150
        
        # Process the expression and build the net
        self.parse_expression(expr, place_id, process_name, base_y)
        
        # Check if this process references others and ensure they're built
        referenced = set()
        for other_name in self.process_definitions:
            if other_name != process_name:
                pattern = r'\b' + re.escape(other_name) + r'\b'
                if re.search(pattern, expr) and other_name not in self.parsed_processes:
                    referenced.add(other_name)
        
        # Build any directly referenced processes that haven't been built yet
        for ref_process in referenced:
            if ref_process not in self.parsed_processes and ref_process in self.process_places:
                # Use a new index based on current parsed processes
                ref_index = len(self.parsed_processes)
                self.build_petri_net(ref_process, ref_index)

    
    
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
        #print(f"Parsing sequence: {sequence}")
        # Split the sequence by dot operator
        parts = self.split_by_operator(sequence, '.')
        
        # Keep track of current place for the sequence
        current_place_id = place_id
        x_offset = 0
        #print(f"Parts: {parts}")
        for i, part in enumerate(parts):
            part = part.strip()
            part = self.remove_outer_parentheses(part)
                
            if len(parts) > i+1:
                look_ahead = parts[i+1]
                 # Special handling for STOP
                if look_ahead == 'STOP':
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
                    transition_id = self.create_action_transition(part, current_place_id, process_name, y_pos, x_offset)            
                 # Connect current place to transition
                    self.arcs.append({
                        'source_id': transition_id,
                        'target_id': stop_place_id,
                        'is_place_to_transition': False
                    })
                    break
                elif look_ahead  in self.process_definitions : # process the end of sequence
                    local_process_id = self.process_places[look_ahead]
                    transition_id = self.create_action_transition(part, current_place_id, process_name, y_pos, x_offset)
            
                    self.arcs.append({
                        'source_id': transition_id,
                        'target_id': self.process_places[look_ahead],
                        'is_place_to_transition': False
                    })
                    break
                #fall through to normal action
                #print(f"Fall through Part {i}: {part}")

            if    len(parts)== i +1: #last event 
                    ##print(f"Fall through at end Part {i}: {part}")
                    transition_id = self.create_action_transition(part, current_place_id, process_name, y_pos, x_offset)                               
                    print(f"Created arc from {current_place_id} to {transition_id}")
                    #adds arc from current place to transition  
            if    len(parts)> i +1:
                    #print(f"Fall through not at end Part {i}: {part}")
                    transition_id = self.create_action_transition(part, current_place_id, process_name, y_pos, x_offset)
                    
                    #print(f"Created arc from {current_place_id} to {transition_id}")
                    new_place_id = self.get_id()
                    self.places.append({
                            'id': new_place_id,
                            'name': "",
                            'tokens': 0,
                            'x': self.get_place_x(new_place_id) + 150 + x_offset,
                            'y': y_pos,
                            'is_terminal': False,
                            'process': process_name
                    })
                    #print(f"Created new place {new_place_id}")
                    self.arcs.append({
                            'source_id': transition_id, #previous transition to new place
                            'target_id': new_place_id,
                            'is_place_to_transition': False  
                    })
                    current_place_id = new_place_id
                    #print(f"Created arc from {transition_id} to {new_place_id}")                         
                
                    x_offset += 100
                    continue           
            # after loop
    
                
                
        
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
        if not self.parsing_errors:
            return ["No specific error information available. Check the console for details."]
        return self.parsing_errors