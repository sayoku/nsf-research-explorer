// const/let 
const maxAwards = 5
let query = "water research in Tennessee"

// template literals 
console.log(`Searching for: ${query}, max awards: ${maxAwards}`)

// arrow function
const buildRequest = (query, maxAward) => ({
    method: "POST",
    headers: { "Content-Type": "application/json"},
    body: JSON.stringify({query: query, max_awards: maxAwards})
})

// fetch + async/wait
const runQuery = async () => {
    console.log("Fetching...")

    const response = await fetch("http://localhost:8000/api/query/", buildRequest(query, maxAwards))

    console.log("Summary:", data.summary)
    console.log("Stats:", data.stats)

    // .map() - iterate over something in the response
    // run /api/pis/
    // const piNames = data.pis.map(pi => pi.toUpperCase())
    // console.log(piNames)
}

runQuery()
