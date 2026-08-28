// Sub tabs for directory navigation! Tabs on tabs on tabs. 

function SubTabs({ active, onChange, counts }) {
  const tabs = [ // Adding count to show
    { id: "awards", label: `Awards (${counts.awards})` },
    { id: "pis", label: `PIs (${counts.pis})` },
    { id: "copis", label: `Co-PIs (${counts.copis})` },
    { id: "institutions", label: `Institutions (${counts.institutions})` },
  ]

  return (
    <nav style={{ display: "flex", gap: "0.5rem", borderBottom: "2px solid #eee", marginBottom: "1.5rem" }}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          style={{
            padding: "0.4rem 0.9rem",
            border: "none",
            borderBottom: active === tab.id ? "3px solid #3A6BC0" : "1px solid #ccc",
            background: active === tab.id ? "#EAF0FB" : "#fff",
            fontWeight: active === tab.id ? "600" : "400",
            cursor: "pointer",
            fontSize: "0.9rem",
          }}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  )
}

export default SubTabs