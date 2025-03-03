import os
import json
import configparser
from pathlib import Path

class FileManager:
    """Manager for loading and saving Petri nets to/from files"""
    
    def __init__(self):
        # Create nets directory if it doesn't exist
        self.nets_dir = Path("nets")
        self.nets_dir.mkdir(exist_ok=True)
        
        # Create or load config file
        self.config_file = Path("config.ini")
        self.config = configparser.ConfigParser()
        
        if self.config_file.exists():
            self.config.read(self.config_file)
        
        # Ensure the general section exists
        if not self.config.has_section('General'):
            self.config.add_section('General')
            self.config.set('General', 'last_net', '')
            self._save_config()
    
    def _save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def get_last_net(self):
        """Get the path to the last opened Petri net"""
        last_net = self.config.get('General', 'last_net', fallback='')
        if last_net and Path(last_net).exists():
            return last_net
        return None
    
    def set_last_net(self, net_path):
        """Set the last opened Petri net"""
        self.config.set('General', 'last_net', str(net_path))
        self._save_config()
    
    def save_petri_net(self, parser, filename):
        """Save a Petri net and parse tree to a JSON file"""
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Ensure path is within the nets directory
        file_path = self.nets_dir / filename
        
        # Create expanded process definitions by replacing process references
        expanded_definitions = self._expand_process_definitions(parser.process_definitions)
        
        # Convert parser data to serializable format
        data = {
            'places': parser.places,
            'transitions': parser.transitions,
            'arcs': parser.arcs,
            'parse_tree': {
                'process_definitions': parser.process_definitions,
                'expanded_definitions': expanded_definitions,
                'process_places': parser.process_places,
                'current_id': parser.current_id
            },
            'source_code': self._generate_source_code(parser)
        }
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Update last net
        self.set_last_net(str(file_path))
        
        return str(file_path)
    
    def _expand_process_definitions(self, process_definitions):
        """Create expanded process definitions by replacing references"""
        expanded = process_definitions.copy()
        
        # Track which definitions have been processed to avoid infinite recursion
        processed = set()
        
        def expand_definition(name, depth=0):
            """Recursively expand a single definition"""
            if name in processed or depth > 10:  # Prevent infinite recursion
                return expanded[name]
                
            processed.add(name)
            definition = expanded[name]
            
            # Find all process references in this definition
            for other_name in process_definitions:
                if other_name != name:  # Avoid self-replacement
                    # Replace only whole-word matches (not parts of identifiers)
                    import re
                    pattern = r'\b' + re.escape(other_name) + r'\b'
                    
                    # Check if we have a match
                    if re.search(pattern, definition):
                        # Get the expanded definition for the reference
                        other_expanded = expand_definition(other_name, depth + 1)
                        
                        # Replace references with expanded definition
                        definition = re.sub(pattern, f"({other_expanded})", definition)
            
            # Update the expanded dictionary
            expanded[name] = definition
            return definition
        
        # Process each definition
        for name in process_definitions:
            expand_definition(name)
            
        return expanded
        
    def _generate_source_code(self, parser):
        """Generate process algebra source code from the parser"""
        source_code = []
        for process_name, definition in parser.process_definitions.items():
            source_code.append(f"{process_name} = {definition}")
        return "\n".join(source_code)
    

    
    def get_available_nets(self):
        """Get a list of available Petri net files"""
        nets = []
        for path in self.nets_dir.glob('*.json'):
            nets.append({
                'name': path.stem,
                'path': str(path),
                'size': path.stat().st_size,
                'modified': path.stat().st_mtime
            })
        
        # Sort by modification time (newest first)
        nets.sort(key=lambda x: x['modified'], reverse=True)
        
        return nets
    

    #######################
    def load_petri_net(self, file_path):
        """Load a Petri net from a JSON file with backward compatibility for arcs without process names"""
        path = Path(file_path)
        if not path.exists():
            return None
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            # Add backward compatibility for arc process names
            if 'arcs' in data:
                # Create a mapping of IDs to process names for backward compatibility
                process_map = {}
                
                # Add place processes to the map
                if 'places' in data:
                    for place in data['places']:
                        if 'id' in place and 'process' in place:
                            process_map[place['id']] = place['process']
                
                # Add transition processes to the map
                if 'transitions' in data:
                    for transition in data['transitions']:
                        if 'id' in transition and 'process' in transition:
                            process_map[transition['id']] = transition['process']
                
                # Update arcs with process information if missing
                for arc in data['arcs']:
                    if 'process' not in arc:
                        source_id = arc.get('source_id')
                        target_id = arc.get('target_id')
                        
                        # Try to get process name from source
                        if source_id in process_map:
                            arc['process'] = process_map[source_id]
                        # If not found in source, try target
                        elif target_id in process_map:
                            arc['process'] = process_map[target_id]
                        # If neither source nor target has process info, use the file name
                        else:
                            net_name = path.stem.replace("_", " ").title()
                            arc['process'] = net_name
            
            # Update last net
            self.set_last_net(str(path))
            
            return data
        except Exception as e:
            print(f"Error loading file: {str(e)}")
            return None
    #######################