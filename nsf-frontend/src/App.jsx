import { useState, useEffect } from 'react'
import ReactMarkdown from "react-markdown"
import {api} from './api.js'
import PIsList from '../components/PIsList'
import InstitutionsList from '../components/InstitutionsList'
import AwardsTable from '../components/AwardsTable'
import PIDetail from '../components/PIDetail.jsx'
import InstitutionDetail from '../components/InstitutionDetail.jsx'
import AwardDetail from '../components/AwardDetail.jsx'
import GraphCanvas from '../components/GraphCanvas.jsx'
import SubgraphQuery from '../components/SubgraphQuery.jsx'

function App() {
  const [query, setQuery] = useState("")
  const [summary, setSummary] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [searchError, setSearchError] = useState(null)

  const [awards, setAwards] = useState([])
  const [pis, setPIs] = useState([])
  const [institutions, setInstitutions] = useState([])
  const [listsLoading, setListsLoading] = useState(false)  
  const [listsError, setListsError] = useState(null)

  const [selectedPI, setSelectedPI] = useState(null)
  const [piDetail, setPiDetail] = useState(null)
  const [piDetailLoading, setPiDetailLoading] = useState(false)
  const [piDetailError, setPiDetailError] = useState(null)

  const [selectedInst, setSelectedInst] = useState(null)
  const [institutionDetail, setInstitutionDetail] = useState(null)
  const [instDetailLoading, setInstDetailLoading] = useState(false)
  const [instDetailError, setInstDetailError] = useState(null)

  const [selectedAward, setSelectedAward] = useState(null)
  const [awardDetail, setAwardDetail] = useState(null)
  const [awardDetailLoading, setAwardDetailLoading] = useState(false)
  const [awardDetailError, setAwardDetailError] = useState(null)

  const [fullGraph, setFullGraph] = useState(null)
  const [activeGraph, setActiveGraph] = useState(null)
  const [graphExplanation, setGraphExplanation] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setSearchError(null)
    try {
      const data = await api.runQuery(query, 5)
      setSummary(data.summary)
      fetchAll() // refetch the lists to account for growing graph
    } catch (err) {
      setSearchError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchAll = async () => {
    setListsLoading(true)
    setListsError(null)
    try {
      const [awardsData, pisData, instData] = await Promise.all([
        api.getAwards(),
        api.getPIs(),
        api.getInstitutions(),
      ])
  
      setAwards(awardsData.awards)
      setPIs(pisData.pis) // pisData.copis also exists lol
      setInstitutions(instData.institutions)
    } catch (err) {
      setListsError(err.message)
    } finally {
      setListsLoading(false)
    }
  }

  const fetchFullGraph = async () => {
    const data = await api.getGraph()
    if (data.graph) {
      setFullGraph(data.graph)
      setActiveGraph(data.graph)
    }
  }

  useEffect(() => {
    fetchAll()
    fetchFullGraph()
  }, [])

  const handleSelectPI = async (piName) => {
    setSelectedPI(piName)
    setPiDetailLoading(true)
    setPiDetailError(null)
    try {
      const data = await api.getPI(piName)
      setPiDetail(data)
    } catch (err) {
      setPiDetailError(err.message)
    } finally {
      setPiDetailLoading(false)
    }
  }
  const handleSelectInstitution = async (instName) => {
    setSelectedInst(instName)
    setInstDetailLoading(true)
    setInstDetailError(null)
    try {
      const data = await api.getInstitution(instName)
      setInstitutionDetail(data)
    } catch (err) {
      setInstDetailError(err.message)
    } finally {
      setInstDetailLoading(false)
    }
  }

  const handleSelectAward = async (awardName) => {
  setSelectedAward(awardName)
  setAwardDetailLoading(true)
  setAwardDetailError(null)
  try {
    const data = await api.getAward(awardName)
    setAwardDetail(data)
  } catch (err) {
    setAwardDetailError(err.message)
  } finally {
    setAwardDetailLoading(false)
  }
}

const handleSubqueryResult = async (queryText) => {
  const data = await api.subquery(queryText)
  setActiveGraph(data.graph)
  setGraphExplanation(data.explanation)
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

      {searchError && <p className="error">Error: {searchError}</p>}
      {summary && <ReactMarkdown>{summary}</ReactMarkdown>}

      <hr />

      {listsLoading && <p>Loading PIs, institutions, and awards...</p>}
      {listsError && <p className="error">Error: {listsError}</p>}

      {!listsLoading && !listsError && (
        <>
          <PIsList pis={pis} onSelectPI={handleSelectPI} />
          {selectedPI && (
            piDetailError
              ? <p className="error">Error: {piDetailError}</p>
              : <PIDetail detail={piDetail} loading={piDetailLoading} />
          )}

          <InstitutionsList institutions={institutions} onSelectInstitution={handleSelectInstitution} />
          {selectedInst && (
            instDetailError
              ? <p className="error">Error: {instDetailError}</p>
              : <InstitutionDetail detail={institutionDetail} loading={instDetailLoading} />
          )}

          <AwardsTable awards={awards} onSelectAward={handleSelectAward} />
          {selectedAward && (
            awardDetailError
              ? <p className="error">Error: {awardDetailError}</p>
              : <AwardDetail detail={awardDetail} loading={awardDetailLoading} />
          )}
        </>
      )}

      <hr />
      <h2>Knowledge Graph</h2>
      <SubgraphQuery onResult={handleSubqueryResult} />
      {graphExplanation && <p><em>{graphExplanation}</em></p>}
      <button onClick={() => setActiveGraph(fullGraph)}>Reset to full graph</button>
      <GraphCanvas graphData={activeGraph} />

    </div>
  )
}

export default App
