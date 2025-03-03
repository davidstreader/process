
from parser import ProcessAlgebraParser

def petri_to_state_machine(parser, net_id=None):
    """
    Convert a Petri net to a state machine where:
    - States represent sets of marked places
    - Transitions represent the firing of Petri net transitions
    
    Args:
        parser: The ProcessAlgebraParser instance containing the Petri net
        net_id: Optional ID of a specific Petri net stored in parser.petri_nets
               If None, uses the current active Petri net in the parser
        
    Returns:
        dict: A state machine dictionary with the following structure:
            {
                'id': str,              # Unique identifier for the state machine
                'name': str,            # Name of the state machine
                'states': [             # List of states
                    {
                        'id': int,      # State ID
                        'name': str,    # State name
                        'places': list, # List of place IDs that have tokens in this state
                        'is_initial': bool # Whether this is the initial state
                    },
                    ...
                ],
                'edges': [              # List of transitions between states
                    {
                        'source': int,  # Source state ID
                        'target': int,  # Target state ID
                        'name': str     # Transition name
                    },
                    ...
                ]
            }
    """
    # If net_id is provided, load that specific Petri net
    original_places = None
    original_transitions = None
    original_arcs = None
    original_net_id = None
    
    if net_id is not None and hasattr(parser, 'petri_nets') and net_id in parser.petri_nets:
        # Store the current parser state
        original_places = parser.places
        original_transitions = parser.transitions
        original_arcs = parser.arcs
        original_net_id = parser.current_net if hasattr(parser, 'current_net') else None
        
        # Load the specified Petri net
        net_data = parser.petri_nets[net_id]
        parser.places = net_data['places']
        parser.transitions = net_data['transitions']
        parser.arcs = net_data['arcs']
        
    # Get the net name for our state machine
    sm_name = "State Machine"
    if net_id is not None and hasattr(parser, 'petri_nets') and net_id in parser.petri_nets:
        sm_name = f"State Machine for {parser.petri_nets[net_id].get('name', net_id)}"
    elif hasattr(parser, 'current_net') and parser.current_net is not None:
        sm_name = f"State Machine for {parser.current_net}"
    # Find all places and transitions
    places = parser.places
    transitions = parser.transitions
    arcs = parser.arcs
    
    # Create a mapping from place ID to place object for easy lookup
    place_map = {place['id']: place for place in places}
    transition_map = {trans['id']: trans for trans in transitions}
    
    # Find initially marked places (places with tokens)
    initial_marking = frozenset(place['id'] for place in places if place.get('tokens', 0) > 0)
    
    # Create the initial state
    states = {0: initial_marking}
    state_to_id = {initial_marking: 0}
    initial_state = 0
    next_state_id = 1
    
    # Create transition function
    edges = []
    
    # Keep track of unexplored states
    unexplored_states = [initial_marking]
    
    while unexplored_states:
        current_marking = unexplored_states.pop(0)
        current_state_id = state_to_id[current_marking]
        
        # Find all enabled transitions from this marking
        for transition in transitions:
            transition_id = transition['id']
            transition_name = transition['name']
            
            # Check if this transition is enabled (all input places have tokens)
            input_places = set()
            for arc in arcs:
                if arc['target_id'] == transition_id and arc['is_place_to_transition']:
                    input_places.add(arc['source_id'])
            
            # Transition is enabled if all input places are in the current marking
            if all(place_id in current_marking for place_id in input_places):
                # Transition is enabled - compute new marking
                new_marking = set(current_marking)
                
                # Remove tokens from input places
                for input_place in input_places:
                    new_marking.remove(input_place)
                
                # Add tokens to output places
                output_places = set()
                for arc in arcs:
                    if arc['source_id'] == transition_id and not arc['is_place_to_transition']:
                        output_places.add(arc['target_id'])
                
                new_marking.update(output_places)
                
                # Convert to frozenset for hashability
                new_marking_frozen = frozenset(new_marking)
                
                # Create a new state if we haven't seen this marking before
                if new_marking_frozen not in state_to_id:
                    state_to_id[new_marking_frozen] = next_state_id
                    states[next_state_id] = new_marking_frozen
                    unexplored_states.append(new_marking_frozen)
                    next_state_id += 1
                
                # Add the transition
                target_state_id = state_to_id[new_marking_frozen]
                edges.append({
                    'source': current_state_id,
                    'target': target_state_id,
                    'name': transition_name
                })
    
    # Generate the structured state machine dictionary
    state_machine = {
        'id': net_id or 'current',
        'name': sm_name,
        'states': [],
        'edges': edges
    }
    
    # Convert states to the desired format
    for state_id, marking in states.items():
        # Get place names for this state
        place_names = []
        for place_id in marking:
            if place_id in place_map:
                place_name = place_map[place_id].get('name', f'p{place_id}')
                place_names.append(place_name)
        
        state_machine['states'].append({
            'id': state_id,
            'name': f"State {state_id}",
            'places': list(marking),  # Convert frozenset to list
            'place_names': sorted(place_names),  # Sorted place names for readability
            'is_initial': state_id == initial_state
        })
    
    # Restore original parser state if we loaded a specific net
    if original_places is not None:
        parser.places = original_places
        parser.transitions = original_transitions
        parser.arcs = original_arcs
        if original_net_id is not None and hasattr(parser, 'current_net'):
            parser.current_net = original_net_id
    
    return state_machine

def print_state_machine(state_machine):
    """
    Print a state machine in a readable format
    
    Args:
        state_machine: State machine dictionary
    """
    print(f"State Machine: {state_machine['name']}")
    print("=============")
    
    print("\nStates:")
    print("------")
    for state in state_machine['states']:
        initial_marker = " (initial)" if state['is_initial'] else ""
        place_names = ', '.join(state['place_names'])
        print(f"State {state['id']}{initial_marker}: {place_names}")
    
    print("\nTransitions:")
    print("-----------")
    for edge in state_machine['edges']:
        print(f"State {edge['source']} --({edge['name']})--> State {edge['target']}")

def get_available_petri_nets(parser):
    """
    Get a list of all available Petri nets stored in the parser
    
    Args:
        parser: The ProcessAlgebraParser instance
        
    Returns:
        list: List of available Petri net details (id, name)
    """
    if hasattr(parser, 'get_all_petri_nets'):
        return parser.get_all_petri_nets()
    elif hasattr(parser, 'petri_nets'):
        return [{'id': net_id, 'name': data.get('name', net_id)} 
                for net_id, data in parser.petri_nets.items()]
    else:
        return []

def visualize_state_machine(state_machine, output_filename='state_machine.dot'):
    """
    Generate a Graphviz DOT file to visualize the state machine
    
    Args:
        state_machine: State machine dictionary
        output_filename: Filename to save the DOT file
    """
    with open(output_filename, 'w') as f:
        f.write('digraph state_machine {\n')
        f.write('    rankdir=LR;\n')
        f.write('    node [shape = circle];\n')
        
        # Write states
        for state in state_machine['states']:
            place_names = ', '.join(state['place_names'])
            label = f"S{state['id']}\\n{place_names}"
            if state['is_initial']:
                f.write(f'    {state["id"]} [label="{label}", style=filled, fillcolor=lightblue];\n')
            else:
                f.write(f'    {state["id"]} [label="{label}"];\n')
        
        # Write transitions
        for edge in state_machine['edges']:
            f.write(f'    {edge["source"]} -> {edge["target"]} [label="{edge["name"]}"];\n')
        
        f.write('}\n')
    
    print(f"State machine visualization saved to {output_filename}")
    print("You can render it using Graphviz with the command:")
    print(f"  dot -Tpng {output_filename} -o state_machine.png")

# Example of how to use these functions with a parser:
# # Using current active Petri net
# state_machine = petri_to_state_machine(parser)
# print_state_machine(state_machine)
# 
# # Using a specific stored Petri net by ID
# # First, get the list of available nets
# available_nets = get_available_petri_nets(parser)
# for net in available_nets:
#     print(f"Net ID: {net['id']}, Name: {net['name']}")
#
# # Then use a specific net by ID
# net_id = "newboy"  # Replace with actual ID
# state_machine = petri_to_state_machine(parser, net_id)
# print_state_machine(state_machine)
# visualize_state_machine(state_machine, f"{net_id}_state_machine.dot")