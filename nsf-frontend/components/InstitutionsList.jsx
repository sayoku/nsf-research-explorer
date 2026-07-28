export default function InstitutionsList({institutions, onSelectInstitution}) {
    // When there's no pi's return nothing
    if (!institutions || institutions.length === 0) {
        return <p className="empty-state">No Institutions found. Try running a query</p>;
    }
    // else return pi list and button to select the pi
    return (
        <ul className="institutions-list">
            {institutions.map((instName) => ( 
                <li key={instName}> 
                    <button onClick = {() => onSelectInstitution?.(instName)}>
                        {instName}
                    </button>
                </li>
            ))}
        </ul>
    ); 
}