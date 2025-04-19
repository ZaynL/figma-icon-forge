import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('figma_svg_mcp')

# Import our modules
from figma_tools import figma_to_react, get_figma_node
from figma_debug import debug_node_response, log_node_structure, find_node_by_id, improve_node_id
from iconify_tools import search_icons, get_icon_svg, get_icon_collections

# Create FastAPI app
app = FastAPI(title="Figma SVG MCP")

# Mount static files directory for the web UI
app.mount("/static", StaticFiles(directory="static"), name="static")

# Define data models
class FigmaRequest(BaseModel):
    file_key: str = Field(..., description="Figma file key")
    node_id: str = Field(..., description="Figma node ID")

class IconSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    style: Optional[str] = Field(None, description="Filter by style (fill, stroke)")
    limit: Optional[int] = Field(20, description="Maximum number of results")

class IconRequest(BaseModel):
    icon_name: str = Field(..., description="Full icon name (prefix:name)")

class MCPResponse(BaseModel):
    status: str
    data: Optional[Any] = None
    error: Optional[str] = None

# Root endpoint to serve the UI
@app.get("/", response_class=HTMLResponse)
async def root():
    return FileResponse("static/index.html")

# Debug endpoint for Figma node
@app.get("/debug-figma-node", response_model=MCPResponse)
async def debug_figma_node(file_key: str, node_id: str):
    try:
        # Get the node data
        node_data = get_figma_node(file_key, node_id)
        
        # Debug the response
        debug_info = debug_node_response(node_data)
        
        # For each found node, log its structure if it has a document
        for node_info in debug_info.get("found_nodes", []):
            if node_info.get("has_document", False):
                for key, item in node_data.get("nodes", {}).items():
                    if "document" in item and key == node_info["id"]:
                        logger.info(f"Logging structure for node {key}:")
                        log_node_structure(item["document"])
        
        return MCPResponse(status="success", data=debug_info)
    except Exception as e:
        logger.error(f"Error debugging Figma node: {str(e)}")
        return MCPResponse(status="error", error=str(e))
#create a route in your FastAPI application to serve test page
@app.get("/test-icons", response_class=HTMLResponse)
async def test_icons():
    """Test endpoint for icon display troubleshooting"""
    with open("static/test-icons.html", "r") as f:
        return f.read()

# Figma to React endpoint
@app.post("/figma-to-react", response_model=MCPResponse)
async def api_figma_to_react(request: FigmaRequest):
    try:
        logger.info(f"Converting Figma node to React: {request.file_key}, {request.node_id}")
        react_code = figma_to_react(request.file_key, request.node_id)
        return MCPResponse(status="success", data={"code": react_code})
    except Exception as e:
        logger.error(f"Error converting Figma to React: {str(e)}")
        return MCPResponse(status="error", error=str(e))

# Icon search endpoint
@app.post("/search-icons", response_model=MCPResponse)
async def api_search_icons(request: IconSearchRequest):
    try:
        logger.info(f"Searching icons: {request.query}, style={request.style}, limit={request.limit}")
        icons = search_icons(request.query, request.style, request.limit)
        return MCPResponse(status="success", data={"icons": icons})
    except Exception as e:
        logger.error(f"Error searching icons: {str(e)}")
        return MCPResponse(status="error", error=str(e))

# GET version for easier testing
@app.get("/search-icons", response_model=MCPResponse)
async def get_search_icons(query: str, style: Optional[str] = None, limit: Optional[int] = 20):
    try:
        logger.info(f"GET Searching icons: {query}, style={style}, limit={limit}")
        icons = search_icons(query, style, limit)
        return MCPResponse(status="success", data={"icons": icons})
    except Exception as e:
        logger.error(f"Error searching icons: {str(e)}")
        return MCPResponse(status="error", error=str(e))

# Get icon SVG endpoint
@app.get("/icon/{icon_name}", response_model=MCPResponse)
async def get_icon(icon_name: str):
    try:
        svg_data = get_icon_svg(icon_name)
        return MCPResponse(status="success", data={"svg": svg_data})
    except Exception as e:
        logger.error(f"Error getting icon: {str(e)}")
        return MCPResponse(status="error", error=str(e))

# Get icon collections endpoint
@app.get("/collections", response_model=MCPResponse)
async def get_collections():
    try:
        collections = get_icon_collections()
        return MCPResponse(status="success", data={"collections": collections})
    except Exception as e:
        logger.error(f"Error getting collections: {str(e)}")
        return MCPResponse(status="error", error=str(e))

# Error handler for more informative responses
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "error": str(exc)}
    )

# MCP-compatible endpoint
@app.post("/mcp")
async def mcp_endpoint(request: dict):
    try:
        function_name = request.get("function")
        params = request.get("params", {})
        
        logger.info(f"MCP function call: {function_name}")
        
        if function_name == "figma_to_react":
            figma_request = FigmaRequest(**params)
            result = await api_figma_to_react(figma_request)
            return {"result": result}
        
        elif function_name == "search_icons":
            icon_request = IconSearchRequest(**params)
            result = await api_search_icons(icon_request)
            return {"result": result}
        
        elif function_name == "get_icon":
            result = await get_icon(params.get("icon_name"))
            return {"result": result}
        
        elif function_name == "get_collections":
            result = await get_collections()
            return {"result": result}
        
        else:
            logger.warning(f"Unknown MCP function: {function_name}")
            return {"error": f"Unknown function: {function_name}"}
            
    except Exception as e:
        logger.error(f"Error in MCP endpoint: {str(e)}")
        return {"error": str(e)}

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)