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
    
    prompt = f"""Create a concise JIRA ticket for SEO work based on the following inputs:
    Title: {inputs['title']}
    Purpose: {inputs['purpose']}
    Background: {inputs['background']}
    
    Format the response in plain text using this exact structure:
    
    Title: {inputs['title']}

    Purpose:
    [2-3 sentences maximum]

    Background:
    [2-3 sentences maximum]

    Definition of Done:
    [3-5 bullet points]

    User Persona:
    [1-2 sentences describing the end user]

    Stakeholders / Dependencies:
    [List only key stakeholders, maximum 3]

    OKRs / Goals:
    [1-2 specific goals]

    Estimated Impact:
    [1-2 sentences on potential outcomes]

    Timeliness / Urgency:
    [1 sentence on timeline]

    Anticipated Workflow:
    [List 5-7 key steps. IMPORTANT: Total timeline must not exceed 4 weeks. Break down estimates in days or weeks, ensuring the total is between 1-4 weeks maximum]
    """

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are an SEO expert creating concise JIRA tickets. Keep responses brief and focused. Ensure all work estimates fall within 1-4 weeks maximum."},
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
        if line.strip():  # Only add non-empty lines
            doc.add_paragraph(line.strip())
    return doc

def main():
    st.title("SEO JIRA Ticket Generator")
    
    st.write("""
    A tool to generate structured JIRA tickets for SEO work.
    Created by Brandon Lazovic
    """)

    api_key = st.text_input("OpenAI API Key", type="password")

    with st.form("jira_ticket_form"):
        title = st.text_input(
            "JIRA Ticket Title",
            help="Enter a descriptive title for the JIRA ticket"
        )
        
        purpose = st.text_area(
            "Purpose",
            help="Brief description of the task (1-2 sentences)"
        )
        
        background = st.text_area(
            "Background",
            help="Quick context about the task (1-2 sentences)"
        )
        
        urgency = st.selectbox(
            "Urgency",
            ["Low", "Medium", "High", "Critical"]
        )
        
        submitted = st.form_submit_button("Generate Ticket")

    if submitted and api_key:
        inputs = {
            "title": title,
            "purpose": purpose,
            "background": background,
            "urgency": urgency
        }
        
        with st.spinner("Generating..."):
            ticket_content = create_jira_ticket(api_key, inputs)
            
            st.text_area("Generated Ticket", value=ticket_content, height=400)
            
            # Using Streamlit's built-in clipboard functionality
            st.code(ticket_content, language=None)  # This creates a copyable code block
            st.info("👆 Click the copy button in the top-right corner of the box above to copy the content")
            
            doc = save_as_docx(ticket_content)
            bio = io.BytesIO()
            doc.save(bio)
            
            st.download_button(
                label="Download as Word",
                data=bio.getvalue(),
                file_name=f"seo_ticket_{datetime.now().strftime('%Y%m%d')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

if __name__ == "__main__":
    main()
