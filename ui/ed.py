# Patch for ui/editor_window.py

# 1. Fix the broken show_petri_net_selector method
def show_petri_net_selector(self):
    """Show the Petri net selector when the visualize button is clicked"""
    # Get the current text from the editor
    text = self.text_edit.toPlainText()
    
    if text.strip():
        # First try to parse the text to get process definitions
        try:
            self.parser.parse(text)
            # Successful parse - update the selector's parser reference
            self.petri_net_window.selector_window.parser = self.parser
            # Load the parser definitions into the selector
            self.petri_net_window.selector_window.load_parser_definitions()
        except Exception as e:
            print(f"Parser error (non-critical): {str(e)}")
        
        # Add the current editor content as a custom net
        self.petri_net_window.selector_window.add_custom_net(
            name="Current Editor Content",
            description=text if len(text) < 100 else text[:97] + "...",
            expression=text
        )

    # Show the selector
    self.petri_net_window.selector_window.show_selector()

# 2. Properly implement the visualize_petri_net method
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

# Patch for ui/petri_net_selector.py

# 3. Enhance the load_parser_definitions method
def load_parser_definitions(self):
    """Load Petri net definitions from the parser"""
    # Clear previous parser nets
    self.parser_nets = []
    
    # Get process definitions from parser
    process_definitions = self.parser.process_definitions
    if not process_definitions:
        return
    
    # Convert process definitions to net format
    for name, expr in process_definitions.items():
        # Create a complete expression that can be parsed
        full_expr = f"{name} = {expr}"
        
        # Skip duplicates
        duplicate = False
        for net in self.parser_nets:
            if net['expression'] == full_expr:
                duplicate = True
                break
                
        if not duplicate:
            net = {
                'name': f"Process: {name}",
                'description': full_expr,
                'expression': full_expr
            }
            self.parser_nets.append(net)
    
    # Add a special entry for the combined processes if there are multiple
    if len(process_definitions) > 1:
        # Create a combined expression with all processes
        combined_expr = "\n".join([f"{name} = {expr}" for name, expr in process_definitions.items()])
        
        # Add a "Main System" entry that includes all processes
        all_processes = {
            'name': "Main System (All Processes)",
            'description': "Combined system with all defined processes",
            'expression': combined_expr
        }
        self.parser_nets.append(all_processes)
    
    # Refresh the list
    self.populate_list()

# 4. Improve the populate_list method
def populate_list(self):
    """Populate the list with available Petri nets"""
    self.list_widget.clear()
    
    # Add predefined examples
    if self.available_nets:
        self.list_widget.addItem("--- Predefined Examples ---")
        item = self.list_widget.item(0)
        item.setFlags(item.flags() & ~Qt.ItemIsSelectable)  # Make header non-selectable
        
        for net in self.available_nets:
            item = QListWidgetItem(net['name'])
            item.setData(Qt.UserRole, net)  # Store the full net data
            item.setToolTip(net['description'])
            self.list_widget.addItem(item)
    
    # Add parser definitions if any
    if self.parser_nets:
        self.list_widget.addItem("")  # Spacer
        item = self.list_widget.item(self.list_widget.count() - 1)
        item.setFlags(item.flags() & ~Qt.ItemIsSelectable)  # Make spacer non-selectable
        
        self.list_widget.addItem("--- Parser Definitions ---")
        item = self.list_widget.item(self.list_widget.count() - 1)
        item.setFlags(item.flags() & ~Qt.ItemIsSelectable)  # Make header non-selectable
        
        for net in self.parser_nets:
            item = QListWidgetItem(net['name'])
            item.setData(Qt.UserRole, net)  # Store the full net data
            item.setToolTip(net['description'])
            self.list_widget.addItem(item)
            
    # Select the first selectable item automatically if available
    for i in range(self.list_widget.count()):
        item = self.list_widget.item(i)
        if item and item.flags() & Qt.ItemIsSelectable:
            self.list_widget.setCurrentItem(item)
            break

# Patch for models/parser.py

# 5. Add export_to_process_algebra method
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

# 6. Helper method for export_to_process_algebra
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