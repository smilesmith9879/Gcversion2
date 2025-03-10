#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Smart Car - Run Script
This script runs the AI Smart Car application.
"""

import os
import sys
from src.main import AISmartCar

if __name__ == "__main__":
    # Create and start the AI Smart Car application
    car = AISmartCar()
    try:
        car.start()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Shutting down...")
        car.stop()
        sys.exit(0)
    except Exception as e:
        print(f"Error in main application: {e}")
        car.stop()
        sys.exit(1) 