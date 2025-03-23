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
    pattern = r'^([ \t]*)#{1,6}\s+(.*?)$'
    return re.sub(pattern, r'\1\2', text, flags=re.MULTILINE)


def remove_bold_italic(text):
    """Remove bold and italic formatting without changing spacing."""
    if not text:
        return text

    # Handle bold with ** and __
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'__(.*?)__', r'\1', text)      # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)       # Italic
    text = re.sub(r'_(.*?)_', r'\1', text)         # Italic

    return text


def remove_code_blocks(text):
    """Remove code blocks (``` or ~~~) and inline code (`) while preserving layout."""
    text = re.sub(r'```(?:\w+)?\n(.*?)\n```', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'~~~(?:\w+)?\n(.*?)\n~~~', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'`(.*?)`', r'\1', text)
    return text


def remove_links(text):
    """Remove Markdown links ([text](url)) and keep only the text."""
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'<(https?://.*?)>', r'\1', text)
    return text


def remove_images(text):
    """Remove Markdown images (![alt](url)) and replace with alt text if available."""
    return re.sub(r'!\[(.*?)\]\(.*?\)', r'\1', text)


def remove_lists(text):
    """Remove bullet points and numbered lists while preserving indentation."""
    text = re.sub(r'^([ \t]*)[\*\-\+]\s+(.*?)$', r'\1\2', text, flags=re.MULTILINE)
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
    return re.sub(r'^\|.*?\|\s*$', '', text, flags=re.MULTILINE)


def remove_markdown_formatting(text, options=None):
    """
    Remove markdown formatting from the given text based on selected options.
    
    Args:
        text (str): The text to process
        options (dict, optional): Dictionary with formatting options to remove.
            If None, removes all formatting.
    
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
    if options.get('headers', True):
        text = remove_headers(text)
    if options.get('bold_italic', True):
        text = remove_bold_italic(text)
    if options.get('code_blocks', True):
        text = remove_code_blocks(text)
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

    return text.strip()  # Remove leading/trailing whitespace after processing


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
    input_text = get_input_text()

    if not input_text:
        logger.warning("No text found to process.")
        return

    cleaned_text = remove_markdown_formatting(input_text)

    logger.info("\n--- CLEANED TEXT ---")
    logger.info(cleaned_text)
    logger.info("-------------------")

    if CLIPBOARD_AVAILABLE:
        try:
            pyperclip.copy(cleaned_text)
            logger.info("Cleaned text copied to clipboard!")
        except Exception as e:
            logger.error(f"Error copying to clipboard: {e}")

    return cleaned_text


if __name__ == "__main__":
    clean_markdown()
