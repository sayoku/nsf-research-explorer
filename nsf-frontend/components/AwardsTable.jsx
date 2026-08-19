function AwardsTable({ awards, onSelectAward }) {
  if (!awards || awards.length === 0) return <p>No awards loaded yet.</p>

  return (
    <table>
      <thead>
        <tr><th>Award ID</th></tr>
      </thead>
      <tbody>
        {awards.map((award) => (
          <tr key={award}>
            <td>
              <button type="button" onClick={() => onSelectAward(award)}>
                {award}
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default AwardsTable