import { useState } from 'react'
import ReactMarkdown from "react-markdown"

function App() {
  const [query, setQuery] = useState("")
  const [summary, setSummary] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    // next line hits the fastapi endpoint
    const response = await fetch("http://localhost:8000/api/query/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query, max_awards: 5 })
    })
    const data = await response.json()

    setSummary(data.summary)
    setIsLoading(false)
  }

  return (
    <div>
      <h1>NSF Research Award Explorer</h1>
      <p>Explore NSF grants using natural language queries</p>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. Water research in Tennessee"
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Searching..." : "Search"}
        </button>
      </form>

      {summary && <ReactMarkdown>{summary}</ReactMarkdown>}
    </div>
  )
}

export default App


