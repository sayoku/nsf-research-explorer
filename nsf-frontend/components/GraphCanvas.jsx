import { useRef, useEffect } from 'react'
import ForceGraph2D from 'react-force-graph-2d'

const COLORS = {
  PI: "#9B59D0",
  "Co-PI": "#CC7A00",
  Institution: "#2BA39B",
  Award: "#3A6BC0",
  Topic: "#B84055",
}

function GraphCanvas({ graphData, height = 600 }) {
  const fgRef = useRef()
  // console.log("graphData:", graphData)

  useEffect(() => {
    if (fgRef.current && graphData) {
      setTimeout(() => fgRef.current.zoomToFit(400, 40), 500)
    }
  }, [graphData])

  if (!graphData || graphData.nodes.length === 0) {
    return <p>No graph data yet.</p>
  }

  const formattedData = {
    nodes: graphData.nodes,
    links: graphData.edges,
  }

  // react-force-graph wants { nodes: [...], links: [...] }
  // nx.node_link_data gives { nodes: [...], links: [...] } already,
  // but each link uses "source"/"target" as node ids — that matches what the lib expects.
  return (
    <div style={{ position: "relative", width: "100%", height, overflow: "hidden", border: "1px solid #ddd" }}>
      <ForceGraph2D
        ref={fgRef}
        graphData={formattedData}
        height={height}
        nodeLabel={(node) => `${node.id} (${node.type || "?"})`}
        nodeColor={(node) => COLORS[node.type] || "#999"}
        nodeRelSize={5}
        linkColor={() => "rgba(0,0,0,0.25)"}
        linkWidth={1}
        cooldownTicks={100}
        onEngineStop={() => fgRef.current?.zoomToFit(400, 40)}
      />
    </div>
  )
}

export default GraphCanvas