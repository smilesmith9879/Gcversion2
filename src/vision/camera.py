#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Camera Manager Module for AI Smart Car
This module handles the camera control and video streaming.
"""

import os
import time
import logging
import threading
import json
import cv2
import numpy as np
import asyncio
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder

# Configure logging
logger = logging.getLogger(__name__)

class VideoStreamTrack(MediaStreamTrack):
    """Video stream track for WebRTC streaming."""
    
    kind = "video"
    
    def __init__(self, camera):
        """Initialize the video stream track.
        
        Args:
            camera: The camera manager instance.
        """
        super().__init__()
        self.camera = camera
        self.frame_count = 0
    
    async def recv(self):
        """Receive a frame from the camera.
        
        Returns:
            VideoFrame: The video frame.
        """
        from av import VideoFrame
        
        # Get the current frame from the camera
        frame = self.camera.get_current_frame()
        
        # Convert the frame to a VideoFrame
        video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        video_frame.pts = self.frame_count
        video_frame.time_base = 1 / 30  # 30 FPS
        
        self.frame_count += 1
        
        return video_frame

class CameraManager:
    """Manager for the camera and video streaming."""
    
    def __init__(self):
        """Initialize the camera manager."""
        logger.info("Initializing camera manager...")
        
        # Camera parameters
        self.camera_index = int(os.getenv('CAMERA_INDEX', 0))
        self.frame_width = int(os.getenv('FRAME_WIDTH', 640))
        self.frame_height = int(os.getenv('FRAME_HEIGHT', 480))
        self.fps = int(os.getenv('FPS', 30))
        
        # Camera state
        self.running = False
        self.camera = None
        self.current_frame = None
        self.camera_thread = None
        
        # Servo gimbal parameters
        self.horizontal_angle = 80  # Initial horizontal angle (degrees)
        self.vertical_angle = 40    # Initial vertical angle (degrees)
        self.horizontal_min = 35    # Minimum horizontal angle (degrees)
        self.horizontal_max = 125   # Maximum horizontal angle (degrees)
        self.vertical_min = -5      # Minimum vertical angle (degrees)
        self.vertical_max = 85      # Maximum vertical angle (degrees)
        
        # WebRTC parameters
        self.peer_connections = set()
        
        # Initialize the camera
        self._init_camera()
        
        # Initialize the servo gimbal
        self._init_servo_gimbal()
        
        logger.info("Camera manager initialized.")
    
    def _init_camera(self):
        """Initialize the camera."""
        logger.info(f"Initializing camera (index: {self.camera_index})...")
        
        try:
            # Open the camera
            self.camera = cv2.VideoCapture(self.camera_index)
            
            # Set camera parameters
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.camera.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Read a test frame
            ret, frame = self.camera.read()
            if not ret:
                logger.error("Failed to read from camera.")
                self.camera = None
                return
            
            # Initialize the current frame
            self.current_frame = frame
            
            logger.info("Camera initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing camera: {e}")
            self.camera = None
    
    def _init_servo_gimbal(self):
        """Initialize the servo gimbal."""
        logger.info("Initializing servo gimbal...")
        
        # In a real implementation, this would initialize the PCA9685 controller
        # For simulation purposes, we'll just log the initialization
        
        logger.info("Servo gimbal initialized.")
    
    def start(self):
        """Start the camera manager."""
        if self.running:
            logger.warning("Camera manager is already running.")
            return
        
        if self.camera is None:
            logger.error("Camera is not initialized.")
            return
        
        logger.info("Starting camera manager...")
        self.running = True
        
        # Start the camera thread
        self.camera_thread = threading.Thread(target=self._camera_loop)
        self.camera_thread.daemon = True
        self.camera_thread.start()
        
        logger.info("Camera manager started.")
    
    def stop(self):
        """Stop the camera manager."""
        if not self.running:
            logger.warning("Camera manager is not running.")
            return
        
        logger.info("Stopping camera manager...")
        self.running = False
        
        # Wait for the camera thread to finish
        if self.camera_thread:
            self.camera_thread.join(timeout=1.0)
        
        # Close the camera
        if self.camera:
            self.camera.release()
            self.camera = None
        
        # Close all peer connections
        for pc in self.peer_connections:
            pc.close()
        self.peer_connections.clear()
        
        logger.info("Camera manager stopped.")
    
    def _camera_loop(self):
        """Main camera loop."""
        logger.info("Camera loop started.")
        
        while self.running:
            if self.camera:
                # Read a frame from the camera
                ret, frame = self.camera.read()
                if ret:
                    # Update the current frame
                    self.current_frame = frame
                else:
                    logger.warning("Failed to read from camera.")
            
            # Sleep to maintain frame rate
            time.sleep(1.0 / self.fps)
        
        logger.info("Camera loop stopped.")
    
    def get_current_frame(self):
        """Get the current frame from the camera.
        
        Returns:
            numpy.ndarray: The current frame.
        """
        if self.current_frame is None:
            # Return a black frame if no frame is available
            return np.zeros((self.frame_height, self.frame_width, 3), dtype=np.uint8)
        
        return self.current_frame
    
    async def process_offer(self, offer):
        """Process a WebRTC offer.
        
        Args:
            offer (dict): The WebRTC offer.
        
        Returns:
            dict: The WebRTC answer.
        """
        logger.info("Processing WebRTC offer...")
        
        # Create a new peer connection
        pc = RTCPeerConnection()
        self.peer_connections.add(pc)
        
        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            logger.info(f"Connection state changed to {pc.connectionState}")
            if pc.connectionState == "failed" or pc.connectionState == "closed":
                self.peer_connections.discard(pc)
        
        # Add the video track
        pc.addTrack(VideoStreamTrack(self))
        
        # Set the remote description
        await pc.setRemoteDescription(
            RTCSessionDescription(sdp=offer["sdp"], type=offer["type"])
        )
        
        # Create an answer
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        
        logger.info("WebRTC offer processed.")
        
        # Return the answer
        return {
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        }
    
    def control(self, action, value):
        """Control the camera.
        
        Args:
            action (str): The action to perform (e.g., "horizontal", "vertical").
            value (float): The value for the action.
        
        Returns:
            dict: A dictionary containing the result of the control command.
        """
        logger.info(f"Camera control: {action} = {value}")
        
        if action == "horizontal":
            # Set the horizontal angle
            self.set_horizontal_angle(value)
            return {"success": True, "horizontal_angle": self.horizontal_angle}
        
        elif action == "vertical":
            # Set the vertical angle
            self.set_vertical_angle(value)
            return {"success": True, "vertical_angle": self.vertical_angle}
        
        else:
            logger.error(f"Unknown camera control action: {action}")
            return {"success": False, "error": f"Unknown action: {action}"}
    
    def set_horizontal_angle(self, angle):
        """Set the horizontal angle of the camera gimbal.
        
        Args:
            angle (float): The horizontal angle in degrees.
        """
        # Ensure the angle is within the valid range
        angle = max(self.horizontal_min, min(self.horizontal_max, angle))
        
        # Set the horizontal angle
        self.horizontal_angle = angle
        
        # In a real implementation, this would control the servo
        logger.info(f"Set horizontal angle to {angle} degrees.")
    
    def set_vertical_angle(self, angle):
        """Set the vertical angle of the camera gimbal.
        
        Args:
            angle (float): The vertical angle in degrees.
        """
        # Ensure the angle is within the valid range
        angle = max(self.vertical_min, min(self.vertical_max, angle))
        
        # Set the vertical angle
        self.vertical_angle = angle
        
        # In a real implementation, this would control the servo
        logger.info(f"Set vertical angle to {angle} degrees.")
    
    def joystick_control(self, x, y):
        """Control the camera gimbal using joystick input.
        
        Args:
            x (float): The x-axis value of the joystick (-1.0 to 1.0).
            y (float): The y-axis value of the joystick (-1.0 to 1.0).
        
        Returns:
            dict: A dictionary containing the result of the joystick command.
        """
        # Ensure x and y are within the valid range
        x = max(-1.0, min(1.0, x))
        y = max(-1.0, min(1.0, y))
        
        # Calculate the new angles
        horizontal_delta = x * 5.0  # 5 degrees per joystick unit
        vertical_delta = -y * 5.0   # 5 degrees per joystick unit (inverted)
        
        # Set the new angles
        self.set_horizontal_angle(self.horizontal_angle + horizontal_delta)
        self.set_vertical_angle(self.vertical_angle + vertical_delta)
        
        return {
            "success": True,
            "horizontal_angle": self.horizontal_angle,
            "vertical_angle": self.vertical_angle
        }
    
    def get_status(self):
        """Get the current status of the camera.
        
        Returns:
            dict: A dictionary containing the current status of the camera.
        """
        return {
            "running": self.running,
            "camera_index": self.camera_index,
            "frame_width": self.frame_width,
            "frame_height": self.frame_height,
            "fps": self.fps,
            "horizontal_angle": self.horizontal_angle,
            "vertical_angle": self.vertical_angle
        } 