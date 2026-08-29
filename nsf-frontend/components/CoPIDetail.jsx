import ExpandableAward from "./ExpandableAward.jsx"

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
        <p>No awards found for this PI.</p>
      ) : (
        <>
          <p><strong>Total Awards:</strong> {awards.length}</p>
          {awards.map((award) => (
            <ExpandableAward key={award.id} awardId={award.id} label={award.title || award.id} />
          ))}
        </>
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