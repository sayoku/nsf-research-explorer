export default function AwardsTable({ awards, onSelectAward }) {
  if (!awards || awards.length === 0) {
    return <p className="empty-state">No awards to display.</p>;
  }

  return (
    <table className="awards-table">
      <thead>
        <tr>
          <th>Award #</th>
          <th>Title</th>
          <th>PI</th>
          <th>Institution</th>
          <th>Amount</th>
        </tr>
      </thead>
      <tbody>
        {awards.map((award) => (
          <tr key={award.award_id} onClick={() => onSelectAward?.(award.award_id)}>
            <td>{award.award_id}</td>
            <td>{award.title}</td>
            <td>{award.pi_name}</td>
            <td>{award.institution}</td>
            <td>{award.amount ? `$${award.amount.toLocaleString()}` : "—"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}