# NSF Research Explorer Agent

An intelligent agentic system that explores National Science Foundation (NSF) award data using Large Language Models, Knowledge Graphs, and interactive visualization.

## Project Overview

This project builds a three-component system:
1.**LLM Agent** - Interprets natural language queries and orchestrates API calls
2.**Knowledge Graph** - Organizes relationships between PIs, institutions, and research topics
3.**Interactive Web Interface** - Visualizes and explores the research network

## Features

- Natural language query processing using LLMs
- NSF Awards API integration for real-time data retrieval
- Knowledge graph construction
- Interactive graph visualization
- Web-based interface

## Technology Stack

- **Python 3.9+**
- **LLM Integration**:
- **Graph Processing**:
- **NLP**:
- **Visualization**:
- **Web Framework**:
- **API Requests**: requests library

## Project Structure

```text
nsf-research-explorer/
├── src/
│   ├── agent/
│   ├── knowledge_graph/
│   └── visualization/
├── data/               
├── tests/
├── app.py                         
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git

### Installation

1. **Clone the repository**

   ```bash

   git clone https://github.com/sayoku/nsf-research-explorer.git
   cd nsf-research-explorer
   ```

2. **Create a virtual environment**

   ```bash

   # Using venv
   python -m venv venv
   source venv/bin/activate  
   ```

3. **Install dependencies**

   ```bash

   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```bash

   cp .env.example .env
   # Edit .env and add your API keys
   ```

### Running the Application

```bash

streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Usage Examples

## Development Phases

### Phase 1: LLM Agent Foundation

### Phase 2: Knowledge Graph

### Phase 3: Visualization

## Success Metrics

## Limitations

## Future Enhancements

- [ ] Integrate GraphRAG for enhanced agent reasoning
- [ ] Migration to Neo4j for better scalability
- [ ] Time-series analysis with temporal filtering
- [ ] Multi-language support
- [ ] Export functionality (PDF reports, CSV data)

## License

This project is licensed under the MIT License

## Acknowledgments

- Project concept by Prof. Han-Wei Shen
- NSF Awards API

## Contact

For questions or feedback, please open an issue or contact [huang.k.anna7@gmail.com]
