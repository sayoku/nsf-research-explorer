import { useState } from 'react'

function SubgraphQuery({ onResult }) {
  const [query, setQuery] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await fetch("http://localhost:8000/api/graph/subgraph/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      })
      if (!res.ok) throw new Error(`Subquery failed (status ${res.status})`)
      const data = await res.json()
      onResult(data.graph, data.explanation)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. Show water research"
        />
        <button type="submit" disabled={loading}>
          {loading ? "Querying..." : "Query Graph"}
        </button>
      </form>
      {error && <p className="error">Error: {error}</p>}
    </div>
  )
}

export default SubgraphQuery