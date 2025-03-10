#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Speech Engine Module for AI Smart Car
This module handles text-to-speech functionality.
"""

import os
import logging
import threading
import time
import langid
import pyttsx3

# Configure logging
logger = logging.getLogger(__name__)

class SpeechEngine:
    """Speech engine for text-to-speech functionality."""
    
    def __init__(self):
        """Initialize the speech engine."""
        logger.info("Initializing speech engine...")
        
        # TTS parameters
        self.rate = int(os.getenv('TTS_RATE', 150))  # Speaking rate (words per minute)
        self.volume = float(os.getenv('TTS_VOLUME', 1.0))  # Volume (0.0 to 1.0)
        
        # Speech state
        self.speaking = False
        self.speech_queue = []
        self.speech_thread = None
        self.speech_lock = threading.Lock()
        
        # Initialize the TTS engine
        self._init_tts_engine()
        
        logger.info("Speech engine initialized.")
    
    def _init_tts_engine(self):
        """Initialize the text-to-speech engine."""
        logger.info("Initializing TTS engine...")
        
        try:
            # Initialize pyttsx3
            self.engine = pyttsx3.init()
            
            # Set properties
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            if voices:
                # Set the default voice (usually the first one)
                self.engine.setProperty('voice', voices[0].id)
            
            logger.info("TTS engine initialized successfully.")
            
            # Start the speech thread
            self.speech_thread = threading.Thread(target=self._speech_loop)
            self.speech_thread.daemon = True
            self.speech_thread.start()
        except Exception as e:
            logger.error(f"Error initializing TTS engine: {e}")
            self.engine = None
    
    def _speech_loop(self):
        """Main speech loop."""
        logger.info("Speech loop started.")
        
        while True:
            # Check if there's anything in the speech queue
            with self.speech_lock:
                if self.speech_queue:
                    # Get the next text to speak
                    text = self.speech_queue.pop(0)
                    self.speaking = True
                else:
                    self.speaking = False
                    # Sleep for a short time before checking again
                    time.sleep(0.1)
                    continue
            
            try:
                # Speak the text
                logger.info(f"Speaking: {text}")
                
                if self.engine:
                    # Detect language
                    lang, _ = langid.classify(text)
                    
                    # Adjust rate based on language
                    if lang == 'zh':  # Chinese
                        self.engine.setProperty('rate', self.rate * 0.8)
                    else:
                        self.engine.setProperty('rate', self.rate)
                    
                    # Speak the text
                    self.engine.say(text)
                    self.engine.runAndWait()
                else:
                    logger.warning("TTS engine is not initialized.")
            except Exception as e:
                logger.error(f"Error speaking text: {e}")
            finally:
                with self.speech_lock:
                    self.speaking = False
    
    def speak(self, text):
        """Speak the given text.
        
        Args:
            text (str): The text to speak.
        """
        if not text:
            return
        
        logger.info(f"Adding text to speech queue: {text}")
        
        # Add the text to the speech queue
        with self.speech_lock:
            self.speech_queue.append(text)
    
    def is_speaking(self):
        """Check if the speech engine is currently speaking.
        
        Returns:
            bool: True if the speech engine is speaking, False otherwise.
        """
        with self.speech_lock:
            return self.speaking
    
    def set_rate(self, rate):
        """Set the speaking rate.
        
        Args:
            rate (int): The speaking rate in words per minute.
        """
        logger.info(f"Setting speaking rate to {rate}")
        
        self.rate = rate
        
        if self.engine:
            self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume):
        """Set the speaking volume.
        
        Args:
            volume (float): The speaking volume (0.0 to 1.0).
        """
        logger.info(f"Setting speaking volume to {volume}")
        
        # Ensure volume is within the valid range
        volume = max(0.0, min(1.0, volume))
        
        self.volume = volume
        
        if self.engine:
            self.engine.setProperty('volume', volume) 