#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Web Application Module for AI Smart Car
This module provides the web interface for controlling the AI Smart Car.
"""

import os
import logging
import json
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

# Configure logging
logger = logging.getLogger(__name__)

# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*")

def create_app(robot_controller, camera_manager, ai_assistant):
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Configure app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'ai-smart-car-secret-key')
    
    # Initialize SocketIO with the app
    socketio.init_app(app)
    
    # Store components
    app.config['ROBOT'] = robot_controller
    app.config['CAMERA'] = camera_manager
    app.config['AI_ASSISTANT'] = ai_assistant
    
    # Register routes
    @app.route('/')
    def index():
        """Render the main control interface."""
        return render_template('index.html')
    
    @app.route('/api/status')
    def status():
        """Get the status of the AI Smart Car."""
        return jsonify({
            'robot': robot_controller.get_status(),
            'camera': camera_manager.get_status(),
            'ai': ai_assistant.get_status()
        })
    
    # WebRTC routes
    @app.route('/api/webrtc/offer', methods=['POST'])
    def webrtc_offer():
        """Handle WebRTC offer for video streaming."""
        offer = request.json
        answer = camera_manager.process_offer(offer)
        return jsonify(answer)
    
    # SocketIO event handlers
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        logger.info(f"Client connected: {request.sid}")
        emit('status', {'status': 'connected'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        logger.info(f"Client disconnected: {request.sid}")
    
    @socketio.on('control')
    def handle_control(data):
        """Handle control commands from the client."""
        logger.debug(f"Received control command: {data}")
        command = data.get('command')
        params = data.get('params', {})
        
        if command == 'move':
            # Extract movement parameters
            direction = params.get('direction')
            speed = params.get('speed', 0.5)
            duration = params.get('duration')
            
            # Execute movement command
            result = robot_controller.move(direction, speed, duration)
            emit('control_response', {'status': 'ok', 'result': result})
        
        elif command == 'camera':
            # Extract camera parameters
            action = params.get('action')
            value = params.get('value')
            
            # Execute camera command
            result = camera_manager.control(action, value)
            emit('control_response', {'status': 'ok', 'result': result})
        
        else:
            emit('control_response', {'status': 'error', 'message': f'Unknown command: {command}'})
    
    @socketio.on('joystick')
    def handle_joystick(data):
        """Handle joystick input from the client."""
        logger.debug(f"Received joystick input: {data}")
        joystick_type = data.get('type')
        x = data.get('x', 0)
        y = data.get('y', 0)
        
        if joystick_type == 'movement':
            # Control robot movement
            robot_controller.joystick_control(x, y)
        
        elif joystick_type == 'camera':
            # Control camera position
            camera_manager.joystick_control(x, y)
        
        emit('joystick_response', {'status': 'ok'})
    
    @socketio.on('voice')
    def handle_voice(data):
        """Handle voice input from the client."""
        logger.info(f"Received voice input")
        audio_data = data.get('audio')
        
        if audio_data:
            # Process voice command
            result = ai_assistant.process_voice(audio_data)
            emit('voice_response', {'status': 'ok', 'result': result})
        else:
            emit('voice_response', {'status': 'error', 'message': 'No audio data received'})
    
    @socketio.on('text')
    def handle_text(data):
        """Handle text input from the client."""
        logger.info(f"Received text input: {data}")
        text = data.get('text')
        
        if text:
            # Process text command
            result = ai_assistant.process_text(text)
            emit('text_response', {'status': 'ok', 'result': result})
        else:
            emit('text_response', {'status': 'error', 'message': 'No text received'})
    
    # Register error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500
    
    return app 