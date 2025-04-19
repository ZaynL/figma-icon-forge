# Figma Icon Forge

<p align="center">
  <img src="docs/images/logo.png" alt="Figma Icon Forge Logo" width="200"/>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#demo">Live Demo</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#api">API</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

Figma Icon Forge is a powerful tool that bridges the gap between design and development, allowing you to seamlessly convert Figma components to React code and search, manage, and export SVG icons from multiple libraries.

![Figma Icon Forge Demo](docs/images/demo.gif)

## Features

### 🔍 Advanced Icon Search and Management
- Search through thousands of SVG icons from popular libraries
- Filter by style (fill, stroke, etc.)
- Preview icons with accurate rendering
- Multiple copy options: as image, SVG code, or name
- Download icons as SVG or PNG files
- Right-click context menu for quick actions

### 🔄 Figma to React Conversion
- Convert Figma components directly to clean React code
- Preserve styling, dimensions, and layout properties
- Extract props from component names
- Support for nested elements and text content
- Debug mode for troubleshooting Figma node structure

### 🧰 Developer-Friendly Features
- Clean, reusable React components
- Proper SVG implementation with namespaces
- Comprehensive error handling
- Cross-browser compatibility
- Simple, intuitive user interface

## Demo

 Try out the live demo: ⏳

## Installation

### Prerequisites
- Python 3.12 or higher
- Figma API key

### Quick Start

```bash
# Clone the repository
git clone https://github.com/zaynl/figma-icon-forge.git
cd figma-icon-forge

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create a .env file with your Figma API key:
echo "FIGMA_API_KEY=your_figma_api_key" > .env

# Run the server
python main.py
```

## Usage

### Icon Search

1. Enter a search term in the "Search for icons" field
2. Optionally specify a style filter (fill, stroke)
3. Click "Search Icons"
4. Use the results in various ways:
   - **Left-click** an icon to copy it as an image
   - **Right-click** to access more options:
     - Copy as Image
     - Copy SVG Code
     - Copy Icon Name
     - Download as PNG
     - Download as SVG

### Figma to React Conversion

1. Obtain your Figma file key from the URL (e.g., `DxhZmrwN3JCMC5KdvIy9Y9`)
2. Find the node ID of the component you want to convert
   - Use the "Debug Node" button if you're unsure of the correct ID
3. Click "Generate React Component"
4. Use the generated code in your React project

## API

The Figma Icon Forge exposes the following API endpoints:

### Icon Search
```
GET /search-icons?query={search_term}&style={optional_style}&limit={max_results}
```

### Figma to React
```
POST /figma-to-react
Content-Type: application/json

{
  "file_key": "your_figma_file_key",
  "node_id": "node_id_to_convert"
}
```

### Debug Figma Node
```
GET /debug-figma-node?file_key={figma_file_key}&node_id={node_id}
```

## Configuration Options

You can configure the application using the following environment variables:

```
# Server configuration
PORT=8000                  # Default: 8000
HOST=0.0.0.0               # Default: 0.0.0.0

# API configuration
FIGMA_API_KEY=your_key     # Required for Figma integration
ICONIFY_API_BASE=url       # Optional: Default is "https://api.iconify.design"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Iconify](https://iconify.design/) for their amazing icon API
- [Figma](https://www.figma.com/) for their design platform and API
- All contributors who have helped make this project better

