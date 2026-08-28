function CoPIList({ copis, onSelectCoPI }) {
  if (!copis || copis.length === 0) return <p>No co-PIs loaded yet.</p>

  return (
    <ul>
      {copis.map((copi) => (
        <li key={copi}>
          <button type="button" onClick={() => onSelectCoPI(copi)}>
            {copi}
          </button>
        </li>
      ))}
    </ul>
  )
}

export default CoPIList