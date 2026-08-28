function PIDetail({ detail, loading }) {
  if (loading) return <p>Loading PI details...</p>
  if (!detail) return null

  const { pi, awards } = detail

  return (
    <div className="pi-detail">
      <h3>{pi}</h3>

      {(!awards || awards.length === 0) ? (
        <p>No awards found for this PI.</p>
      ) : (
        <>
          <p><strong>Total Awards:</strong> {awards.length}</p>
          {awards.map((award) => (
            <details key={award.id} style={{ marginBottom: "0.5rem", border: "1px solid #ddd", borderRadius: "6px", padding: "0.5rem" }}>
              <summary style={{ cursor: "pointer", fontWeight: 600 }}>
                {award.title || award.id}
              </summary>
              <p><strong>Program:</strong> {award.program || "N/A"}</p>
              <p><strong>Amount:</strong> {award.amount ? `$${Number(award.amount).toLocaleString()}` : "N/A"}</p>
              <p><strong>Start Date:</strong> {award.start_date || "N/A"}</p>
              <p><strong>Abstract:</strong> {award.abstract || "N/A"}</p>
            </details>
          ))}
        </>
      )}
    </div>
  )
}

export default PIDetail