import streamlit as st
from google import genai
from PIL import Image

# 1. Set up the webpage design
st.set_page_config(page_title="SJ Council", page_icon="🏛️", layout="centered")
st.title("SJ Council 🏛️")
st.write("Run any decision, document, or image by your 5 AI advisors.")

# 2. Sidebar for API Key (Keeps it secure!)
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter your Gemini API Key:", type="password")
st.sidebar.markdown("*(Get your key from [Google AI Studio](https://aistudio.google.com))*")

# 3. Web App Inputs
question = st.text_area("What decision do you want to run by the council?", height=100)
uploaded_image = st.file_uploader("Attach an image for them to look at (optional)", type=["jpg", "jpeg", "png" , "webp"])

# 4. The Run Button
if st.button("Convene the Council", type="primary"):
    if not api_key:
        st.error("Please paste your API Key in the left sidebar first!")
        st.stop()
    if not question and not uploaded_image:
        st.error("Please type a question or upload an image.")
        st.stop()

    client = genai.Client(api_key=api_key)
    
    advisors = [
        {"name": "The Contrarian", "prompt": "You are the Contrarian. Tell me why this is a terrible idea and will fail."},
        {"name": "The First Principles Thinker", "prompt": "You are the First Principles Thinker. Ignore the surface-level question and strip away assumptions. What are we actually trying to solve here?"},
        {"name": "The Expansionist", "prompt": "You are the Expansionist. Tell me how this could be 10x bigger. Ignore risks and hunt for hidden upside."},
        {"name": "The Outsider", "prompt": "You are the Outsider. You have zero context about this field. Catch the curse of knowledge and point out what is obvious to the creator but confusing to everyone else."},
        {"name": "The Executor", "prompt": "You are the Executor. Ignore theory, what are the literal first 3 steps to do this today?"}
    ]

    # Process the image if one was uploaded
    img = None
    if uploaded_image:
        img = Image.open(uploaded_image)
        st.image(img, caption="Your Uploaded Image", use_container_width=True)

    responses = []
    st.subheader("--- Council Debating ---")
    
    # Run the advisors and show their thoughts on the webpage
    for advisor in advisors:
        with st.expander(f"{advisor['name']} is thinking...", expanded=True):
            # Combine text and image for the AI
            contents = [f"{advisor['prompt']}\n\nCRITICAL INSTRUCTION: If an image is provided, you MUST analyze its visual design, layout, and text to form your answer. The context is: {question}"]
            if img:
                contents.append(img)
            
            try:
                response = client.models.generate_content(
                    model='gemini-3.5-flash-lite', 
                    contents=contents
                )
                st.write(response.text)
                responses.append(f"{advisor['name']} says:\n{response.text}")
            except Exception as e:
                st.error(f"API Error: {e}")

    # Generate Chairman's final verdict
    if len(responses) == 5:
        st.subheader("=== CHAIRMAN'S FINAL VERDICT ===")
        all_advice = "\n".join(responses)
        chairman_prompt = f"You are the Chairman. Review all of this advice and give me a final recommendation:\n{all_advice}"
        
        with st.spinner("Chairman is writing the final verdict..."):
            try:
                chairman_response = client.models.generate_content(
                    model='gemini-3.5-flash-lite',
                    contents=chairman_prompt
                )
                st.success(chairman_response.text)
            except Exception as e:
                st.error(f"Error: {e}")