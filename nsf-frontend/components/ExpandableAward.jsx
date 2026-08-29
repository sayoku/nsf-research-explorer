import { useState } from 'react'
import { api } from '../src/api.js'
import AwardDetail from './AwardDetail.jsx'

function ExpandableAward({ awardId, label }) {
  const [detail, setDetail] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [hasOpened, setHasOpened] = useState(false)

  const handleToggle = async (e) => {
    const isOpen = e.target.open
    if (isOpen && !hasOpened) {
      setHasOpened(true)
      setLoading(true)
      setError(null)
      try {
        const data = await api.getAward(awardId)
        setDetail(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
  }

  return (
    <details
      onToggle={handleToggle}
      style={{ marginBottom: "0.5rem", border: "1px solid #ddd", borderRadius: "6px", padding: "0.5rem" }}
    >
      <summary style={{ cursor: "pointer", fontWeight: 600 }}>{label}</summary>
      {error && <p className="error">Error: {error}</p>}
      {hasOpened && !error && <AwardDetail detail={detail} loading={loading} showTitle={false}/>}
    </details>
  )
}

export default ExpandableAward