# Markdown Cleaner

A tool to clean markdown formatting from text while preserving the original layout and structure.

## Features

- **Selective Cleaning**: Choose which markdown elements to remove (headers, links, code blocks, etc.)
- **Preserve Formatting**: Keep bold and italic formatting by default if desired
- **Copy or Download**: Easily copy cleaned text to clipboard or download as a text file
- **User-Friendly Interface**: Simple and intuitive Streamlit-based web interface

## Use Cases

- Clean up AI-generated text while preserving important formatting
- Convert markdown to plain text while maintaining readability
- Prepare content for platforms that don't support markdown

## Installation

```bash
# Clone the repository
git clone https://github.com/himanchalkaushale/markdown-cleaner.git
cd markdown-cleaner

# Create requirements.txt from dependencies.txt (if needed)
cp dependencies.txt requirements.txt

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the Streamlit app
streamlit run main.py
```

Then open your browser and navigate to the provided URL (typically http://localhost:8501).

## How to Use

1. Paste your markdown text in the input area
2. Select which formatting elements you want to remove using the checkboxes
3. Click "Clean Markdown" to process the text
4. Copy the cleaned text to clipboard or download as a text file

## Requirements

- Python 3.6 or higher
- Streamlit
- Pyperclip (optional, for clipboard functionality)

## License

MIT

## Author

Himanchal Kaushale