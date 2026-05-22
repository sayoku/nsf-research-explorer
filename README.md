# NSF Research Explorer Agent

An intelligent agentic system that explores National Science Foundation (NSF) award data using Large Language Models, Knowledge Graphs, and interactive visualization.

## Project Overview

This project builds a three-component system:
1.**LLM Agent** - Interprets natural language queries and orchestrates API calls
2.**Knowledge Graph** - Organizes relationships between PIs, institutions, and research topics
3.**Interactive Web Interface** - Visualizes and explores the research network

## Features

- Natural language query processing using Claude
- NSF Awards API integration for real-time data retrieval
- Knowledge graph construction with deduplication across PI's, institutions, and awards
- Named entity recognition (NER) for keyword extraction from award abstracts using spaCy
- Interactive graph visualization with hover tooltips, zoom, and pan
- Subgraph querying - asking natural language questions about the loaded graph and explore a filtered view
- Web-based interface built with Streamlit

## Technology Stack

- **Python 3.9+**
- **LLM Integration**: Anthropic claude-sonnet-4-5 using the anthropic Python SDK
- **Graph Processing**: NetworkX for graph construction, traversal, and analysis
- **NLP**: spaCy for named entity recognition and keyword extraction
- **Visualization**: Pyvis for interactive graph rendering (built on vis.js)
- **Web Framework**: Streamlit for web interface
- **API Requests**: requests library for NSF Awards API calls

## Project Structure

```text
nsf-research-explorer/
├── src/
│   ├── agent/
│   │  ├── tool.py # translated natural language to API params, calls the NSF API
│   │  ├── .env
│   │  └── __init__.py
│   ├── kgraph/
│   │  ├── mem.py # KGBuilder: builds and manages the NetworkX kgraph
│   │  ├── query.py # KGQueryAgent: natural language subgraph querying
│   │  └── __init__.py
│   └── app.py # Streamlit application
├── data/               
├── tests/                      
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- An Anthropic API Key

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
   python -m spacy download en_core_web_sm
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

```bash

Search for grants:

Water research in Tennessee — loads NSF awards related to water research in TN
Cognitive science at Ohio State University — finds awards at a specific institution
Machine learning research — broad topic search across all institutions

Subgraph queries (after loading a graph):

Show me all water-related awards — filters the graph to water topic nodes
What awards does [PI name] have? — focuses the graph on a specific researcher
Awards over $500,000 — filters by funding amount
Show research at [university name] — shows all PIs and awards at an institution
```

## Development Phases

### Phase 1: LLM Agent Foundation

This component is the Agent's reasoning core. It translates a human question (e.g., "Find all large grants in California for biology") into the specific parameters needed by the NSF API tool, executes the tool, and then summarizes the resulting data.

### Phase 2: Knowledge Graph

The KG acts as the Agent's long-term, structured Memory. It transforms flat award data into a connected network showing relationships between PIs, Institutions, and research topics.

### Phase 3: Visualization

A web application that renders the connected data as a clickable network diagram, allowing users to dynamically explore the knowledge contained within the Agent's memory (the KG).

## Limitations

- spaCy topic extraction can be noisy, common words and short fragments sometimes appear as topic
- Subgraph querying depends on Claude's correct parsing of the operation type, may return empty results
- Graph size - loading 100 awards can produce many nodes, which may slow down the Pyvis rendering
- No persistent storage (yet) - the graph resets on page refresh, all data is held in the Streamlit session state
- NSF API coverage - only searches funded awards, without access to unfunded proposals

## Future Enhancements

- [ ] Integrate GraphRAG for enhanced agent reasoning
- [ ] Migration to Neo4j for better scalability
- [ ] Time-series analysis with temporal filtering
- [ ] Multi-language support
- [ ] Export functionality (PDF reports, CSV data)
- [ ] Expand node click behavior to link to NSF award page

## License

This project is licensed under the MIT License

This project uses NetworkX, licensed under the BSD 3-Clause License

## Acknowledgments

- Project concept by Prof. Han-Wei Shen
- NSF Awards API
- Anthropic for LLM powered query parsing

## Contact

For questions or feedback, please open an issue or contact [huang.k.anna7@gmail.com]
