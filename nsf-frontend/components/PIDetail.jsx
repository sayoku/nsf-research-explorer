export default function PIDetail({ detail, loading }) {
  if (loading) return <p>Loading...</p>;
  if (!detail) return null;

  return (
    <div className="pi-detail">
      <h3>{detail.pi}</h3>
      {detail.awards.length === 0 ? (
        <p>No awards found for this PI.</p>
      ) : (
        <ul>
          {detail.awards.map((award) => (
            <li key={award.id}>{award.title || award.id}</li>
          ))}
        </ul>
      )}
    </div>
  );
}