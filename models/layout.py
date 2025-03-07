# Updated ForceDirectedLayout class for models/layout.py

import math
import random

class ForceDirectedLayout:
    """Force-directed (spring embedder) layout algorithm for Petri nets"""
    
    def __init__(self):
        # Default layout parameters
        self.spring_constant = 0.1
        self.repulsion_constant = 500.0
        self.damping = 0.85
        self.min_distance = 100.0
        self.max_iterations = 100
        self.temperature = 1.0
        self.cooling_factor = 0.95
        self.timestep = 0.5
        self.current_net_id = None
        
        # Node velocities
        self.velocities = {}
    
    def set_parameters(self, params):
        """Update layout parameters from settings window"""
        # Only update parameters that are provided
        if 'spring_constant' in params:
            self.spring_constant = params['spring_constant']
           # print(f"Updated spring_constant to {self.spring_constant}")
            
        if 'repulsion_constant' in params:
            self.repulsion_constant = params['repulsion_constant']
           # print(f"Updated repulsion_constant to {self.repulsion_constant}")
            
        if 'damping' in params:
            self.damping = params['damping']
           # print(f"Updated damping to {self.damping}")
            
        if 'min_distance' in params:
            self.min_distance = params['min_distance']
           # print(f"Updated min_distance to {self.min_distance}")
            
        if 'max_iterations' in params:
            self.max_iterations = params['max_iterations']
            #print(f"Updated max_iterations to {self.max_iterations}")
            
        if 'temperature' in params:
            self.temperature = params['temperature']
            #print(f"Updated temperature to {self.temperature}")
            
        if 'cooling_factor' in params:
            self.cooling_factor = params['cooling_factor']
            #print(f"Updated cooling_factor to {self.cooling_factor}")
            
        if 'timestep' in params:
            self.timestep = params['timestep']
            #print(f"Updated timestep to {self.timestep}")
    
    def initialize_layout(self, parser, net_id=None):
        """Initialize layout for a specific Petri net"""
        # Reset velocities
        self.velocities = {}
        
        # If no specific net_id is provided, use the first main process
        if net_id is None and hasattr(parser, 'main_processes') and parser.main_processes:
            net_id = next(iter(parser.main_processes))
        
        # Store the current net ID for future operations
        self.current_net_id = net_id
        
        # Get the Petri net data
        net_data = self._get_net_data(parser, net_id)
        if not net_data:
            print(f"Warning: No Petri net data found for ID {net_id}")
            return
        
        #print(f"Initializing layout for Petri net: {net_id}")
        
        # Initialize positions and velocities for places
        for place in net_data['places']:
            if 'x' not in place or 'y' not in place:
                place['x'] = random.uniform(100, 700)
                place['y'] = random.uniform(100, 500)
            
            # Initialize velocity for this node
            self.velocities[f"p{place['id']}"] = {'x': 0, 'y': 0}
        
        # Initialize positions and velocities for transitions
        for transition in net_data['transitions']:
            if 'x' not in transition or 'y' not in transition:
                transition['x'] = random.uniform(100, 700)
                transition['y'] = random.uniform(100, 500)
            
            # Initialize velocity for this node
            self.velocities[f"t{transition['id']}"] = {'x': 0, 'y': 0}
    
    def apply_layout(self, parser, net_id=None, iterations=None):
        """Apply the force-directed layout algorithm to a specific Petri net"""
        # Use provided iterations or default
        if iterations is None:
            iterations = self.max_iterations
        
        # Initialize the layout
        if net_id is None:
            net_id = self.current_net_id
        self.initialize_layout(parser, net_id)
        
        # Get the Petri net data
        net_data = self._get_net_data(parser, net_id)
        if not net_data:
            return
        
        # Iteratively apply forces and update positions
        temp = self.temperature
        for _ in range(iterations):
            # Calculate forces for each node
            forces = self._calculate_forces(net_data)
            
            # Update positions based on forces
            self._update_positions(net_data, forces, temp)
            
            # Cool the temperature
            temp *= self.cooling_factor
            
            if temp < 0.01:
                break
    
    def update_single_iteration(self, parser, net_id=None):
        """Apply a single iteration of the layout algorithm to a specific Petri net"""
        # If no net_id is provided, use the current one
        if net_id is None:
            net_id = self.current_net_id
        
        # Get the Petri net data
        net_data = self._get_net_data(parser, net_id)
        if not net_data:
            return
        
        # Calculate forces and update positions
        forces = self._calculate_forces(net_data)
        self._update_positions(net_data, forces, self.temperature)
    
    def _get_net_data(self, parser, net_id):
        """Get the data for a specific Petri net"""
        # First, try to get from petri_nets dictionary
        if hasattr(parser, 'petri_nets') and net_id in parser.petri_nets:
            return parser.petri_nets[net_id]
        
        # If not found or no net_id specified, use the current parser data
        # This is for backward compatibility
        return {
            'places': parser.places,
            'transitions': parser.transitions,
            'arcs': parser.arcs
        }
    
    def _calculate_forces(self, net_data):
        """Calculate forces for each node based on simplified model"""
        forces = {}
        
        # Initialize forces for all nodes
        for place in net_data['places']:
            forces[f"p{place['id']}"] = {'x': 0, 'y': 0}
        
        for transition in net_data['transitions']:
            forces[f"t{transition['id']}"] = {'x': 0, 'y': 0}
        
        # Calculate repulsive forces between all nodes
        all_nodes = [(f"p{p['id']}", p) for p in net_data['places']] + [(f"t{t['id']}", t) for t in net_data['transitions']]
        
        for i, (id1, node1) in enumerate(all_nodes):
            for j, (id2, node2) in enumerate(all_nodes[i+1:], i+1):
                dx = node1['x'] - node2['x']
                dy = node1['y'] - node2['y']
                
                # Avoid division by zero
                if dx == 0:
                    dx = 0.1
                if dy == 0:
                    dy = 0.1
                
                distance = max(0.1, math.sqrt(dx*dx + dy*dy))
                
                # Repulsive force inversely proportional to distance squared
                force = self.repulsion_constant / (distance * distance)
                
                # Normalize direction
                if distance > 0:
                    dx /= distance
                    dy /= distance
                
                # Apply the force to both nodes in opposite directions
                if not node1.get('fixed', False):
                    forces[id1]['x'] += dx * force
                    forces[id1]['y'] += dy * force
                
                if not node2.get('fixed', False):
                    forces[id2]['x'] -= dx * force
                    forces[id2]['y'] -= dy * force
        
        # Calculate attractive forces along the arcs
        for arc in net_data['arcs']:
            source_id = arc['source_id']
            target_id = arc['target_id']
            
            source = None
            target = None
            source_type = ""
            target_type = ""
            
            # Find source and target nodes
            if arc['is_place_to_transition']:
                # From place to transition
                for place in net_data['places']:
                    if place['id'] == source_id:
                        source = place
                        source_type = "p"
                        break
                
                for transition in net_data['transitions']:
                    if transition['id'] == target_id:
                        target = transition
                        target_type = "t"
                        break
            else:
                # From transition to place
                for transition in net_data['transitions']:
                    if transition['id'] == source_id:
                        source = transition
                        source_type = "t"
                        break
                
                for place in net_data['places']:
                    if place['id'] == target_id:
                        target = place
                        target_type = "p"
                        break
            
            if source and target:
                dx = source['x'] - target['x']
                dy = source['y'] - target['y']
                
                # Avoid division by zero
                distance = max(0.1, math.sqrt(dx*dx + dy*dy))
                
                # Attractive force proportional to distance
                force = self.spring_constant * distance / 10
                
                # Normalize direction
                if distance > 0:
                    dx /= distance
                    dy /= distance
                
                # Apply the force to both nodes in opposite directions
                if not source.get('fixed', False):
                    forces[f"{source_type}{source['id']}"]["x"] -= dx * force
                    forces[f"{source_type}{source['id']}"]["y"] -= dy * force
                
                if not target.get('fixed', False):
                    forces[f"{target_type}{target['id']}"]["x"] += dx * force
                    forces[f"{target_type}{target['id']}"]["y"] += dy * force
        
        return forces
    
    def _update_positions(self, net_data, forces, temperature):
        """Update node positions based on calculated forces"""
        # Update places
        for place in net_data['places']:
            if not place.get('fixed', False):
                node_id = f"p{place['id']}"
                
                # Skip if velocity not initialized
                if node_id not in self.velocities:
                    continue
                
                # Apply forces to velocity (with damping from settings)
                self.velocities[node_id]['x'] = self.velocities[node_id]['x'] * self.damping + forces[node_id]['x'] * self.timestep
                self.velocities[node_id]['y'] = self.velocities[node_id]['y'] * self.damping + forces[node_id]['y'] * self.timestep
                
                # Limit movement by temperature
                displacement = math.sqrt(self.velocities[node_id]['x']**2 + self.velocities[node_id]['y']**2)
                if displacement > 0:
                    scale = min(displacement, temperature * 30) / displacement
                    
                    # Update position
                    place['x'] += self.velocities[node_id]['x'] * scale
                    place['y'] += self.velocities[node_id]['y'] * scale
                    
                    # Keep nodes within reasonable bounds
                    place['x'] = max(50, min(place['x'], 750))
                    place['y'] = max(50, min(place['y'], 550))
        
        # Update transitions
        for transition in net_data['transitions']:
            if not transition.get('fixed', False):
                node_id = f"t{transition['id']}"
                
                # Skip if velocity not initialized
                if node_id not in self.velocities:
                    continue
                
                # Apply forces to velocity (with damping from settings)
                self.velocities[node_id]['x'] = self.velocities[node_id]['x'] * self.damping + forces[node_id]['x'] * self.timestep
                self.velocities[node_id]['y'] = self.velocities[node_id]['y'] * self.damping + forces[node_id]['y'] * self.timestep
                
                # Limit movement by temperature
                displacement = math.sqrt(self.velocities[node_id]['x']**2 + self.velocities[node_id]['y']**2)
                if displacement > 0:
                    scale = min(displacement, temperature * 30) / displacement
                    
                    # Update position
                    transition['x'] += self.velocities[node_id]['x'] * scale
                    transition['y'] += self.velocities[node_id]['y'] * scale
                    
                    # Keep nodes within reasonable bounds
                    transition['x'] = max(50, min(transition['x'], 750))
                    transition['y'] = max(50, min(transition['y'], 550))