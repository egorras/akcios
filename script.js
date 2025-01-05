async function loadData() {
    try {
        const response = await fetch('data/index.json');
        const data = await response.json();
        
        const contentDiv = document.getElementById('content');
        contentDiv.innerHTML = `
            <pre>${JSON.stringify(data, null, 2)}</pre>
        `;
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('content').innerHTML = 'Error loading data';
    }
}

loadData(); 