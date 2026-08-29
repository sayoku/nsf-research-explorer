import ExpandableAward from './ExpandableAward.jsx'

function AwardsTable({ awards }) {
  if (!awards || awards.length === 0) return <p>No awards loaded yet.</p>

  return (
    <div>
      {awards.map((award) => (
        <ExpandableAward key={award} awardId={award} label={award} />
      ))}
    </div>
  )
}

export default AwardsTable