#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Robot Controller Module for AI Smart Car
This module handles the control of the robot's motors and movement.
"""

import time
import logging
import threading
import math
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

class Direction(Enum):
    """Enum for movement directions."""
    FORWARD = "forward"
    BACKWARD = "backward"
    LEFT = "left"
    RIGHT = "right"
    STOP = "stop"

class RobotController:
    """Controller for the robot's motors and movement."""
    
    def __init__(self):
        """Initialize the robot controller."""
        logger.info("Initializing robot controller...")
        
        # Motor control parameters
        self.max_speed = 1.0
        self.current_speed = 0.0
        self.current_direction = Direction.STOP
        
        # PID control parameters
        self.kp = 0.5  # Proportional gain
        self.ki = 0.1  # Integral gain
        self.kd = 0.2  # Derivative gain
        
        # Motor state
        self.running = False
        self.control_thread = None
        
        # Initialize motor drivers
        self._init_motors()
        
        logger.info("Robot controller initialized.")
    
    def _init_motors(self):
        """Initialize the motor drivers."""
        # In a real implementation, this would initialize the ODrive/VESC controllers
        # For simulation purposes, we'll just log the initialization
        logger.info("Initializing motor drivers...")
        
        # Simulated motor initialization
        self.motors = {
            "front_left": {"speed": 0, "direction": 1},
            "front_right": {"speed": 0, "direction": 1},
            "rear_left": {"speed": 0, "direction": 1},
            "rear_right": {"speed": 0, "direction": 1}
        }
        
        logger.info("Motor drivers initialized.")
    
    def start(self):
        """Start the robot controller."""
        if self.running:
            logger.warning("Robot controller is already running.")
            return
        
        logger.info("Starting robot controller...")
        self.running = True
        
        # Start the control thread
        self.control_thread = threading.Thread(target=self._control_loop)
        self.control_thread.daemon = True
        self.control_thread.start()
        
        logger.info("Robot controller started.")
    
    def stop(self):
        """Stop the robot controller."""
        if not self.running:
            logger.warning("Robot controller is not running.")
            return
        
        logger.info("Stopping robot controller...")
        self.running = False
        
        # Stop all motors
        self._stop_motors()
        
        # Wait for the control thread to finish
        if self.control_thread:
            self.control_thread.join(timeout=1.0)
        
        logger.info("Robot controller stopped.")
    
    def _control_loop(self):
        """Main control loop for the robot."""
        logger.info("Control loop started.")
        
        while self.running:
            # Apply PID control to maintain desired speed
            self._apply_pid_control()
            
            # Sleep to maintain control frequency
            time.sleep(0.01)  # 100 Hz control loop
        
        logger.info("Control loop stopped.")
    
    def _apply_pid_control(self):
        """Apply PID control to maintain desired speed."""
        # In a real implementation, this would read encoder feedback and apply PID control
        # For simulation purposes, we'll just simulate the PID control
        
        # Simulate PID control for each motor
        for motor_name, motor in self.motors.items():
            # In a real implementation, this would read encoder feedback
            # and calculate the error between desired and actual speed
            
            # For simulation, we'll just set the motor speed directly
            motor["speed"] = self.current_speed * motor["direction"]
    
    def _stop_motors(self):
        """Stop all motors."""
        logger.info("Stopping all motors...")
        
        # Set all motor speeds to 0
        for motor in self.motors.values():
            motor["speed"] = 0
        
        self.current_speed = 0.0
        self.current_direction = Direction.STOP
        
        logger.info("All motors stopped.")
    
    def move(self, direction, speed=0.5, duration=None):
        """Move the robot in the specified direction.
        
        Args:
            direction (str): The direction to move (forward, backward, left, right, stop).
            speed (float): The speed to move at (0.0 to 1.0).
            duration (float, optional): The duration to move for in seconds.
        
        Returns:
            dict: A dictionary containing the result of the movement command.
        """
        # Validate direction
        try:
            direction = Direction(direction)
        except ValueError:
            logger.error(f"Invalid direction: {direction}")
            return {"success": False, "error": f"Invalid direction: {direction}"}
        
        # Validate speed
        speed = max(0.0, min(1.0, speed))
        
        logger.info(f"Moving {direction.value} at speed {speed}")
        
        # Set the current direction and speed
        self.current_direction = direction
        self.current_speed = speed
        
        # Configure motor directions based on movement direction
        if direction == Direction.FORWARD:
            self._set_motor_directions(1, 1, 1, 1)
        elif direction == Direction.BACKWARD:
            self._set_motor_directions(-1, -1, -1, -1)
        elif direction == Direction.LEFT:
            self._set_motor_directions(-1, 1, -1, 1)
        elif direction == Direction.RIGHT:
            self._set_motor_directions(1, -1, 1, -1)
        elif direction == Direction.STOP:
            self._stop_motors()
        
        # If duration is specified, stop after the specified duration
        if duration is not None:
            def stop_after_duration():
                time.sleep(duration)
                self._stop_motors()
            
            # Start a timer to stop the motors after the specified duration
            timer_thread = threading.Thread(target=stop_after_duration)
            timer_thread.daemon = True
            timer_thread.start()
        
        return {
            "success": True,
            "direction": direction.value,
            "speed": speed,
            "duration": duration
        }
    
    def _set_motor_directions(self, front_left, front_right, rear_left, rear_right):
        """Set the direction of each motor.
        
        Args:
            front_left (int): Direction of the front left motor (1 or -1).
            front_right (int): Direction of the front right motor (1 or -1).
            rear_left (int): Direction of the rear left motor (1 or -1).
            rear_right (int): Direction of the rear right motor (1 or -1).
        """
        self.motors["front_left"]["direction"] = front_left
        self.motors["front_right"]["direction"] = front_right
        self.motors["rear_left"]["direction"] = rear_left
        self.motors["rear_right"]["direction"] = rear_right
    
    def joystick_control(self, x, y):
        """Control the robot using joystick input.
        
        Args:
            x (float): The x-axis value of the joystick (-1.0 to 1.0).
            y (float): The y-axis value of the joystick (-1.0 to 1.0).
        
        Returns:
            dict: A dictionary containing the result of the joystick command.
        """
        # Ensure x and y are within the valid range
        x = max(-1.0, min(1.0, x))
        y = max(-1.0, min(1.0, y))
        
        # Calculate the speed based on the distance from the center
        speed = math.sqrt(x*x + y*y)
        speed = min(1.0, speed)  # Ensure speed is not greater than 1.0
        
        # If the joystick is centered (within a small deadzone), stop the robot
        if speed < 0.1:
            return self.move(Direction.STOP.value)
        
        # Calculate the angle of the joystick
        angle = math.atan2(y, x)
        
        # Determine the direction based on the angle
        if -math.pi/4 <= angle <= math.pi/4:
            # Right
            direction = Direction.RIGHT.value
            # Reduce speed for turning
            speed *= 0.7
        elif math.pi/4 < angle <= 3*math.pi/4:
            # Forward
            direction = Direction.FORWARD.value
        elif -3*math.pi/4 <= angle < -math.pi/4:
            # Backward
            direction = Direction.BACKWARD.value
        else:
            # Left
            direction = Direction.LEFT.value
            # Reduce speed for turning
            speed *= 0.7
        
        # Move the robot in the calculated direction and speed
        return self.move(direction, speed)
    
    def get_status(self):
        """Get the current status of the robot.
        
        Returns:
            dict: A dictionary containing the current status of the robot.
        """
        return {
            "running": self.running,
            "direction": self.current_direction.value,
            "speed": self.current_speed,
            "motors": self.motors
        } 