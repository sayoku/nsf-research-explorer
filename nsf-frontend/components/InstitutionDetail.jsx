import ExpandableAward from './ExpandableAward.jsx'

function InstitutionDetail({ detail, loading }) {
  if (loading) return <p>Loading institution details...</p>
  if (!detail) return null

  const { institution, pi_awards } = detail
  const piNames = Object.keys(pi_awards || {})

  return (
    <div className="institution-detail">
      <h3>{institution}</h3>
      {piNames.length === 0 ? (
        <p>No PIs found for this institution.</p>
      ) : (
        <>
          <p><strong>Total PIs:</strong> {piNames.length}</p>
          {piNames.map((pi) => {
            const awardIds = pi_awards[pi] || []
            return (
              <details
                key={pi}
                style={{ marginBottom: "0.5rem", border: "1px solid #ccc", borderRadius: "6px", padding: "0.5rem" }}
              >
                <summary style={{ cursor: "pointer", fontWeight: 600 }}>
                  {pi}: {awardIds.length} award{awardIds.length !== 1 ? "s" : ""}
                </summary>
                {awardIds.length === 0 ? (
                  <p>No award details available</p>
                ) : (
                  <div style={{ marginTop: "0.5rem", paddingLeft: "1rem" }}>
                    {awardIds.map((awardId) => (
                      <ExpandableAward key={awardId} awardId={awardId} label={awardId} />
                    ))}
                  </div>
                )}
              </details>
            )
          })}
        </>
      )}
    </div>
  )
}

export default InstitutionDetail