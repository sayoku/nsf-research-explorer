import { useRef, useEffect } from 'react'
import ForceGraph2D from 'react-force-graph-2d'

const COLORS = {
  PI: "#9B59D0",
  "Co-PI": "#CC7A00",
  Institution: "#2BA39B",
  Award: "#3A6BC0",
  Topic: "#B84055",
}

function nodeDisplayLabel(node) {
  if (node.type === "Award") {
    const title = node.title || node.id.replace("Award_", "")
    return title.length > 28 ? title.slice(0, 26) + "…" : title
  }
  if (node.type === "Topic") {
    return node.id.replace("Topic_", "").replace(/_/g, " ")
  }
  return node.id // PI, Co-PI, and Institution already use real names as ids
}

// Escapes text so award titles/abstracts can't break the tooltip's HTML
function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
}

function buildAwardConnections(nodes, links) {
  // nodeId -> { pi: name|null, institution: name|null }
  const nodeById = Object.fromEntries(nodes.map((n) => [n.id, n]))
  const connections = {}

  for (const link of links) {
    const sourceId = typeof link.source === "object" ? link.source.id : link.source
    const targetId = typeof link.target === "object" ? link.target.id : link.target

    for (const [awardId, otherId] of [[sourceId, targetId], [targetId, sourceId]]) {
      const awardNode = nodeById[awardId]
      const otherNode = nodeById[otherId]
      if (!awardNode || awardNode.type !== "Award" || !otherNode) continue

      if (!connections[awardId]) connections[awardId] = { pi: null, institution: null }
      if (otherNode.type === "PI") connections[awardId].pi = otherId
      if (otherNode.type === "Institution") connections[awardId].institution = otherId
    }
  }
  return connections
}

function buildTooltip(node, awardConnections) {
  if (node.type === "Award") {
    const conn = awardConnections[node.id] || {}
    const abstract = node.abstract ? node.abstract.slice(0, 200) + (node.abstract.length > 200 ? "…" : "") : "N/A"
    const amount = node.amount ? `$${Number(node.amount).toLocaleString()}` : "N/A"

    return `
      <div style="max-width:320px; white-space:normal; line-height:1.4;">
        <strong>${escapeHtml(node.id)}</strong><br/>
        <strong>Title:</strong> ${escapeHtml(node.title || "N/A")}<br/>
        <strong>PI:</strong> ${escapeHtml(conn.pi || "N/A")}<br/>
        <strong>Institution:</strong> ${escapeHtml(conn.institution || "N/A")}<br/>
        <strong>Program:</strong> ${escapeHtml(node.program || "N/A")}<br/>
        <strong>Amount:</strong> ${escapeHtml(amount)}<br/>
        <strong>Start Date:</strong> ${escapeHtml(node.start_date || "N/A")}<br/>
        <strong>Abstract:</strong> ${escapeHtml(abstract)}
      </div>
    `
  }

  // PI, Co-PI, Institution, Topic: just the title/name
  return `<div>${escapeHtml(nodeDisplayLabel(node))} (${escapeHtml(node.type || "?")})</div>`
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

  const awardConnections = buildAwardConnections(formattedData.nodes, formattedData.links)

  // react-force-graph wants { nodes: [...], links: [...] }
  // nx.node_link_data gives { nodes: [...], links: [...] } already,
  // but each link uses "source"/"target" as node ids — that matches what the lib expects.
  return (
    <div style={{ position: "relative", width: "100%", height, overflow: "hidden", border: "1px solid #ddd" }}>
      <ForceGraph2D
        ref={fgRef}
        graphData={formattedData}
        height={height}
        nodeLabel={(node) => buildTooltip(node, awardConnections)}
        nodeColor={(node) => COLORS[node.type] || "#999"}
        nodeRelSize={5}
        linkColor={() => "rgba(0,0,0,0.25)"}
        linkWidth={1}
        cooldownTicks={100}
        onEngineStop={() => fgRef.current?.zoomToFit(400, 40)}
        nodeCanvasObject={(node, ctx, globalScale) => {
          const label = nodeDisplayLabel(node)
          const fontSize = 11 / globalScale
          const radius = (node.type === "Topic" ? 4 : 6)

          ctx.beginPath()
          ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI)
          ctx.fillStyle = COLORS[node.type] || "#999"
          ctx.fill()

          // Only draw text once zoomed in enough to avoid clutter
          if (globalScale > 1.5) {
            ctx.font = `${fontSize}px Sans-Serif`
            ctx.textAlign = "center"
            ctx.textBaseline = "top"
            ctx.fillStyle = "#222"
            ctx.fillText(label, node.x, node.y + radius + 2)
          }
        }}
      />
    </div>
  )
}

export default GraphCanvas