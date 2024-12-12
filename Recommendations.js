import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Recommendations() {
    const [recommendations, setRecommendations] = useState([]);

    useEffect(() => {
        axios.get('http://localhost:5000/recommendations', { params: { user_id: 1 } })
            .then(response => setRecommendations(response.data))
            .catch(error => console.error("Erro ao buscar recomendações:", error));
    }, []);

    return (
        <div>
            <h2>Recomendações de Livros</h2>
            <ul>
                {recommendations.map((rec, index) => (
                    <li key={index}>{rec}</li>
                ))}
            </ul>
        </div>
    );
}

export default Recommendations;
