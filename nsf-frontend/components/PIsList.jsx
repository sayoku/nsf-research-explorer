export default function PIsList({pis, onSelectPI}) {
    // When there's no pi's return nothing
    if (!pis || pis.length === 0) {
        return <p className="empty-state">No PIs found. Try running a query</p>;
    }
    // else return pi list and button to select the pi
    return (
        <ul className="pis-list">
            {pis.map((pi) => ( 
                <li key={pi.name}> 
                    <button onClick = {() => onSelectPI?.(pi.name)}>
                        {pi.name}
                    </button>
                    {pi.role && <span className="pi-role">{pi.role}</span>}
                </li>
            ))}
        </ul>
    ); 
}