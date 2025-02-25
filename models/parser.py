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
