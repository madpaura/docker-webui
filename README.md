# Docker Web UI

A web interface for building Docker images from Dockerfiles stored in Git repositories and publishing them to a local registry server.

## Features

- Clone Git repositories containing Dockerfiles
- Edit Dockerfiles through the web interface with syntax highlighting
- Build Docker images from Dockerfiles with automatic build argument detection
- View build logs with syntax highlighting
- Publish successfully built images to a local registry
- Commit changes to Dockerfiles with custom commit messages
- Push Docker images to registry with proper tags
- Compatible with various Docker installations including snap

## Installation

### Method 1: Local Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd docker-webui
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration:
```bash
cp .env.example .env
```
Edit the `.env` file to set your registry server URL and other configuration options.

4. Ensure Docker is installed and running on your system.

5. Start the application:
```bash
streamlit run app.py
```

### Method 2: Using Docker Compose (Recommended)

1. Clone this repository:
```bash
git clone <repository-url>
cd docker-webui
```

2. Use the setup script to start the application and registry server:
```bash
./setup_registry.sh
```

Or manually start with Docker Compose:
```bash
docker-compose up -d
```

This will start both the Docker Registry server and the Docker Web UI application.

3. Access the application at http://localhost:8501

## Usage

1. Open your browser and navigate to the URL (usually http://localhost:8501)

2. Follow the instructions in the web interface to:
   - Clone a Git repository
   - Edit the Dockerfile
   - Build the Docker image
   - Publish the image to your registry

## Docker Registry

The Docker Compose setup includes a Docker Registry server running at http://localhost:5000. 
All images will be published to this registry by default. The registry data is persisted in the `/tmp/docker-registry` directory.

### Managing the Registry

- To start the registry and web UI: `./setup_registry.sh`
- To stop the registry and clean up: `./stop_registry.sh`
- To test the registry functionality: `./test_registry.sh`
- To view registry contents: `curl http://localhost:5000/v2/_catalog`
- To view image tags: `curl http://localhost:5000/v2/<repository>/tags/list`

## Project Structure

- `app.py`: Main Streamlit application
- `docker-compose.yml`: Docker Compose configuration for running the application and registry
- `Dockerfile`: Dockerfile for building the Docker Web UI application
- `setup_registry.sh`: Script to set up and start the Docker Registry and Web UI
- `stop_registry.sh`: Script to stop the Docker Registry and clean up data
- `test_registry.sh`: Script to test the Docker Registry functionality
- `config.py`: Configuration management
- `modules/`: Core functionality modules
  - `git_handler.py`: Git operations (clone, commit, push)
  - `docker_handler.py`: Docker operations (build, tag, push)
  - `registry_handler.py`: Docker registry operations
  - `file_handler.py`: File operations (read/write Dockerfiles)
- `utils/`: Utility functions
  - `validators.py`: Input validation
  - `formatters.py`: Output formatting
