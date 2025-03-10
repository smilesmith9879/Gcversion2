#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Smart Four-Wheel Drive Car - Main Application
This is the main entry point for the AI Smart Car application.
It initializes and coordinates all the components of the system.
"""

import os
import sys
import time
import logging
import threading
import signal
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components
from src.web.app import create_app, socketio
from src.control.robot import RobotController
from src.vision.camera import CameraManager
from src.ai.assistant import AIAssistant
from src.utils.speech import SpeechEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ai_car.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AISmartCar:
    """Main class for the AI Smart Car application."""
    
    def __init__(self):
        """Initialize the AI Smart Car application."""
        logger.info("Initializing AI Smart Car...")
        
        # Initialize components
        self.robot = RobotController()
        self.camera = CameraManager()
        self.speech = SpeechEngine()
        self.ai_assistant = AIAssistant(self.speech)
        
        # Create Flask app
        self.app = create_app(self.robot, self.camera, self.ai_assistant)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logger.info("AI Smart Car initialized successfully.")
        
        # Welcome message
        self.speech.speak("AI Smart Car system is ready.")
    
    def start(self):
        """Start the AI Smart Car application."""
        logger.info("Starting AI Smart Car...")
        
        # Start the robot controller
        self.robot.start()
        
        # Start the camera
        self.camera.start()
        
        # Start the AI assistant
        self.ai_assistant.start()
        
        # Start the web server
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 5000))
        logger.info(f"Starting web server on {host}:{port}")
        
        # Run the Flask app with SocketIO
        socketio.run(self.app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)
    
    def stop(self):
        """Stop the AI Smart Car application."""
        logger.info("Stopping AI Smart Car...")
        
        # Stop the robot controller
        self.robot.stop()
        
        # Stop the camera
        self.camera.stop()
        
        # Stop the AI assistant
        self.ai_assistant.stop()
        
        logger.info("AI Smart Car stopped successfully.")
    
    def signal_handler(self, sig, frame):
        """Handle signals for graceful shutdown."""
        logger.info(f"Received signal {sig}, shutting down...")
        self.stop()
        sys.exit(0)

if __name__ == "__main__":
    # Create and start the AI Smart Car application
    car = AISmartCar()
    try:
        car.start()
    except Exception as e:
        logger.error(f"Error in main application: {e}")
        car.stop()
        sys.exit(1) 