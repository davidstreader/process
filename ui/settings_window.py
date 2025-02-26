# Update this in ui/settings_window.py

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QSlider, QDoubleSpinBox, QSpinBox, QPushButton)
from PyQt5.QtCore import Qt, pyqtSignal

class LayoutSettingsWindow(QMainWindow):
    """Window for adjusting force-directed layout parameters"""
    
    # Signal emitted when a parameter changes
    parameter_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Layout Settings")
        self.resize(400, 500)
        
        # Create main widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # Spring constant
        spring_layout = QHBoxLayout()
        spring_layout.addWidget(QLabel("Spring Constant:"))
        self.spring_slider = QSlider(Qt.Horizontal)
        self.spring_slider.setRange(10, 1000)
        self.spring_slider.setValue(10)  # Default value of 0.1
        spring_layout.addWidget(self.spring_slider)
        self.spring_spin = QDoubleSpinBox()
        self.spring_spin.setRange(0.01, 1.0)
        self.spring_spin.setSingleStep(0.01)
        self.spring_spin.setValue(0.1)
        spring_layout.addWidget(self.spring_spin)
        layout.addLayout(spring_layout)
        
        # Repulsion constant
        repulsion_layout = QHBoxLayout()
        repulsion_layout.addWidget(QLabel("Repulsion Force:"))
        self.repulsion_slider = QSlider(Qt.Horizontal)
        self.repulsion_slider.setRange(100, 1000)
        self.repulsion_slider.setValue(500)  # Default value of 500
        repulsion_layout.addWidget(self.repulsion_slider)
        self.repulsion_spin = QDoubleSpinBox()
        self.repulsion_spin.setRange(100, 1000)
        self.repulsion_spin.setSingleStep(10)
        self.repulsion_spin.setValue(500)
        repulsion_layout.addWidget(self.repulsion_spin)
        layout.addLayout(repulsion_layout)
        
        # Damping
        damping_layout = QHBoxLayout()
        damping_layout.addWidget(QLabel("Damping:"))
        self.damping_slider = QSlider(Qt.Horizontal)
        self.damping_slider.setRange(50, 100)
        self.damping_slider.setValue(85)  # Default value of 0.85
        damping_layout.addWidget(self.damping_slider)
        self.damping_spin = QDoubleSpinBox()
        self.damping_spin.setRange(0.5, 1.0)
        self.damping_spin.setSingleStep(0.01)
        self.damping_spin.setValue(0.85)
        damping_layout.addWidget(self.damping_spin)
        layout.addLayout(damping_layout)
        
        # Minimum distance - UPDATED RANGE
        min_dist_layout = QHBoxLayout()
        min_dist_layout.addWidget(QLabel("Minimum Distance:"))
        self.min_dist_slider = QSlider(Qt.Horizontal)
        self.min_dist_slider.setRange(50, 1000)  # Increased upper limit to 1000
        self.min_dist_slider.setValue(100)  # Default value of 100
        min_dist_layout.addWidget(self.min_dist_slider)
        self.min_dist_spin = QDoubleSpinBox()
        self.min_dist_spin.setRange(50, 1000)  # Increased upper limit to 1000
        self.min_dist_spin.setSingleStep(10)
        self.min_dist_spin.setValue(100)
        min_dist_layout.addWidget(self.min_dist_spin)
        layout.addLayout(min_dist_layout)
        
        # Temperature
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Temperature:"))
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setRange(10, 100)
        self.temp_slider.setValue(100)  # Default value of 1.0
        temp_layout.addWidget(self.temp_slider)
        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.1, 1.0)
        self.temp_spin.setSingleStep(0.1)
        self.temp_spin.setValue(1.0)
        temp_layout.addWidget(self.temp_spin)
        layout.addLayout(temp_layout)
        
        # Cooling factor
        cooling_layout = QHBoxLayout()
        cooling_layout.addWidget(QLabel("Cooling Factor:"))
        self.cooling_slider = QSlider(Qt.Horizontal)
        self.cooling_slider.setRange(80, 100)
        self.cooling_slider.setValue(95)  # Default value of 0.95
        cooling_layout.addWidget(self.cooling_slider)
        self.cooling_spin = QDoubleSpinBox()
        self.cooling_spin.setRange(0.8, 1.0)
        self.cooling_spin.setSingleStep(0.01)
        self.cooling_spin.setValue(0.95)
        cooling_layout.addWidget(self.cooling_spin)
        layout.addLayout(cooling_layout)
        
        # Timestep
        timestep_layout = QHBoxLayout()
        timestep_layout.addWidget(QLabel("Timestep:"))
        self.timestep_slider = QSlider(Qt.Horizontal)
        self.timestep_slider.setRange(1, 100)
        self.timestep_slider.setValue(50)  # Default value of 0.5
        timestep_layout.addWidget(self.timestep_slider)
        self.timestep_spin = QDoubleSpinBox()
        self.timestep_spin.setRange(0.01, 1.0)
        self.timestep_spin.setSingleStep(0.01)
        self.timestep_spin.setValue(0.5)
        timestep_layout.addWidget(self.timestep_spin)
        layout.addLayout(timestep_layout)
        
        # Max iterations
        iter_layout = QHBoxLayout()
        iter_layout.addWidget(QLabel("Max Iterations:"))
        self.iter_slider = QSlider(Qt.Horizontal)
        self.iter_slider.setRange(50, 500)
        self.iter_slider.setValue(100)  # Default value of 100
        iter_layout.addWidget(self.iter_slider)
        self.iter_spin = QSpinBox()
        self.iter_spin.setRange(50, 500)
        self.iter_spin.setSingleStep(10)
        self.iter_spin.setValue(100)
        iter_layout.addWidget(self.iter_spin)
        layout.addLayout(iter_layout)
        
        # Reset button
        reset_layout = QHBoxLayout()
        self.reset_button = QPushButton("Reset to Defaults")
        reset_layout.addWidget(self.reset_button)
        layout.addLayout(reset_layout)
        
        self.setCentralWidget(main_widget)
        
        # Connect signals
        self._connect_signals()
        self.reset_button.clicked.connect(self.reset_to_defaults)
    
    def _connect_signals(self):
        """Connect all slider and spinbox signals"""
        # Spring constant
        self.spring_slider.valueChanged.connect(
            lambda v: self._update_spring_constant(v / 100))
        self.spring_spin.valueChanged.connect(
            lambda v: self._update_spring_slider(v))
        
        # Repulsion constant
        self.repulsion_slider.valueChanged.connect(
            lambda v: self._update_repulsion_constant(v))
        self.repulsion_spin.valueChanged.connect(
            lambda v: self._update_repulsion_slider(v))
        
        # Damping
        self.damping_slider.valueChanged.connect(
            lambda v: self._update_damping(v / 100))
        self.damping_spin.valueChanged.connect(
            lambda v: self._update_damping_slider(v))
        
        # Minimum distance
        self.min_dist_slider.valueChanged.connect(
            lambda v: self._update_min_distance(v))
        self.min_dist_spin.valueChanged.connect(
            lambda v: self._update_min_distance_slider(v))
        
        # Temperature
        self.temp_slider.valueChanged.connect(
            lambda v: self._update_temperature(v / 100))
        self.temp_spin.valueChanged.connect(
            lambda v: self._update_temperature_slider(v))
        
        # Cooling factor
        self.cooling_slider.valueChanged.connect(
            lambda v: self._update_cooling_factor(v / 100))
        self.cooling_spin.valueChanged.connect(
            lambda v: self._update_cooling_slider(v))
        
        # Timestep
        self.timestep_slider.valueChanged.connect(
            lambda v: self._update_timestep(v / 100))
        self.timestep_spin.valueChanged.connect(
            lambda v: self._update_timestep_slider(v))
        
        # Max iterations
        self.iter_slider.valueChanged.connect(
            lambda v: self._update_max_iterations(v))
        self.iter_spin.valueChanged.connect(
            lambda v: self._update_max_iterations_slider(v))
    
    def _update_spring_constant(self, value):
        """Update spring constant from slider"""
        self.spring_spin.blockSignals(True)
        self.spring_spin.setValue(value)
        self.spring_spin.blockSignals(False)
        self.parameter_changed.emit({'spring_constant': value})
    
    def _update_spring_slider(self, value):
        """Update spring slider from spinbox"""
        self.spring_slider.blockSignals(True)
        self.spring_slider.setValue(int(value * 100))
        self.spring_slider.blockSignals(False)
        self.parameter_changed.emit({'spring_constant': value})
    
    def _update_repulsion_constant(self, value):
        """Update repulsion constant from slider"""
        self.repulsion_spin.blockSignals(True)
        self.repulsion_spin.setValue(value)
        self.repulsion_spin.blockSignals(False)
        self.parameter_changed.emit({'repulsion_constant': value})
    
    def _update_repulsion_slider(self, value):
        """Update repulsion slider from spinbox"""
        self.repulsion_slider.blockSignals(True)
        self.repulsion_slider.setValue(int(value))
        self.repulsion_slider.blockSignals(False)
        self.parameter_changed.emit({'repulsion_constant': value})
    
    def _update_damping(self, value):
        """Update damping from slider"""
        self.damping_spin.blockSignals(True)
        self.damping_spin.setValue(value)
        self.damping_spin.blockSignals(False)
        self.parameter_changed.emit({'damping': value})
    
    def _update_damping_slider(self, value):
        """Update damping slider from spinbox"""
        self.damping_slider.blockSignals(True)
        self.damping_slider.setValue(int(value * 100))
        self.damping_slider.blockSignals(False)
        self.parameter_changed.emit({'damping': value})
    
    def _update_min_distance(self, value):
        """Update minimum distance from slider"""
        self.min_dist_spin.blockSignals(True)
        self.min_dist_spin.setValue(value)
        self.min_dist_spin.blockSignals(False)
        self.parameter_changed.emit({'min_distance': value})
    
    def _update_min_distance_slider(self, value):
        """Update minimum distance slider from spinbox"""
        self.min_dist_slider.blockSignals(True)
        self.min_dist_slider.setValue(int(value))
        self.min_dist_slider.blockSignals(False)
        self.parameter_changed.emit({'min_distance': value})
    
    def _update_temperature(self, value):
        """Update temperature from slider"""
        self.temp_spin.blockSignals(True)
        self.temp_spin.setValue(value)
        self.temp_spin.blockSignals(False)
        self.parameter_changed.emit({'temperature': value})
    
    def _update_temperature_slider(self, value):
        """Update temperature slider from spinbox"""
        self.temp_slider.blockSignals(True)
        self.temp_slider.setValue(int(value * 100))
        self.temp_slider.blockSignals(False)
        self.parameter_changed.emit({'temperature': value})
    
    def _update_cooling_factor(self, value):
        """Update cooling factor from slider"""
        self.cooling_spin.blockSignals(True)
        self.cooling_spin.setValue(value)
        self.cooling_spin.blockSignals(False)
        self.parameter_changed.emit({'cooling_factor': value})
    
    def _update_cooling_slider(self, value):
        """Update cooling factor slider from spinbox"""
        self.cooling_slider.blockSignals(True)
        self.cooling_slider.setValue(int(value * 100))
        self.cooling_slider.blockSignals(False)
        self.parameter_changed.emit({'cooling_factor': value})
    
    def _update_timestep(self, value):
        """Update timestep from slider"""
        self.timestep_spin.blockSignals(True)
        self.timestep_spin.setValue(value)
        self.timestep_spin.blockSignals(False)
        self.parameter_changed.emit({'timestep': value})
    
    def _update_timestep_slider(self, value):
        """Update timestep slider from spinbox"""
        self.timestep_slider.blockSignals(True)
        self.timestep_slider.setValue(int(value * 100))
        self.timestep_slider.blockSignals(False)
        self.parameter_changed.emit({'timestep': value})
    
    def _update_max_iterations(self, value):
        """Update max iterations from slider"""
        self.iter_spin.blockSignals(True)
        self.iter_spin.setValue(value)
        self.iter_spin.blockSignals(False)
        self.parameter_changed.emit({'max_iterations': value})
    
    def _update_max_iterations_slider(self, value):
        """Update max iterations slider from spinbox"""
        self.iter_slider.blockSignals(True)
        self.iter_slider.setValue(value)
        self.iter_slider.blockSignals(False)
        self.parameter_changed.emit({'max_iterations': value})
    
    def reset_to_defaults(self):
        """Reset all parameters to default values"""
        self.spring_slider.setValue(10)
        self.repulsion_slider.setValue(500)
        self.damping_slider.setValue(85)
        self.min_dist_slider.setValue(100)
        self.temp_slider.setValue(100)
        self.cooling_slider.setValue(95)
        self.timestep_slider.setValue(50)
        self.iter_slider.setValue(100)