#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

import click
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def slugify(text: str) -> str:
    """Convert a heading text to a GitHub-style anchor ID."""
    # Convert to lowercase
    slug = text.lower()
    # Remove special characters, keep alphanumeric, spaces, and hyphens
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    # Remove consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    return slug


def extract_markdown_links(content: str) -> List[Tuple[str, str, str]]:
    """
    Extract markdown links from content.
    Returns list of tuples: (full_match, link_text, link_path)
    """
    # Match markdown links: [text](path)
    pattern = r'\[([^\]]+)\]\((\./[^\)]+\.md)\)'
    matches = re.findall(pattern, content)
    return [(f'[{text}]({path})', text, path) for text, path in matches]


def read_file(file_path: Path) -> str:
    """Read a file and return its content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        click.echo(f"Warning: File not found: {file_path}", err=True)
        return ""


def consolidate_readme_impl(readme_path: Path, output_path: Path) -> None:
    """
    Consolidate README with linked documents.
    
    Args:
        readme_path: Path to the main README.md file
        output_path: Path where the consolidated README should be written
    """
    base_dir = readme_path.parent
    
    # Read the main README
    main_content = read_file(readme_path)
    if not main_content:
        click.echo("Error: Could not read main README.md", err=True)
        sys.exit(1)
    
    # Extract all markdown links
    links = extract_markdown_links(main_content)
    
    # Build a mapping of link paths to their content and anchor
    link_map: Dict[str, Tuple[str, str, str]] = {}  # path -> (anchor, heading, content)
    
    for full_match, link_text, link_path in links:
        # Resolve the relative path
        # link_path is like "./doc/motivation.md"
        resolved_path = base_dir / link_path[2:]  # Remove "./" prefix
        
        if link_path in link_map:
            continue  # Already processed this document
        
        # Read the linked document
        doc_content = read_file(resolved_path)
        if not doc_content:
            continue
        
        # Use the link text as the heading to provide context
        # This ensures each section has a meaningful, unique heading
        # Clean up common articles from link text for better headings
        heading = link_text
        if heading.lower().startswith('the '):
            heading = heading[4:]  # Remove "the " prefix
        # Generate anchor from the cleaned heading so it matches
        anchor = slugify(heading)
        
        link_map[link_path] = (anchor, heading, doc_content)
    
    # Replace links in the main README with anchor links
    consolidated = main_content
    for full_match, link_text, link_path in links:
        if link_path in link_map:
            anchor, _, _ = link_map[link_path]
            # Replace the link with an anchor link
            new_link = f'[{link_text}](#{anchor})'
            consolidated = consolidated.replace(full_match, new_link)
    
    # Append all linked documents to the consolidated README
    for link_path, (anchor, heading, doc_content) in link_map.items():
        # Add a separator and the document content
        consolidated += f"\n\n---\n\n# {heading}\n\n"
        
        # Remove the first heading from doc_content since we're adding it above
        lines = doc_content.split('\n')
        content_lines = []
        found_first_heading = False
        for line in lines:
            if not found_first_heading and line.startswith('#'):
                found_first_heading = True
                continue
            if found_first_heading:
                content_lines.append(line)
        
        consolidated += '\n'.join(content_lines).strip()
    
    # Write the consolidated README
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(consolidated)
    
    click.echo(f"Consolidated README written to: {output_path}")


@click.command()
@click.argument('readme_path', type=click.Path(exists=True, path_type=Path))
@click.argument('output_path', type=click.Path(path_type=Path))
def consolidated_readme(readme_path: Path, output_path: Path) -> None:
    """
    Create a consolidated README by combining the main README with all linked documents.
    
    This command:
    1. Takes the main README.md
    2. Follows all links to other markdown documents
    3. Concatenates those documents inline with sensible headings
    4. Replaces cross-document links with doc-local anchor links
    """
    consolidate_readme_impl(readme_path, output_path)
