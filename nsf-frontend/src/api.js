const BASE_URL = "http://localhost:8000"

// Handle fetches to clean up App.jsx
async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`Request failed: ${path} (status ${res.status})`)
  }
  return res.json()
}

export const api = {
  runQuery: (query, max_awards = 5) =>
    request("/api/query/", {
      method: "POST",
      body: JSON.stringify({ query, max_awards }),
    }),

  getAwards: () => request("/api/awards/"),
  getPIs: () => request("/api/pis/"),
  getCoPI: (copiName) => request(`/api/copis/${encodeURIComponent(copiName)}/`),
  getInstitutions: () => request("/api/institutions/"),

  getPI: (piName) => request(`/api/pis/${encodeURIComponent(piName)}/`),
  getInstitution: (instName) => request(`/api/institutions/${encodeURIComponent(instName)}/`),
  getAward: (awardName) => request(`/api/awards/${encodeURIComponent(awardName)}`),

  getGraph: () => request("/api/graph/"),
  subquery: (query) =>
    request("/api/graph/subgraph/", {
      method: "POST",
      body: JSON.stringify({ query }),
    }),
}