import ForceGraph2D from 'react-force-graph-2d'

const COLORS = {
  PI: "#CF9FFF",
  "Co-PI": "#FFB347",
  Institution: "#4ECDC4",
  Award: "#6495ED",
  Topic: "#E37383",
}

function GraphCanvas({ graphData, height = 600 }) {
  if (!graphData || graphData.nodes.length === 0) {
    return <p>No graph data yet.</p>
  }

  // react-force-graph wants { nodes: [...], links: [...] }
  // nx.node_link_data gives { nodes: [...], links: [...] } already,
  // but each link uses "source"/"target" as node ids — that matches what the lib expects.
  return (
    <ForceGraph2D
      graphData={graphData}
      height={height}
      nodeLabel={(node) => `${node.id} (${node.type || "?"})`}
      nodeColor={(node) => COLORS[node.type] || "#999"}
      linkColor={() => "rgba(255,255,255,0.2)"}
      nodeRelSize={5}
    />
  )
}

export default GraphCanvas