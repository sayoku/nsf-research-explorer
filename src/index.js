// arrow function
const buildRequest = (query, maxAwards) => ({
    method: "POST",
    headers: { "Content-Type": "application/json"},
    body: JSON.stringify({query: query, max_awards: maxAwards})
})

// fetch + async/wait
const runQuery = async (query) => {
    console.log("Fetching...")

    const response = await fetch("http://localhost:8000/api/query/", buildRequest(query, 5))
    const data = await response.json()

    console.log("Summary:", data.summary)
    console.log("Stats:", data.stats)

    document.getElementById("summary").textContext = data.summary

    // .map() - iterate over something in the response
    // run /api/pis/
    // const piNames = data.pis.map(pi => pi.toUpperCase())
    // console.log(piNames)
}

// Grab form and listen for submit
const form = document.getElemendById("search-form")
form.addEventListener("sumbit", (event) => {
    event.preventDefault() 
    const query = document.getElementById("query").value
    runQuery()
})
