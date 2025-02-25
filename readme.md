# Process Algebra to Petri Net Visualization

A PyQt5-based application for visualizing Process Algebra expressions as Petri Nets with interactive force-directed layout.

## Features

- **Process Algebra Parser**: Convert simple process algebra expressions to Petri nets
- **Interactive Visualization**: Visualize Petri nets with places, transitions, and proper arcs
- **Force-Directed Layout**: Spring embedder algorithm for automatic graph layout
- **Real-time Layout Settings**: Adjust force-directed layout parameters with immediate visual feedback
- **Interactive Node Manipulation**: Drag and move individual nodes to customize the layout
- **Spring Embedding Toggle**: Turn force-directed layout on/off while manipulating nodes
- **Zoom Controls**: Zoom in/out and reset view functionality

## Requirements

- Python 3.6+
- PyQt5

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/process-algebra-viz.git
cd process-algebra-viz
```

2. Install required packages:
```bash
pip install PyQt5
```

## Usage

Run the application:
```bash
python main.py
```

### Process Algebra Editor

Enter process algebra expressions in the editor window using the following syntax:

- Sequential composition: `.` (e.g., `a.b`)
- Choice: `+` (e.g., `a + b`)
- Process definition: `=` (e.g., `P = a.b + c`)

Example:
```
P = a.b.P + c.d.STOP
Q = e.P + f.g.Q
MAIN = P | Q
```

### Visualizing Petri Nets

1. Enter process algebra expressions in the editor
2. Click "Visualize Petri Net" to generate and display the corresponding Petri net
3. Click "Load Example" to load an example process algebra expression

### Customizing the Layout

#### Spring Embedding Controls
- **Enable Spring Layout**: Toggle checkbox to enable/disable force-directed layout
- **Apply Full Layout**: Restart layout algorithm and apply it to all nodes
- **Layout Settings**: Open settings window to adjust force-directed layout parameters

#### Manual Node Positioning
- **Drag Nodes**: Click and drag places or transitions to move them around
- **Fixed vs. Dynamic Nodes**: 
  - When spring layout is enabled, dragged nodes will resume movement after release
  - When spring layout is disabled, dragged nodes will remain fixed in place

#### Layout Settings Window
Adjust the following parameters with real-time visual feedback:
- **Spring Constant**: Strength of edge attractive forces
- **Repulsion Force**: Strength of node repulsive forces
- **Damping**: Velocity decay factor
- **Minimum Distance**: Minimum separation distance between nodes
- **Temperature**: Controls maximum movement per iteration
- **Cooling Factor**: Rate at which temperature decreases
- **Timestep**: Size of simulation time steps
- **Max Iterations**: Maximum number of iterations for full layout

## Project Structure

```
process_algebra_viz/
│
├── main.py                  # Main application entry point
├── README.md                # Project documentation
│
├── models/
│   ├── __init__.py          # Package initialization
│   ├── parser.py            # Process algebra parser
│   └── layout.py            # Force-directed layout algorithm
│
└── ui/
    ├── __init__.py          # Package initialization
    ├── editor_window.py     # Text editor window
    ├── petri_net_window.py  # Petri