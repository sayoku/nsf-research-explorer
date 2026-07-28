export default function AwardsTable({ awards, onSelectAward }) {
  if (!awards || awards.length === 0) {
    return <p className="empty-state">No awards to display.</p>;
  }

  return (
    <table className="awards-table">
      <thead>
        <tr>
          <th>Award</th>
        </tr>
      </thead>
      <tbody>
        {awards.map((awardId) => (
          <tr key={awardId} onClick={() => onSelectAward?.(awardId)}>
            <td>{awardId}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}