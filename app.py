#!/usr/bin/env python3
"""
Satish's AI Digital Resume - Hugging Face Spaces Entry Point
This file imports and launches the main Gradio app for deployment.
"""

# Import the demo from our main app
from digital_resume import demo

# For Hugging Face Spaces, simply expose the demo object
# HF Spaces will handle the launching automatically
if __name__ == "__main__":
    print("🚀 Launching Satish's AI Digital Resume on Hugging Face Spaces")
    # Use default launch settings for HF Spaces compatibility
    demo.launch()
