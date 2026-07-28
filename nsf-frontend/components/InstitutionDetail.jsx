export default function InstitutionDetail({ detail, loading }) {
  if (loading) return <p>Loading...</p>;
  if (!detail) return null;

  const piNames = Object.keys(detail.pi_awards || {});

  return (
    <div className="institution-detail">
      <h3>{detail.institution}</h3>
      {piNames.length === 0 ? (
        <p>No PIs found for this institution.</p>
      ) : (
        piNames.map((piName) => (
          <div key={piName}>
            <strong>{piName}</strong>
            <ul>
              {detail.pi_awards[piName].map((award) => (
                <li key={award.id}>{award.title || award.id}</li>
              ))}
            </ul>
          </div>
        ))
      )}
    </div>
  );
}