function CoPIDetail({ detail, loading }) {
  if (loading) return <p>Loading Co-PI details...</p>
  if (!detail) return null

  const { copi, awards, collaborators } = detail

  return (
    <div className="copi-detail">
      <h3>{copi}</h3>

      <div style={{ display: "flex", gap: "2rem", margin: "0.5rem 0" }}>
        <p><strong>Co-PI Awards:</strong> {awards?.length || 0}</p>
        <p><strong>Collaborators:</strong> {collaborators?.length || 0}</p>
      </div>

      {(!awards || awards.length === 0) ? (
        <p>No awards found for this Co-PI.</p>
      ) : (
        awards.map((award) => (
          <details key={award.id} style={{ marginBottom: "0.5rem", border: "1px solid #ddd", borderRadius: "6px", padding: "0.5rem" }}>
            <summary style={{ cursor: "pointer", fontWeight: 600 }}>
              {award.title || award.id}
            </summary>
            <p><strong>Program:</strong> {award.program || "N/A"}</p>
            <p><strong>Amount:</strong> {award.amount ? `$${Number(award.amount).toLocaleString()}` : "N/A"}</p>
            <p><strong>Start Date:</strong> {award.start_date || "N/A"}</p>
            <p><strong>Abstract:</strong> {award.abstract || "N/A"}</p>
          </details>
        ))
      )}

      {collaborators && collaborators.length > 0 && (
        <>
          <h4>Collaborators</h4>
          <p>{collaborators.join(", ")}</p>
        </>
      )}
    </div>
  )
}

export default CoPIDetail