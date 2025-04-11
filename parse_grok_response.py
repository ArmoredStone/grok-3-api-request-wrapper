#!/usr/bin/env python3

import json
import sys
import argparse
import textwrap
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

def parse_grok_response(json_str):
    """Parse the Grok API JSON response string into a Python dictionary."""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)

def print_assistant_response(assistant_message):
    print("## AI Response\n")
    print(assistant_message)


def wrap_text_for_markdown(text, width=80):
    """Wrap text to prevent breaking Markdown tables."""
    if not text:
        return "N/A"
    
    # For multiline text, wrap each line separately and join with <br> for Markdown line breaks
    lines = str(text).split("\n")
    wrapped_lines = []
    
    for line in lines:
        if len(line) > width:
            # Wrap long lines
            wrapped = textwrap.fill(line, width=width)
            # Replace newlines with Markdown line breaks
            wrapped = wrapped.replace("\n", "<br>")
            wrapped_lines.append(wrapped)
        else:
            wrapped_lines.append(line)
    
    # Join all lines with Markdown line breaks
    return "<br>".join(wrapped_lines)

def format_response(response_data, wrap_width=80):
    """Format the parsed response data into a readable output using Rich library."""

    assistant_message = ""
    if "choices" in response_data and len(response_data["choices"]) > 0:
        assistant_message = response_data["choices"][0]["message"]["content"]
    
    # Create main response panel
    print("\n---\n")
    print_assistant_response(assistant_message)
    print("\n---\n")
    # Create metadata markdown table
    print("\n## Metadata\n")
    print("| Property | Value |")
    print("|----------|-------|")
    
    # Add basic metadata with wrapping for potentially long values
    print(f"| Response ID | {wrap_text_for_markdown(response_data.get('id', 'N/A'), wrap_width)} |")
    print(f"| Model | {wrap_text_for_markdown(response_data.get('model', 'N/A'), wrap_width)} |")
    
    created_time = response_data.get("created", None)
    if created_time:
        # Convert Unix timestamp to readable format
        time_str = datetime.fromtimestamp(created_time).strftime("%Y-%m-%d %H:%M:%S")
        print(f"| Created | {time_str} |")
    
    # Add finish reason
    if "choices" in response_data and len(response_data["choices"]) > 0:
        finish_reason = response_data["choices"][0].get("finish_reason", "N/A")
        print(f"| Finish Reason | {wrap_text_for_markdown(finish_reason, wrap_width)} |")
    
    # Add system fingerprint
    print(f"| System Fingerprint | {wrap_text_for_markdown(response_data.get('system_fingerprint', 'N/A'), wrap_width)} |")
    
    # Create token usage markdown table
    if "usage" in response_data:
        usage = response_data["usage"]
        print("\n## Token Usage\n")
        print("| Category | Count |")
        print("|----------|-------|")
        
        # Add main token counts
        print(f"| Prompt Tokens | {usage.get('prompt_tokens', 0)} |")
        print(f"| Completion Tokens | {usage.get('completion_tokens', 0)} |")
        print(f"| Total Tokens | {usage.get('total_tokens', 0)} |")
        
        # Add detailed token counts if available
        if "prompt_tokens_details" in usage or "completion_tokens_details" in usage:
            print("\n## Detailed Token Usage\n")
            print("| Category | Count |")
            print("|----------|-------|")
            
            ptd = usage.get("prompt_tokens_details", {})
            for key, value in ptd.items():
                formatted_key = f"Prompt: {key.replace('_', ' ').title()}"
                print(f"| {formatted_key} | {value} |")
                
            ctd = usage.get("completion_tokens_details", {})
            for key, value in ctd.items():
                formatted_key = f"Completion: {key.replace('_', ' ').title()}"
                print(f"| {formatted_key} | {value} |")

  



def main():
    parser = argparse.ArgumentParser(description="Parse and format Grok API responses")
    parser.add_argument("json_text", help="JSON text to parse")
    args = parser.parse_args()
    # Parse and format the response
    response_data = parse_grok_response(args.json_text)
    format_response(response_data)
    print("\n---\n")
    print(args.json_text)
    print("\n---\n")

if __name__ == "__main__":
    main()
