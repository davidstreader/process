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
        """Save a Petri net to a JSON file"""
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Ensure path is within the nets directory
        file_path = self.nets_dir / filename
        
        # Convert parser data to serializable format
        data = {
            'places': parser.places,
            'transitions': parser.transitions,
            'arcs': parser.arcs
        }
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Update last net
        self.set_last_net(str(file_path))
        
        return str(file_path)
    
    def load_petri_net(self, file_path):
        """Load a Petri net from a JSON file"""
        path = Path(file_path)
        if not path.exists():
            return None
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            # Update last net
            self.set_last_net(str(path))
            
            return data
        except Exception as e:
            print(f"Error loading file: {str(e)}")
            return None
    
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
