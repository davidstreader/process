# Process Algebra to Petri Net - Load/Save Feature Implementation Guide

This guide describes the implementation of the load/save feature for the Process Algebra to Petri Net visualization application.

## New Features

1. **Load and Save Petri Nets**: Users can now save their Petri nets to JSON files and load them later.
2. **Configuration File**: The application now remembers the last used Petri net and automatically loads it on startup.
3. **Dedicated Nets Directory**: Petri nets are saved in a dedicated `nets` directory for better organization.
4. **Process Algebra Export**: The application can now export Petri nets back to process algebra code.

## Implementation Components

### 1. FileManager (models/file_manager.py)

A new class that handles all file and configuration operations.

Key features:
- Creates and manages the `nets` directory
- Handles saving Petri nets to JSON files
- Loads Petri nets from JSON files
- Manages the `config.ini` file that tracks the last opened net
- Provides methods to list available Petri nets

### 2. Enhanced ProcessAlgebraParser (models/parser.py)

The original parser has been enhanced with:
- Support for loading Petri nets directly from JSON data
- Advanced tracking of process definitions
- Ability to export Petri nets back to process algebra code
- Improved annotation of elements for better connectivity tracking

### 3. Updated UI Components

#### TextEditorWindow (ui/editor_window.py)
- Added "Load" and "Save" buttons
- Added file menu with appropriate actions
- New dialogs for saving and loading Petri nets
- Integration with FileManager for file operations
- Automatic loading of the last used Petri net

#### PetriNetWindow (ui/petri_net_window.py)
- Added file menu with save/load options
- "Save Layout" and "Save As" buttons
- Tracking of the current file path
- Updated update_petri_net method to accept a file path

## Configuration System

The application uses a simple INI-based configuration file (`config.ini`) to track the last opened Petri net. The configuration is managed by the FileManager class and is automatically loaded on application startup.

## File Format

Petri nets are saved as JSON files with the following structure:

```json
{
  "places": [
    {
      "id": 0,
      "name": "P",
      "tokens": 1,
      "x": 50,
      "y": 50,
      "is_process": true
    },
    ...
  ],
  "transitions": [
    {
      "id": 1,
      "name": "a",
      "x": 150,
      "y": 50,
      "process": "P"
    },
    ...
  ],
  "arcs": [
    {
      "source_id": 0,
      "target_id": 1,
      "is_place_to_transition": true
    },
    ...
  ]
}
```

## Usage Guide

### Saving a Petri Net

1. Create a process algebra expression in the editor
2. Click "Visualize Petri Net" to generate the Petri net
3. In the Petri Net window, click "Save Layout" or "Save As" to save the current net
4. Enter a name for the Petri net when prompted
5. The net will be saved to the `nets` directory as a JSON file

### Loading a Petri Net

1. In the Process Algebra Editor, click "Load"
2. Select a Petri net from the list of available nets
3. The Petri net will be loaded and visualized, and the corresponding process algebra code will be generated in the editor

### Last Used Net

The application automatically remembers the last used Petri net and loads it on startup.

## Implementation Notes

1. **Directory Creation**: The `nets` directory is created if it doesn't exist.
2. **Error Handling**: All file operations include proper error handling.
3. **User Feedback**: Users receive feedback through message boxes for all operations.
4. **Menu Integration**: File operations are accessible through buttons and menu items.
5. **Keyboard Shortcuts**: Common operations have keyboard shortcuts (Ctrl+S, Ctrl+O, etc.).

## Future Improvements

1. **Preview in Load Dialog**: Add preview thumbnails in the load dialog.
2. **Multiple File Formats**: Support for different file formats beyond JSON.
3. **User Tags and Metadata**: Allow users to add tags and metadata to saved Petri nets.
4. **Cloud Synchronization**: Enable saving and loading from cloud storage.
