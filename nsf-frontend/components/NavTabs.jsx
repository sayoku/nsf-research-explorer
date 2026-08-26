// nsf-frontend/src/components/NavTabs.jsx
function NavTabs({ active, onChange }) {
  const tabs = [
    { id: "search", label: "Search" },
    { id: "directory", label: "Directory" },
    { id: "graph", label: "Knowledge Graph" },
  ]

  return (
    <nav style={{ display: "flex", gap: "0.5rem", borderBottom: "2px solid #eee", marginBottom: "1.5rem" }}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          style={{
            padding: "0.6rem 1.2rem",
            border: "none",
            borderBottom: active === tab.id ? "3px solid #3A6BC0" : "3px solid transparent",
            background: "none",
            fontWeight: active === tab.id ? "600" : "400",
            cursor: "pointer",
            fontSize: "1rem",
          }}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  )
}

export default NavTabs