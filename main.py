import streamlit as st
from markdown_cleaner import remove_markdown_formatting
import re

# Set page config
st.set_page_config(
    page_title="Markdown Cleaner",
    page_icon="📝",
    layout="centered"
)

# Custom CSS to match Replit theme
st.markdown("""
<style>
    /* Apply dark theme colors */
    .stApp {
        background-color: #0E1525;
        color: #F5F9FC;
    }
    .stTextArea > div > div {
        background-color: #1C2333;
        color: #F5F9FC;
    }
    .stButton > button {
        background-color: #2B3245;
        color: #F5F9FC;
        border: 1px solid #3C445C;
    }
    .stButton > button:hover {
        background-color: #3C445C;
        color: #F5F9FC;
    }
    /* Output text area styling */
    .output-area {
        background-color: #1C2333;
        border-radius: 4px;
        padding: 10px;
        font-family: monospace;
        white-space: pre-wrap;
        margin-top: 10px;
    }
    /* Download button styling */
    [data-testid="stDownloadButton"] button {
        background-color: #FFFF00 !important;
        color: #000000 !important;
        border: 1px solid #FFD700 !important;
    }
    [data-testid="stDownloadButton"] button:hover {
        background-color: #FFD700 !important;
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.title("Markdown Cleaner")
st.markdown("Remove markdown formatting from your text. Paste your markdown text below and get clean, plain text.")

# Input text area
markdown_text = st.text_area("Paste your markdown text here:", height=200)

# Formatting options - Allow users to select which markdown elements to remove
st.subheader("Select markdown elements to remove:")

# Create columns for the checkboxes to make the UI more compact
col1, col2, col3 = st.columns(3)

with col1:
    remove_headers = st.checkbox("Headers (# Title)", value=True)
    remove_bold_italic = st.checkbox("Bold and Italic (**bold**, *italic*)", value=False)  # Default to False to keep bold/italic
    remove_code = st.checkbox("Code Blocks (```code```)", value=True)

with col2:
    remove_links = st.checkbox("Links ([text](url))", value=True)
    remove_images = st.checkbox("Images (![alt](url))", value=True)
    remove_lists = st.checkbox("Lists (*, 1., etc.)", value=True)

with col3:
    remove_blockquotes = st.checkbox("Blockquotes (> text)", value=True)
    remove_hr = st.checkbox("Horizontal Rules (---, ***)", value=True)
    remove_tables = st.checkbox("Tables (| cell | cell |)", value=True)

# Create a formatting options dictionary
formatting_options = {
    'headers': remove_headers,
    'bold_italic': remove_bold_italic,
    'code_blocks': remove_code,
    'links': remove_links,
    'images': remove_images,
    'lists': remove_lists,
    'blockquotes': remove_blockquotes,
    'horizontal_rules': remove_hr,
    'tables': remove_tables
}

# Process the markdown text when the button is clicked
if markdown_text:
    if st.button("Clean Markdown"):
        # Process the markdown text with selected options
        cleaned_text = remove_markdown_formatting(markdown_text, formatting_options)
        
        # Store the cleaned text in session state to persist across re-runs
        st.session_state.cleaned_text = cleaned_text
        st.session_state.show_result = True
        st.session_state.formatting_options = formatting_options  # Save the options used

# Check if we have a result to display from the current or previous run
if markdown_text and ('show_result' in st.session_state and st.session_state.show_result):
    # Get the cleaned text from the session state
    cleaned_text = st.session_state.cleaned_text
    
    # Display the cleaned text
    st.subheader("Cleaned Text:")
    # Use st.code with no language to show plain text but preserve formatting
    st.code(cleaned_text, language=None)
    
    # Create a container for the copy functionality
    copy_col1, copy_col2 = st.columns([1, 3])
    
    # Add a copy button in the first column
    if copy_col1.button("Copy to Clipboard"):
        # Use JavaScript to copy to clipboard
        js = f"""
        <script>
        navigator.clipboard.writeText({repr(cleaned_text)}).then(function() {{
            document.getElementById('success-message').style.display = 'block';
        }});
        </script>
        <div id="success-message" style="display: none; color: green;">Text copied to clipboard!</div>
        """
        st.markdown(js, unsafe_allow_html=True)
        st.success("Text copied!")
    
    # Show a download button in the second column
    download_btn = copy_col2.download_button(
        label="Download as Text File",
        data=cleaned_text,
        file_name="cleaned_text.txt",
        mime="text/plain"
    )
    
elif markdown_text:
    st.info("Click the 'Clean Markdown' button to process your text.")
else:
    st.warning("Please enter some markdown text to clean.")

# Add information about the features
with st.expander("About this tool"):
    st.markdown("""
    ### Markdown Cleaner for AI-Generated Text
    
    This tool helps you clean up markdown formatting from text, especially useful for AI-generated answers. 
    
    #### How to use:
    1. Paste your markdown text in the input area
    2. Select which formatting elements you want to remove using the checkboxes
    3. Click "Clean Markdown" to process the text
    4. Copy or download the cleaned result
    
    #### Benefits:
    - Selectively remove only the formatting elements you don't want
    - Preserves original text layout, spacing, and indentation
    - Perfect for cleaning up AI assistant responses while keeping the content intact
    - Easy to use with a simple, intuitive interface
    """)

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and Python by Himanchal Kaushale")
