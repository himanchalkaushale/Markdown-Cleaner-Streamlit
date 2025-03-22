#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown Cleaner

This script removes markdown formatting from text in the clipboard
and copies the clean text back to the clipboard.
"""

import re
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Try to import pyperclip, fallback to input/output if not available
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    logger.warning("Pyperclip not found. Install with: pip install pyperclip")
    logger.warning("Falling back to input/output mode.\n")
    CLIPBOARD_AVAILABLE = False


def remove_headers(text):
    """Remove Markdown headers (# Header)."""
    # Replace headers with their content (remove the # symbols)
    pattern = r'^([ \t]*)#{1,6}\s+(.*?)$'
    return re.sub(pattern, r'\1\2', text, flags=re.MULTILINE)


def remove_bold_italic(text):
    """Remove bold and italic formatting without changing spacing."""
    if not text:
        return text
        
    # Handle bold with ** (greedy approach to match most patterns)
    while '**' in text:
        # Find the positions of opening and closing **
        start_pos = text.find('**')
        if start_pos != -1:
            # Start after the first **
            search_pos = start_pos + 2
            # Find the next **
            end_pos = text.find('**', search_pos)
            if end_pos != -1:
                # Replace the entire pattern with just the content
                content = text[search_pos:end_pos]
                text = text[:start_pos] + content + text[end_pos+2:]
            else:
                # No matching closing **, move past this one
                break
                
    # Handle bold with __ (greedy approach to match most patterns)
    while '__' in text:
        # Find the positions of opening and closing __
        start_pos = text.find('__')
        if start_pos != -1:
            # Start after the first __
            search_pos = start_pos + 2
            # Find the next __
            end_pos = text.find('__', search_pos)
            if end_pos != -1:
                # Replace the entire pattern with just the content
                content = text[search_pos:end_pos]
                text = text[:start_pos] + content + text[end_pos+2:]
            else:
                # No matching closing __, move past this one
                break
    
    # Process line by line to handle italic properly
    lines = text.split('\n')
    for i, line in enumerate(lines):
        # Handle italic (* and _) - simple approach
        if '*' in line:
            # Try a few common patterns first
            # Asterisks with words on both sides, but spaces around the pattern
            lines[i] = re.sub(r'(\s)\*([^\s*][^*]*?[^\s*])\*(\s)', r'\1\2\3', lines[i])
            # Asterisk at start of line or after space but with word attached
            lines[i] = re.sub(r'(^|\s)\*([^\s*][^*]*?[^\s*])\*', r'\1\2', lines[i])
            # Asterisk around a word and at end of line
            lines[i] = re.sub(r'\*([^\s*][^*]*?[^\s*])\*($|\s)', r'\1\2', lines[i])
            
        # Similarly for underscores
        if '_' in line:
            # Underscore with words on both sides, but spaces around the pattern
            lines[i] = re.sub(r'(\s)_([^\s_][^_]*?[^\s_])_(\s)', r'\1\2\3', lines[i])
            # Underscore at start of line or after space but with word attached
            lines[i] = re.sub(r'(^|\s)_([^\s_][^_]*?[^\s_])_', r'\1\2', lines[i])
            # Underscore around a word and at end of line
            lines[i] = re.sub(r'_([^\s_][^_]*?[^\s_])_($|\s)', r'\1\2', lines[i])
            
    return '\n'.join(lines)


def remove_code_blocks(text):
    """Remove code blocks (``` or ~~~) and inline code (`) while preserving layout."""
    # Replace triple backtick code blocks with their content, preserving internal formatting
    text = re.sub(r'```(?:\w+)?\n(.*?)\n```', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'~~~(?:\w+)?\n(.*?)\n~~~', r'\1', text, flags=re.DOTALL)
    
    # Replace inline code with their content
    text = re.sub(r'`(.*?)`', r'\1', text)
    
    return text


def remove_links(text):
    """Remove Markdown links ([text](url)) and keep only the text."""
    # Replace [text](url) with text
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    
    # Replace <url> with url
    text = re.sub(r'<(https?://.*?)>', r'\1', text)
    
    return text


def remove_images(text):
    """Remove Markdown images (![alt](url)) and replace with alt text if available."""
    return re.sub(r'!\[(.*?)\]\(.*?\)', r'\1', text)


def remove_lists(text):
    """Remove bullet points and numbered lists while preserving indentation."""
    # Remove bullet points (*, -, +) but preserve indentation
    text = re.sub(r'^([ \t]*)[\*\-\+]\s+(.*?)$', r'\1\2', text, flags=re.MULTILINE)
    
    # Remove numbered lists (1., 2., etc.) but preserve indentation
    text = re.sub(r'^([ \t]*)\d+\.\s+(.*?)$', r'\1\2', text, flags=re.MULTILINE)
    
    return text


def remove_blockquotes(text):
    """Remove blockquotes (> text) while preserving indentation."""
    return re.sub(r'^([ \t]*)>\s+(.*?)$', r'\1\2', text, flags=re.MULTILINE)


def remove_horizontal_rules(text):
    """Remove horizontal rules (---, ***, ___) but keep the line breaks."""
    return re.sub(r'^(?:\*{3,}|-{3,}|_{3,})$', '', text, flags=re.MULTILINE)


def remove_tables(text):
    """Remove markdown tables while preserving spacing structure."""
    # Find table sections (lines with | characters and separator lines)
    table_pattern = r'((?:^.*\|.*$\n)+)'
    
    def process_table(match):
        table_text = match.group(1)
        rows = table_text.strip().split('\n')
        
        # Remove separator lines (like |---|---|)
        rows = [row for row in rows if not re.match(r'^[\s\|\-:]+$', row)]
        
        # Process each row to maintain column alignment as much as possible
        processed_rows = []
        for row in rows:
            # Split by pipe but keep spaces
            cells = []
            current_cell = ""
            in_cell = False
            
            for char in row:
                if char == '|':
                    if in_cell:  # End of a cell
                        cells.append(current_cell)
                        current_cell = ""
                    in_cell = True
                else:
                    if in_cell:
                        current_cell += char
            
            # Add the last cell if it exists
            if current_cell:
                cells.append(current_cell)
            
            # Filter out empty cells from start/end
            cells = [cell for cell in cells if cell.strip()]
            
            # Recreate the row with the original spacing but without pipes
            processed_rows.append('  '.join(cells))
        
        return '\n'.join(processed_rows) + '\n'
    
    return re.sub(table_pattern, process_table, text, flags=re.MULTILINE)


def force_remove_all_stars_and_underscores(text, options):
    """A brute force method to remove any remaining markdown formatting for bold/italic.
    This is a fallback method that should be used after the more targeted remove_bold_italic.
    """
    if not options.get('bold_italic', True):
        return text
    
    # Most direct approach to remove ** and __ regardless of content
    while '**' in text:
        text = text.replace('**', '')
    
    while '__' in text:
        text = text.replace('__', '')
    
    # Handle single asterisks carefully to avoid affecting math expressions
    lines = text.split('\n')
    for i in range(len(lines)):
        # Skip lines that are likely bullet points
        if not lines[i].strip().startswith('*') and '*' in lines[i]:
            # First try to find and replace the most common italic patterns
            lines[i] = re.sub(r'\s\*(\w[^*\n]*?)\*\s', r' \1 ', lines[i])
            lines[i] = re.sub(r'^\*(\w[^*\n]*?)\*\s', r'\1 ', lines[i])
            lines[i] = re.sub(r'\s\*(\w[^*\n]*?)\*$', r' \1', lines[i])
            
            # For more complex cases, if asterisks persist, only remove them if they seem like formatting
            if '*' in lines[i] and not re.search(r'[a-zA-Z0-9]\*[a-zA-Z0-9]', lines[i]):  # Skip potential math expressions
                lines[i] = lines[i].replace('*', '')
        
        # Similar approach for underscores
        if '_' in lines[i]:
            # First replace common italic patterns
            lines[i] = re.sub(r'\s_(\w[^_\n]*?)_\s', r' \1 ', lines[i])
            lines[i] = re.sub(r'^_(\w[^_\n]*?)_\s', r'\1 ', lines[i])
            lines[i] = re.sub(r'\s_(\w[^_\n]*?)_$', r' \1', lines[i])
            
            # Only remove remaining underscores if they look like formatting rather than snake_case variables
            if '_' in lines[i] and not re.search(r'[a-zA-Z0-9]_[a-zA-Z0-9]', lines[i]):
                lines[i] = lines[i].replace('_', '')
    
    return '\n'.join(lines)


def remove_markdown_formatting(text, options=None):
    """
    Remove markdown formatting from the given text based on selected options.
    
    Args:
        text (str): The text to process
        options (dict, optional): Dictionary with formatting options to remove.
            If None, removes all formatting. Example:
            {
                'headers': True,
                'bold_italic': True,
                'code_blocks': True,
                'links': True,
                'images': True,
                'lists': True,
                'blockquotes': True,
                'horizontal_rules': True,
                'tables': True
            }
    
    Returns:
        str: The cleaned text with selected formatting removed
    """
    if not text:
        return ""
    
    # If no options provided, remove all formatting
    if options is None:
        options = {
            'headers': True,
            'bold_italic': True,
            'code_blocks': True,
            'links': True,
            'images': True,
            'lists': True,
            'blockquotes': True,
            'horizontal_rules': True,
            'tables': True
        }
    
    # Process in a specific order to handle nested or complex formatting
    if options.get('code_blocks', True):
        text = remove_code_blocks(text)
    if options.get('headers', True):
        text = remove_headers(text)
    # Only remove bold/italic if specifically requested
    if options.get('bold_italic', True):
        text = remove_bold_italic(text)
        # Only apply forceful removal if bold/italic removal is enabled
        # This is critical to preserve bold/italic when option is unchecked
        text = force_remove_all_stars_and_underscores(text, options)
    if options.get('links', True):
        text = remove_links(text)
    if options.get('images', True):
        text = remove_images(text)
    if options.get('lists', True):
        text = remove_lists(text)
    if options.get('blockquotes', True):
        text = remove_blockquotes(text)
    if options.get('horizontal_rules', True):
        text = remove_horizontal_rules(text)
    if options.get('tables', True):
        text = remove_tables(text)
    
    # Clean up extra whitespace and blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    return text


def get_input_text():
    """Get text from clipboard or user input."""
    if CLIPBOARD_AVAILABLE:
        try:
            return pyperclip.paste()
        except Exception as e:
            logger.error(f"Error accessing clipboard: {e}")
            logger.info("Falling back to manual input.")
    
    logger.info("Enter the markdown text (press Ctrl+D or Ctrl+Z on Windows to finish):")
    return sys.stdin.read()


def clean_markdown():
    """Main function to clean markdown from clipboard or input."""
    # Get text from clipboard or input
    input_text = get_input_text()
    
    if not input_text:
        logger.warning("No text found to process.")
        return
    
    # Clean the markdown
    cleaned_text = remove_markdown_formatting(input_text)
    
    # Output the cleaned text
    logger.info("\n--- CLEANED TEXT ---")
    logger.info(cleaned_text)
    logger.info("-------------------")
    
    # Copy back to clipboard if available
    if CLIPBOARD_AVAILABLE:
        try:
            pyperclip.copy(cleaned_text)
            logger.info("Cleaned text copied to clipboard!")
        except Exception as e:
            logger.error(f"Error copying to clipboard: {e}")
    
    return cleaned_text


if __name__ == "__main__":
    clean_markdown()
