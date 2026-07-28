import { useState, useEffect } from 'react'
import ReactMarkdown from "react-markdown"
import PIsList from '../components/PIsList'
import InstitutionsList from '../components/InstitutionsList'
import AwardsTable from '../components/AwardsTable'

function App() {
  const [query, setQuery] = useState("")
  const [summary, setSummary] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [awards, setAwards] = useState([])
  const [pis, setPIs] = useState([])
  const [institutions, setInstitutions] = useState([])
  const [error, setError] = useState(null)


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

    fetchAll() // refetch the lists to account for growing graph
  }

  const fetchAll = async () => {
    setError(null)
    try {
      const [awardsRes, pisRes, instRes] = await Promise.all([
        fetch("http://localhost:8000/api/awards/"),
        fetch("http://localhost:8000/api/pis/"),
        fetch("http://localhost:8000/api/institutions/"),
      ])
      if (!awardsRes.ok || !pisRes.ok || !instRes.ok) {
        throw new Error("One or more requests failed")
      }
      setAwards(await awardsRes.json())
      setPIs(await pisRes.json())
      setInstitutions(await instRes.json())
    } catch (err) {
      setError(err.message)
    }
  }
  useEffect(() => { 
    fetchAll()
  }, [])

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
      {error && <p className="error">Error: {error}</p>}

      <PIsList pis={pis} />
      <InstitutionsList institutions={institutions} />
      <AwardsTable awards={awards} />
    </div>
  )

} 

export default App


