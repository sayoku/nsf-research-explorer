import ExpandableAward from "./ExpandableAward.jsx"

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
            <ExpandableAward key={award.id} awardId={award.id} label={award.title || award.id} />
          ))}
        </>
      )}
    </div>
  )
}

export default PIDetail