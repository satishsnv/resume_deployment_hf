#!/usr/bin/env python3
"""
Clean version of Satish's AI Digital Resume with working chat and proper UI
"""

import gradio as gr
import os
import json
import logging
import base64
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Configure OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    openai.api_key = api_key.strip().strip('"')  # Remove any quotes and whitespace
else:
    print("Warning: OPENAI_API_KEY not found in environment variables")
    
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "5000"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.5"))

# Load resume content
def load_resume_content():
    try:
        with open("static/Resume_satish_2025.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Resume content not found"

def get_profile_photo_base64():
    """Convert profile photo to base64 for embedding in HTML"""
    try:
        with open("static/satish_photo.jpeg", "rb") as f:
            image_data = f.read()
            base64_string = base64.b64encode(image_data).decode()
            return f"data:image/jpeg;base64,{base64_string}"
    except FileNotFoundError:
        return None

SATISH_RESUME = load_resume_content()

# Global conversation history
conversation_history = []

def get_exact_profile_data():
    """Return the exact same profile data as the original React app"""
    return {
        "name": "Seethepalli Naga Venkata Satish Kumar",
        "title": "Engineering Leader | Architect | Senior Manager",
        "description": "I'm Satish, an Engineering Leader with 18 years of experience in product development and leading high-performing teams to deliver innovative products. Curious about how my expertise aligns with your opportunities? Feel free to chat with me to explore my experience, and technical capabilities in detail!",
        "skills": ["Solution Architecture", "Microservices", "ML/Generative AI/Agentic AI", "Team Leadership", "AuthZ/AuthN", "Cloud"],
        "experience": "18 years",
        "current_role": "Senior Engineering Manager at Hitachi Vantara",
        "education": "M.Tech, IIT Delhi",
        "photo_url": "satish_photo.jpeg",
        "contact": {
            "email": "snvskiit@gmail.com",
            "mobile": "+91-9963699436",
            "github": "https://github.com/satishsnv/",
            "linkedin": "https://www.linkedin.com/in/satishsnv/"
        },
        "expertise_areas": [
            {
                "area": "Architecture & Design",
                "description": "Enterprise-scale solution architecture, microservices transformation, cloud-native design",
                "icon": "🏗️"
            },
            {
                "area": "Product Development", 
                "description": "End-to-end product lifecycle management, from ideation to production deployment",
                "icon": "🚀"
            },
            {
                "area": "AI/ML Solutions",
                "description": "GenAI applications, Integration and deployment of AI/ML models, intelligent agents using MCP protocol",
                "icon": "🤖"
            },
            {
                "area": "Team Leadership",
                "description": "Building & mentoring cross-functional teams, scaling engineering organizations",
                "icon": "👥"
            }
        ],
        "achievements": [
            "Architected and delivered AI/ML features from inception to production",
            "Spearheaded the development of GenAI-Companion using LLM, LangChain and RAG",
            "Built self sustaining teams with a focus on innovation and quality",            
            "Successfully transformed monolith architectures to scalable microservices"
        ]
    }

# Example questions removed for cleaner interface

def chat_with_satish(message, history):
    """Enhanced chat function with loader and proper tuple format for Gradio chatbot"""
    if not message.strip():
        return history, ""
    
    if history is None:
        history = []
    
    # Add user message and show thinking
    history.append((message, "🤔 Satish thinking..."))
    yield history, ""
    
    try:
        # Prepare system prompt with resume content
        system_prompt = f"""You are Satish, responding to messages as if you are him personally. Use the following resume and professional information about Satish to inform your responses:

            {SATISH_RESUME}...

            IMPORTANT INSTRUCTIONS:
            1. Respond as Satish in first person (use "I", "my", "me") 
            2. Be conversational and professional, as if you are Satish himself
            3. Draw from Satish's background, experience, and expertise when relevant
            4. If asked about technical topics, provide insights based on Satish's actual experience from the resume
            5. Stay in character as Satish throughout the conversation
            6. Be encouraging and supportive, especially for career-related questions
            7. Focus on information that's actually in the resume - don't make up details
            8. Keep responses focused and practical
            9. Use a professional yet approachable tone
            10. Provide responses in markdown format for better frontend rendering
            11. When discussing projects, refer to the specific work mentioned in the resume
            12. For contact information, use the details provided in the resume

            CONTACT DETAILS FROM RESUME:
            - Email: snvskiit@gmail.com
            - Phone: +91-9963699436
            - GitHub: https://github.com/satishsnv/
            - LinkedIn: https://www.linkedin.com/in/satishsnv/

            Remember: You ARE Satish, not an AI assistant representing him. Base all responses on the actual information in the resume provided above."""

        
        # Prepare messages for OpenAI - convert from tuple format to messages format
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (convert from tuples to messages, excluding thinking message)
        for user_msg, bot_msg in history[:-1]:  # Exclude the "thinking" message
            if "thinking" not in bot_msg:
                messages.append({"role": "user", "content": user_msg})
                messages.append({"role": "assistant", "content": bot_msg})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Call OpenAI API
        if openai.api_key:
            try:
                client = openai.OpenAI(api_key=openai.api_key)
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    max_tokens=MAX_TOKENS,
                    temperature=TEMPERATURE
                )
                ai_response = response.choices[0].message.content.strip()
            except Exception as api_error:
                print(f"OpenAI API Error: {api_error}")
                ai_response = f"I apologize, but I encountered an API error: {str(api_error)}. Please check your OpenAI API key and try again."
        else:
            ai_response = "OpenAI API key not configured. Please set your OPENAI_API_KEY in the .env file."
        
        # Replace the thinking message with actual response
        history[-1] = (message, ai_response)
        
        # Log conversation
        conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_message": message,
            "ai_response": ai_response,
            "model": MODEL_NAME
        })
        
        yield history, ""
        
    except Exception as e:
        error_msg = f"I apologize, but I encountered an error: {str(e)}. Please try again."
        history[-1] = (message, error_msg)
        yield history, ""

def create_exact_profile_html():
    """Create HTML that exactly matches the original React profile panel"""
    profile = get_exact_profile_data()
    photo_base64 = get_profile_photo_base64()
    
    # Create photo HTML with fallback
    if photo_base64:
        photo_html = f'''<div style="width: 120px; height: 120px; border-radius: 50%; margin: 0 auto 0.5rem auto; overflow: hidden; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);">
<img src="{photo_base64}" alt="Satish Kumar" style="width: 100%; height: 100%; object-fit: cover; object-position: center top; border-radius: 50%;">
</div>'''
    else:
        photo_html = '''<div style="width: 120px; height: 120px; border-radius: 50%; background: linear-gradient(135deg, #667eea, #764ba2); margin: 0 auto 0.5rem auto; display: flex; align-items: center; justify-content: center; font-size: 3rem; color: white; font-weight: bold; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);">
👨‍💼
</div>'''
    
    return f"""
<div style="text-align: center; color: #2d3748; padding: 0.5rem 0.4rem; overflow: hidden; max-height: 100%;">

{photo_html}

<h1 style="color: #2d3748; margin-bottom: 0.2rem; font-weight: 700; font-size: 1.4rem; line-height: 1.1;">{profile['name']}</h1>
<p style="color: #4a5568; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.4rem;">{profile['title']}</p>
<p style="color: #718096; line-height: 1.3; margin-bottom: 0.6rem; font-size: 0.8rem; max-width: 100%; margin-left: auto; margin-right: auto;">{profile['description']}</p>

<!-- Contact Information -->
<h3 style="color: #2d3748; margin: 0.8rem 0 0.5rem 0; font-weight: 600; text-align: center; font-size: 1rem; border-bottom: 2px solid #667eea; padding-bottom: 0.3rem; display: inline-block;">💼 Contact</h3>
<div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 1rem; margin-bottom: 0.8rem;">
<div style="display: flex; align-items: center; gap: 0.5rem; color: #2d3748; font-weight: 600; font-size: 0.85rem; padding: 0.5rem 1rem; background: #ffffff; border: 2px solid #e2e8f0; border-radius: 8px;">
📧 {profile['contact']['email']}
</div>
<div style="display: flex; align-items: center; gap: 0.5rem; color: #2d3748; font-weight: 600; font-size: 0.85rem; padding: 0.5rem 1rem; background: #ffffff; border: 2px solid #e2e8f0; border-radius: 8px;">
📱 {profile['contact']['mobile']}
</div>
<a href="{profile['contact']['github']}" target="_blank" style="display: flex; align-items: center; gap: 0.5rem; color: #2d3748; font-weight: 600; font-size: 0.85rem; text-decoration: none; padding: 0.5rem 1rem; background: #ffffff; border: 2px solid #e2e8f0; border-radius: 8px;">
🔗 GitHub
</a>
<a href="{profile['contact']['linkedin']}" target="_blank" style="display: flex; align-items: center; gap: 0.5rem; color: #2d3748; font-weight: 600; font-size: 0.85rem; text-decoration: none; padding: 0.5rem 1rem; background: #ffffff; border: 2px solid #e2e8f0; border-radius: 8px;">
� LinkedIn
</a>
</div>

<!-- Technical Skills -->
<h3 style="color: #2d3748; margin: 0.8rem 0 0.5rem 0; font-weight: 600; text-align: center; font-size: 1rem; border-bottom: 2px solid #667eea; padding-bottom: 0.3rem; display: inline-block;">⚡ Skills</h3>
<div style="display: flex; flex-wrap: nowrap; justify-content: center; gap: 0.3rem; margin-bottom: 0.8rem; overflow-x: auto;">
{' '.join([f'<span style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 0.3rem 0.6rem; border-radius: 20px; font-size: 0.7rem; font-weight: 600; white-space: nowrap;">{skill}</span>' for skill in profile['skills']])}
</div>

<!-- Areas of Expertise -->
<h3 style="color: #2d3748; margin: 0.8rem 0 0.5rem 0; font-weight: 600; text-align: center; font-size: 1rem; border-bottom: 2px solid #667eea; padding-bottom: 0.3rem; display: inline-block;">🎯 Expertise</h3>
<div style="display: flex; flex-wrap: nowrap; justify-content: center; gap: 0.4rem; margin-bottom: 0.8rem; overflow-x: auto;">
{' '.join([f'''
<div style="background: rgba(255, 255, 255, 0.3); backdrop-filter: blur(5px); padding: 0.7rem 0.6rem; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.4); text-align: center; min-width: 160px; max-width: 180px;">
<div style="font-size: 1.3rem; margin-bottom: 0.3rem;">{area['icon']}</div>
<h4 style="color: #2d3748; margin: 0 0 0.3rem 0; font-weight: 700; font-size: 0.9rem; line-height: 1.1;">{area['area']}</h4>
<p style="color: #4a5568; margin: 0; font-size: 0.7rem; line-height: 1.2; text-align: center; font-weight: 500;">{area['description']}</p>
</div>
''' for area in profile['expertise_areas']])}
</div>

<!-- Key Achievements -->
<h3 style="color: #2d3748; margin: 0.8rem 0 0.5rem 0; font-weight: 600; text-align: center; font-size: 1rem; border-bottom: 2px solid #667eea; padding-bottom: 0.3rem; display: inline-block;">🏆 Achievements</h3>
<div style="text-align: left; margin-bottom: 0.5rem;">
{' '.join([f'<div style="background: rgba(255, 255, 255, 0.3); backdrop-filter: blur(5px); padding: 0.6rem 0.8rem; margin-bottom: 0.4rem; border-radius: 8px; border-left: 4px solid #667eea; color: #2d3748; font-size: 0.8rem; line-height: 1.3; font-weight: 500;">{achievement}</div>' for achievement in profile['achievements']])}
</div>

</div>
    """

# Clean CSS for proper UI
clean_css = """
.gradio-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    font-family: 'Inter', sans-serif !important;
    min-height: 100vh !important;
    max-height: 100vh !important;
    padding: 1rem !important;
    overflow: hidden !important;
}

footer { display: none !important; }

.main-grid {
    display: grid !important;
    grid-template-columns: 1fr 1fr !important;
    gap: 1.5rem !important;
    min-height: calc(100vh - 2rem) !important;
    width: 100% !important;
    align-items: stretch !important;
}

.profile-section {
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 16px !important;
    padding: 0 !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
    height: calc(100vh - 2rem) !important;
    overflow-y: auto !important;
    display: flex !important;
    flex-direction: column !important;
}

.chat-section {
    display: flex !important;
    flex-direction: column !important;
    height: calc(100vh - 2rem) !important;
    gap: 1rem !important;
}

.chat-messages {
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 16px !important;
    flex: 1 !important;
    overflow: hidden !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
}

.chat-input-row {
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 16px !important;
    padding: 1rem !important;
    display: flex !important;
    gap: 0.75rem !important;
    align-items: center !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
}

.gr-button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.4rem 0.6rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
    margin-bottom: 0.3rem !important;
    width: 100% !important;
    height: 35px !important;
}

.gr-button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4) !important;
}

.clear-btn {
    background: #e53e3e !important;
}

.clear-btn:hover {
    background: #c53030 !important;
}

.gr-textbox input {
    border: 2px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 0.75rem 1rem !important;
    font-size: 0.9rem !important;
    outline: none !important;
    transition: all 0.3s ease !important;
}

.gr-textbox input:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
}

@media (max-width: 1024px) {
    .main-grid {
        grid-template-columns: 1fr !important;
        grid-template-rows: auto 1fr !important;
    }
    
    .profile-section {
        max-height: 50vh !important;
    }
    
    .chat-section {
        height: 50vh !important;
    }
}
"""

# Create the main interface
with gr.Blocks(
    title="🤖 Satish's AI Digital Resume",
    theme=gr.themes.Soft(primary_hue="blue", secondary_hue="purple"),
    css=clean_css
) as demo:
    
    with gr.Row(elem_classes=["main-grid"]):
        # Profile Panel
        with gr.Column(scale=1, elem_classes=["profile-section"]):
            profile_html = gr.HTML(
                value=create_exact_profile_html(),
                elem_classes=["profile-content"]
            )
        
        # Chat Panel
        with gr.Column(scale=1, elem_classes=["chat-section"]):
            # Chat Messages
            chatbot = gr.Chatbot(
                height=400,
                elem_classes=["chat-messages"]
            )
            
            # Input Row
            with gr.Row(elem_classes=["chat-input-row"]):
                msg_input = gr.Textbox(
                    placeholder="Type your message here...",
                    label="",
                    lines=1,
                    scale=8,
                    container=False
                )
                with gr.Column(scale=1, min_width=60):
                    send_btn = gr.Button("📤", size="sm")
                    clear_btn = gr.Button("🗑️", size="sm", elem_classes=["clear-btn"])

    # Event handlers
    def respond(message, history):
        if not message.strip():
            return history, ""
        # Use yield from to handle the generator
        yield from chat_with_satish(message, history)
    
    def clear_chat():
        return [], ""
    
    # Connect events
    msg_input.submit(respond, [msg_input, chatbot], [chatbot, msg_input])
    send_btn.click(respond, [msg_input, chatbot], [chatbot, msg_input])
    clear_btn.click(clear_chat, outputs=[chatbot, msg_input])

# Launch
if __name__ == "__main__":
    print("🚀 Starting Satish's AI Digital Resume - Clean Version")
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
