export default function PIsList({pis, onSelectPI}) {
    // When there's no pi's return nothing
    if (!pis || pis.length === 0) {
        return <p className="empty-state">No PIs found. Try running a query</p>;
    }
    // else return pi list and button to select the pi
    return (
        <ul className="pis-list">
            {pis.map((piName) => ( 
                <li key={piName}> 
                    <button onClick = {() => onSelectPI?.(piName)}>
                        {piName}
                    </button>
                </li>
            ))}
        </ul>
    ); 
}