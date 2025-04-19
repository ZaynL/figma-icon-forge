import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('figma_tools')

def debug_node_response(node_data):
    """
    Debug Figma node API response structure
    
    Args:
        node_data: Response from Figma API
        
    Returns:
        Dictionary with debug information
    """
    debug_info = {
        "found_nodes": [],
        "response_structure": {}
    }
    
    try:
        # Check if we have nodes in the response
        if "nodes" in node_data:
            debug_info["response_structure"]["has_nodes"] = True
            debug_info["response_structure"]["node_count"] = len(node_data["nodes"])
            
            # Check each node
            for node_id, node_content in node_data["nodes"].items():
                node_info = {
                    "id": node_id,
                    "has_document": "document" in node_content,
                    "node_type": node_content.get("document", {}).get("type", "Unknown")
                }
                
                debug_info["found_nodes"].append(node_info)
                
                # If document exists, try to find children
                if "document" in node_content:
                    document = node_content["document"]
                    if "children" in document:
                        node_info["has_children"] = True
                        node_info["children_count"] = len(document["children"])
                        
                        # Get first level children types
                        node_info["children_types"] = [
                            child.get("type", "Unknown") for child in document["children"][:5]
                        ]
                    else:
                        node_info["has_children"] = False
        else:
            debug_info["response_structure"]["has_nodes"] = False
        
        return debug_info
    
    except Exception as e:
        logger.error(f"Error debugging node response: {str(e)}")
        return {"error": str(e)}

def find_node_by_id(document, target_id):
    """
    Recursively search for a node by ID
    
    Args:
        document: Document or node object to search in
        target_id: ID to find
        
    Returns:
        Found node or None
    """
    # Check if this is the node we're looking for
    if document.get("id") == target_id:
        return document
    
    # Check children if they exist
    if "children" in document:
        for child in document["children"]:
            result = find_node_by_id(child, target_id)
            if result:
                return result
    
    return None

def log_node_structure(node, indent=0):
    """
    Log the structure of a node for debugging
    
    Args:
        node: Node to log
        indent: Indentation level
    """
    if not node:
        logger.info("Node is None")
        return
    
    prefix = "  " * indent
    node_type = node.get("type", "Unknown")
    node_id = node.get("id", "No ID")
    node_name = node.get("name", "Unnamed")
    
    logger.info(f"{prefix}- {node_type}: {node_name} (ID: {node_id})")
    
    if "children" in node:
        for child in node["children"]:
            log_node_structure(child, indent + 1)

def improve_node_id(node_id):
    """
    Improve node ID format for better compatibility
    
    Sometimes node IDs need a specific format (e.g., 0:1 vs 1)
    
    Args:
        node_id: Original node ID
        
    Returns:
        Improved node ID format
    """
    # Check if it's already in the format X:Y
    if ":" in node_id:
        return node_id
    
    # Try the common format 0:{id}
    return f"0:{node_id}"