import os
import json
import requests
from dotenv import load_dotenv
from figma_debug import debug_node_response, find_node_by_id, log_node_structure, improve_node_id

# Load environment variables
load_dotenv()

# Figma API configuration
FIGMA_API_KEY = os.getenv("FIGMA_API_KEY")
FIGMA_API_BASE = "https://api.figma.com/v1"

def get_figma_file(file_key):
    """Get a Figma file's data using the Figma API"""
    headers = {
        "X-Figma-Token": FIGMA_API_KEY
    }
    
    url = f"{FIGMA_API_BASE}/files/{file_key}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch Figma file: {response.text}")
    
    return response.json()

def get_figma_node(file_key, node_id):
    """Get a specific node from a Figma file"""
    headers = {
        "X-Figma-Token": FIGMA_API_KEY
    }
    
    url = f"{FIGMA_API_BASE}/files/{file_key}/nodes?ids={node_id}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch Figma node: {response.text}")
    
    return response.json()

def parse_node_styles(node):
    """Extract CSS styles from a Figma node"""
    styles = {}
    
    # Extract dimensions
    if "absoluteBoundingBox" in node:
        bbox = node["absoluteBoundingBox"]
        styles["width"] = f"{bbox.get('width', 'auto')}px"
        styles["height"] = f"{bbox.get('height', 'auto')}px"
    
    # Extract fills (background colors)
    if "fills" in node and node["fills"]:
        for fill in node["fills"]:
            if fill.get("type") == "SOLID" and fill.get("visible", True):
                color = fill.get("color", {})
                r = int(color.get("r", 0) * 255)
                g = int(color.get("g", 0) * 255)
                b = int(color.get("b", 0) * 255)
                a = color.get("a", 1)
                styles["backgroundColor"] = f"rgba({r}, {g}, {b}, {a})"
                break
    
    # Extract border radius
    if "cornerRadius" in node:
        styles["borderRadius"] = f"{node['cornerRadius']}px"
    
    # Extract strokes (borders)
    if "strokes" in node and node["strokes"]:
        for stroke in node["strokes"]:
            if stroke.get("type") == "SOLID" and stroke.get("visible", True):
                color = stroke.get("color", {})
                r = int(color.get("r", 0) * 255)
                g = int(color.get("g", 0) * 255)
                b = int(color.get("b", 0) * 255)
                a = color.get("a", 1)
                styles["border"] = f"{node.get('strokeWeight', 1)}px solid rgba({r}, {g}, {b}, {a})"
                break
    
    # Add more style properties
    # Extract padding
    if "paddingLeft" in node:
        styles["paddingLeft"] = f"{node['paddingLeft']}px"
    if "paddingRight" in node:
        styles["paddingRight"] = f"{node['paddingRight']}px"
    if "paddingTop" in node:
        styles["paddingTop"] = f"{node['paddingTop']}px"
    if "paddingBottom" in node:
        styles["paddingBottom"] = f"{node['paddingBottom']}px"
    
    # Extract opacity
    if "opacity" in node:
        styles["opacity"] = str(node["opacity"])
    
    # Extract shadows
    if "effects" in node:
        for effect in node["effects"]:
            if effect.get("type") == "DROP_SHADOW" and effect.get("visible", True):
                color = effect.get("color", {})
                r = int(color.get("r", 0) * 255)
                g = int(color.get("g", 0) * 255)
                b = int(color.get("b", 0) * 255)
                a = color.get("a", 1)
                offset = effect.get("offset", {})
                x = offset.get("x", 0)
                y = offset.get("y", 0)
                blur = effect.get("radius", 0)
                styles["boxShadow"] = f"{x}px {y}px {blur}px rgba({r}, {g}, {b}, {a})"
                break
    
    return styles

def recursive_find_node(node, node_id):
    """Find a node by its ID in the node tree"""
    if node.get("id") == node_id:
        return node
    
    if "children" in node:
        for child in node["children"]:
            found = recursive_find_node(child, node_id)
            if found:
                return found
    
    return None

def extract_children(node):
    """Extract children nodes and their styles"""
    children = []
    
    if "children" in node:
        for child in node["children"]:
            styles = parse_node_styles(child)
            content = ""
            
            # Check for text content
            if child.get("type") == "TEXT" and "characters" in child:
                content = child["characters"]
            
            children.append({
                "styles": styles,
                "content": content
            })
    
    return children

def generate_react_props(node):
    """Generate React props from node properties"""
    props = []
    
    # Add basic props
    if "name" in node:
        name_parts = node["name"].split('=')
        if len(name_parts) > 1:
            prop_name = name_parts[0].strip()
            default_value = name_parts[1].strip()
            if default_value.lower() in ["true", "false"]:
                props.append(f"{prop_name}={default_value}")
            else:
                props.append(f'{prop_name}="{default_value}"')
    
    return props

def figma_to_react(file_key, node_id):
    """Convert a Figma node to a React component"""
    try:
        # Get the node data
        node_data = get_figma_node(file_key, node_id)
        
        # Extract the node from the response
        node = None
        for key, item in node_data.get("nodes", {}).items():
            if "document" in item:
                node = item["document"]
                break
        
        if not node:
            # Try to find node in the document tree
            for key, item in node_data.get("nodes", {}).items():
                if "document" in item:
                    document = item["document"]
                    node = recursive_find_node(document, node_id.split(':')[-1])
                    if node:
                        break
        
        if not node:
            raise Exception("Node not found in response")
        
        # Parse node name to get component name
        component_name = node.get("name", "FigmaComponent").replace(" ", "")
        
        # Parse styles
        styles = parse_node_styles(node)
        styles_str = ",\n        ".join([f"{k}: '{v}'" for k, v in styles.items()])
        
        # Parse props
        props = generate_react_props(node)
        props_str = "\n  ".join(props)
        
        # Extract children
        children = extract_children(node)
        children_str = ""
        
        for child in children:
            child_styles_str = ",\n          ".join([f"{k}: '{v}'" for k, v in child["styles"].items()])
            content = child["content"]
            
            children_str += f"""
      <div style={{{{
          {child_styles_str}
        }}}}>
        {content}
      </div>"""
        
        # Generate React component
        react_code = f"""import React from 'react';

const {component_name} = (props) => {{
  return (
    <div 
      style={{{{
        {styles_str}
      }}}}
      {{...props}}
    >
      {children_str}
      {props_str}
    </div>
  );
}};

export default {component_name};
"""
        return react_code
    
    except Exception as e:
        raise Exception(f"Failed to convert Figma to React: {str(e)}")