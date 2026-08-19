function AwardDetail({ detail, loading }) {
  if (loading) return <p>Loading award...</p>
  if (!detail) return null

  const { award_id, award_data, pi_nodes, copi_nodes, link_to_award } = detail

  return (
    <div className="award-detail">
      <h3>{award_data.title || `Award ${award_id}`}</h3>
      <p><strong>Program:</strong> {award_data.program || "N/A"}</p>
      <p><strong>Amount:</strong> {award_data.amount ? `$${Number(award_data.amount).toLocaleString()}` : "N/A"}</p>
      <p><strong>Start Date:</strong> {award_data.start_date || "N/A"}</p>
      <p><strong>PI(s):</strong> {pi_nodes?.length ? pi_nodes.join(", ") : "N/A"}</p>
      <p><strong>Co-PI(s):</strong> {copi_nodes?.length ? copi_nodes.join(", ") : "N/A"}</p>
      <p><strong>Abstract:</strong> {award_data.abstract || "N/A"}</p>
      <a href={link_to_award} target="_blank" rel="noreferrer">View on NSF.gov →</a>
    </div>
  )
}

export default AwardDetail