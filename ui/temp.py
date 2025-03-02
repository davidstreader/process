# Add this to the visualize_petri_net method in ui/main_window.py


# Call this method at the end of update_petri_net
def update_petri_net(self, parser, file_path=None):
    # ... existing code ...
    
    # Update UI state
    self.update_ui_state()