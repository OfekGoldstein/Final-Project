document.addEventListener('DOMContentLoaded', () => {
    const solarSystem = document.getElementById('solar-system');
    const info = document.getElementById('info');
    const planetSelect = document.getElementById('planet-select');
    const voteButton = document.getElementById('vote-button');

    // Fetch planet data from the server
    fetch('/planets')
        .then(response => response.json())
        .then(planets => {
            planets.forEach(planet => {
                // Create planet element
                const planetDiv = document.createElement('div');
                planetDiv.className = 'planet';
                planetDiv.innerHTML = `<img src="path/to/${planet.name.toLowerCase()}.png" alt="${planet.name}">`;
                planetDiv.addEventListener('mouseover', () => {
                    info.innerText = `${planet.name}: ${planet.description}`;
                });
                planetDiv.addEventListener('mouseout', () => {
                    info.innerText = 'Hover over a planet to see its information.';
                });
                solarSystem.appendChild(planetDiv);

                // Create planet option for voting
                const option = document.createElement('option');
                option.value = planet.name;
                option.innerText = planet.name;
                planetSelect.appendChild(option);
            });
        });

    // Function to toggle voting section visibility
    window.toggleVote = () => {
        planetSelect.style.display = planetSelect.style.display === 'none' ? 'inline' : 'none';
        voteButton.style.display = voteButton.style.display === 'none' ? 'inline' : 'none';
    };

    // Function to vote for a planet
    window.vote = () => {
        const planetName = planetSelect.value;
        fetch(`/vote/${planetName}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        });
    };
});