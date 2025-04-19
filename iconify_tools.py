import requests
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('iconify_tools')

# Iconify API configuration
ICONIFY_API_BASE = "https://api.iconify.design"

def get_icon_svg_data(icon_name):
    """
    Get raw SVG data for an icon
    
    Args:
        icon_name: Full icon name (prefix:name)
    
    Returns:
        SVG data including body, width, height
    """
    try:
        # First, try to get the JSON data
        json_url = f"{ICONIFY_API_BASE}/icon/{icon_name}?format=json"
        json_response = requests.get(json_url)
        
        if json_response.status_code == 200:
            return json_response.json()
            
        # If JSON fails, try direct SVG
        svg_url = f"{ICONIFY_API_BASE}/{icon_name}.svg"
        svg_response = requests.get(svg_url)
        
        if svg_response.status_code == 200:
            # We got raw SVG, extract the content
            svg_content = svg_response.text
            # Create a basic structure similar to the JSON response
            return {
                "body": svg_content,
                "width": 24,  # Default values
                "height": 24
            }
            
        # If both fail, try the proxy endpoint
        proxy_url = f"https://icon.iconly.io/{icon_name}.svg"
        proxy_response = requests.get(proxy_url)
        
        if proxy_response.status_code == 200:
            svg_content = proxy_response.text
            return {
                "body": svg_content,
                "width": 24,
                "height": 24
            }
            
        logger.warning(f"Failed to get SVG for {icon_name}, status: {json_response.status_code}")
        return {"body": "", "width": 24, "height": 24}
        
    except Exception as e:
        logger.error(f"Error getting SVG for {icon_name}: {str(e)}")
        return {"body": "", "width": 24, "height": 24}

def search_icons(query, style=None, limit=20):
    """
    Search for icons using the Iconify API
    
    Args:
        query: Search query
        style: Optional filter for style (fill, stroke)
        limit: Maximum number of results to return
    
    Returns:
        List of icons matching the search
    """
    try:
        # Build search query with style parameter if provided
        search_query = query
        if style and style.lower() in ["fill", "stroke"]:
            search_query = f"{query} style={style}"
        
        logger.info(f"Searching for icons with query: {search_query}, limit: {limit}")
        
        # Make API request
        url = f"{ICONIFY_API_BASE}/search?query={search_query}&limit={limit}"
        response = requests.get(url)
        
        if response.status_code != 200:
            logger.error(f"Failed to search icons: {response.text}")
            raise Exception(f"Failed to search icons: {response.text}")
        
        data = response.json()
        logger.info(f"Search returned {len(data.get('icons', []))} icons")
        icons = data.get("icons", [])
        
        # Format results
        results = []
        for icon_name in icons:
            # Icon names are in format "prefix:name"
            parts = icon_name.split(":")
            if len(parts) == 2:
                prefix, name = parts
                
                # Get direct SVG data
                logger.info(f"Fetching SVG data for icon: {icon_name}")
                svg_data = get_icon_svg_data(icon_name)
                
                # Log what we got
                logger.info(f"SVG data for {icon_name}: width={svg_data.get('width')}, height={svg_data.get('height')}, body length={len(svg_data.get('body', ''))}")
                
                results.append({
                    "prefix": prefix,
                    "name": name,
                    "full_name": icon_name,
                    "svg_url": f"{ICONIFY_API_BASE}/{icon_name}.svg",
                    "svg_body": svg_data.get("body", ""),
                    "width": svg_data.get("width", 24),
                    "height": svg_data.get("height", 24)
                })
                
                # Limit to prevent too many requests
                if len(results) >= 10:
                    break
        
        logger.info(f"Returning {len(results)} processed icons")
        return results
    
    except Exception as e:
        logger.error(f"Failed to search icons: {str(e)}")
        raise Exception(f"Failed to search icons: {str(e)}")

def get_icon_svg(icon_name):
    """
    Get SVG data for an icon
    
    Args:
        icon_name: Full icon name (prefix:name)
    
    Returns:
        SVG data for the icon
    """
    try:
        logger.info(f"Getting SVG data for icon: {icon_name}")
        return get_icon_svg_data(icon_name)
    
    except Exception as e:
        logger.error(f"Failed to get icon SVG: {str(e)}")
        raise Exception(f"Failed to get icon SVG: {str(e)}")

def get_icon_collections():
    """
    Get list of available icon collections
    
    Returns:
        List of icon collections
    """
    try:
        logger.info("Getting icon collections")
        url = f"{ICONIFY_API_BASE}/collections"
        response = requests.get(url)
        
        if response.status_code != 200:
            logger.error(f"Failed to get collections: {response.text}")
            raise Exception(f"Failed to get collections: {response.text}")
        
        collections = response.json()
        logger.info(f"Retrieved {len(collections)} icon collections")
        return collections
    
    except Exception as e:
        logger.error(f"Failed to get icon collections: {str(e)}")
        raise Exception(f"Failed to get icon collections: {str(e)}")