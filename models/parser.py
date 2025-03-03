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
        self.petri_nets = {}  # Dictionary to store petri nets with their data
        self.current_net = None  # Track the current net being viewed
    
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
        # Keep petri_nets dictionary intact when resetting
    x_toggal = True
    y_toggal = True
     
    def get_id(self):
        self.current_id += 1
        return self.current_id - 1
        
    ################
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
            
            # Find processes referenced by others
            for name, expr in self.process_definitions.items():
                for other_name in self.process_definitions:
                    if other_name != name:
                        pattern = r'\b' + re.escape(other_name) + r'\b'
                        if re.search(pattern, expr):
                            self.referenced_processes.add(other_name)
            
            # Find main processes (those not referenced)
            for name in self.process_definitions:
                if name not in self.referenced_processes:
                    self.main_processes[name] = self.process_definitions[name]
            
            # Create places for all processes (with tokens only for main processes)
            for name in self.process_definitions:
                place_id = self.get_id()
                # Only add tokens to main processes
                tokens = 1 if name in self.main_processes else 0
                
                self.places.append({
                    'id': place_id,
                    'name': name,
                    'tokens': tokens,
                    'x': 100,
                    'y': 100 + len(self.process_places) * 150,
                    'is_process': True,
                    'process': name,
                    'is_main': name in self.main_processes
                })
                self.process_places[name] = place_id
            
            # Build the Petri net for each process
            for i, process_name in enumerate(self.process_definitions):
                if process_name in self.process_places:
                    self.build_petri_net(process_name, i)
            
            # Create petri_net entry for the current parse
            net_name = next(iter(self.main_processes)) if self.main_processes else "Unnamed Net"
            self.store_current_petri_net(net_name, text)
            
            return True
        except Exception as e:
            import traceback
            error_msg = f"Parsing error: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            self.parsing_errors.append(error_msg)
            return False
    # ##############    
    
    def store_current_petri_net(self, name, source_text):
        """Store the current Petri net data with its name"""
        print(f"parser Storing current Petri net with name {name}")
        net_id = name.lower().replace(" ", "_")
        
        # Create a deep copy of the current state
        import copy
        
        # Store all the data needed to recreate this net
        self.petri_nets[net_id] = {
            'name': name,
            'source_text': source_text,
            'places': copy.deepcopy(self.places),
            'transitions': copy.deepcopy(self.transitions),
            'arcs': copy.deepcopy(self.arcs),
            'process_definitions': copy.deepcopy(self.process_definitions),
            'process_places': copy.deepcopy(self.process_places),
            'main_processes': copy.deepcopy(self.main_processes),
            'last_id': self.current_id
        }
        
        # Set as current net
        self.current_net = net_id
        
        return net_id

    def load_petri_net(self, net_id):
        """Load a previously stored Petri net as the current net"""
        if net_id not in self.petri_nets:
            return False
        
        # Reset the current state
        self.reset()
        
        # Load the stored net data
        net_data = self.petri_nets[net_id]
        self.places = net_data['places']
        self.transitions = net_data['transitions']
        self.arcs = net_data['arcs']
        self.process_definitions = net_data['process_definitions']
        self.process_places = net_data['process_places']
        self.main_processes = net_data['main_processes']
        self.current_id = net_data['last_id']
        
        # Set as current net
        self.current_net = net_id
        
        return True

    def _build_all_referenced_processes(self):
        """Build all referenced processes to ensure completeness"""
        # Make a list of all processes to ensure they're fully parsed
        print(f" I think _build_all_referenced_processes is not needed")
        all_processes = set(self.process_definitions.keys())
        for process_name in all_processes:
            if process_name not in self.parsed_processes and process_name in self.process_places:
                # Calculate a position based on existing processes
                position_index = len(self.parsed_processes)
                self.build_petri_net(process_name, position_index)
    
    def build_petri_net(self, process_name, index):
        """Build the Petri net for a process definition"""
        print(f"parser Building Petri net for process {process_name}")
        
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
                print(f"Building referenced process {ref_process} at index {ref_index}")
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
        
        # Split the sequence by dot operator
        parts = self.split_by_operator(sequence, '.')
        
        # Keep track of current place for the sequence
        current_place_id = place_id
        x_offset = 20
        y_offset = 20
        
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
                        'x': self.get_place_x(current_place_id) + x_offset,
                        'y': self.get_place_y(current_place_id) + y_offset,
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

            if len(parts)== i +1: #last event 
                    transition_id = self.create_action_transition(part, current_place_id, process_name, y_pos, x_offset)                               
                    print(f"Created arc from {current_place_id} to {transition_id}")
                    #adds arc from current place to transition  
            if len(parts)> i +1:
                    transition_id = self.create_action_transition(part, current_place_id, process_name, y_pos, x_offset)
                    
                    new_place_id = self.get_id()
                    self.places.append({
                            'id': new_place_id,
                            'name': "",
                            'tokens': 0,
                            'x': self.get_place_x(new_place_id) +  x_offset,
                            'y': self.get_place_x(new_place_id) +  y_offset,
                            'is_terminal': False,
                            'process': process_name
                    })
                    self.arcs.append({
                            'source_id': transition_id, #previous transition to new place
                            'target_id': new_place_id,
                            'is_place_to_transition': False  
                    })
                    current_place_id = new_place_id                      
                
                    x_offset += 100
                    continue           
                
    def create_action_transition(self, action, place_id, process_name, y_pos, x_offset=0):
        """Create a transition for an action"""
        # Create transition
        transition_id = self.get_id()
        self.transitions.append({
            'id': transition_id,
            'name': action,
            'x': self.get_place_x(place_id) + x_offset,
            'y': self.get_place_y(place_id) + x_offset,
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
                if  self.x_toggal :
                    self.x_toggal = False
                    return place['x'] + 100
                else:
                    self.x_toggal = True
                    return place['x'] + 50
               
        return 100  # Default
    def get_place_y(self, place_id):
        """Get the x coordinate of a place"""
        for place in self.places:
            if place['id'] == place_id:
                if  self.y_toggal :
                    self.y_toggal = False
                    return place['y'] + 100
                else:
                    self.y_toggal = True
                    return place['y'] + 50
               
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
        
    def get_all_petri_nets(self):
        """Return a list of all stored Petri nets with their metadata"""
        return [{'id': net_id, 'name': data['name']} for net_id, data in self.petri_nets.items()]