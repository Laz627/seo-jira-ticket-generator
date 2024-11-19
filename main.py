import streamlit as st
import openai
from docx import Document
import io
import requests
from datetime import datetime

def create_jira_ticket(api_key, inputs):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Create a detailed JIRA ticket for SEO work based on the following inputs:
    Purpose: {inputs['purpose']}
    Background: {inputs['background']}
    
    Please format the output following the template below and suggest a detailed workflow with time estimates:
    
    Purpose: [Enhanced version of user input]
    
    Background: [Enhanced version of user input]
    
    Definition of Done: [Based on purpose and background]
    
    User Persona: [Create appropriate persona]
    
    Stakeholders / Dependencies: [Suggest relevant stakeholders]
    
    OKRs / Goals: [Suggest alignment with common SEO objectives]
    
    Estimated Impact: [Provide realistic estimates]
    
    Timeliness / Urgency: [Suggest timeline]
    
    Detailed Workflow with Time Estimates:
    [Provide detailed steps with time estimates]
    """

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are an SEO expert creating detailed JIRA tickets."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }
        )
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

def save_as_docx(content):
    doc = Document()
    for line in content.split('\n'):
        doc.add_paragraph(line)
    return doc

def main():
    st.title("SEO JIRA Ticket Generator")
    
    st.markdown("""
    ### About This Tool
    Created by Brandon Lazovic
    
    This tool helps generate structured JIRA tickets for SEO work. Simply fill in the basic information,
    and the AI will help create a detailed ticket with workflow estimates.
    """)

    # API Key input
    api_key = st.text_input("Enter your OpenAI API Key", type="password")

    # Form inputs
    with st.form("jira_ticket_form"):
        purpose = st.text_area(
            "Purpose",
            help="What is this task?"
        )
        
        background = st.text_area(
            "Background",
            help="Additional context for the task"
        )
        
        urgency = st.selectbox(
            "Urgency Level",
            ["Low", "Medium", "High", "Critical"],
            help="Select the urgency level of this task"
        )
        
        submitted = st.form_submit_button("Generate Ticket")

    if submitted and api_key:
        inputs = {
            "purpose": purpose,
            "background": background,
            "urgency": urgency
        }
        
        with st.spinner("Generating ticket..."):
            ticket_content = create_jira_ticket(api_key, inputs)
            
            st.markdown("### Generated Ticket")
            st.text_area("Ticket Content", ticket_content, height=400)
            
            # Copy to clipboard button
            st.button("Copy to Clipboard", on_click=lambda: st.write(ticket_content))
            
            # Download as Word doc
            doc = save_as_docx(ticket_content)
            bio = io.BytesIO()
            doc.save(bio)
            
            st.download_button(
                label="Download as Word Document",
                data=bio.getvalue(),
                file_name=f"seo_ticket_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

if __name__ == "__main__":
    main()
