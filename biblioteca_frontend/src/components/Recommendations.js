import React, { useState } from 'react';
import api from '../services/api';

const Recommendations = () => {
  const [userId, setUserId] = useState('');
  const [recommendations, setRecommendations] = useState([]);

  const fetchRecommendations = () => {
    api.get(`/recommendations?user_id=${userId}`)
      .then(response => {
        setRecommendations(response.data.recommendations || []);
      })
      .catch(error => {
        console.error('Erro ao pesquisar recomendações:', error);
      });
  };

  return (
    <div>
      <h1>Recomendações de Livros</h1>
      <input
        type="text"
        placeholder="ID do Utilizador"
        value={userId}
        onChange={e => setUserId(e.target.value)}
      />
      <button onClick={fetchRecommendations}>Pesquisar Recomendações</button>
      <ul>
        {recommendations.map((book, index) => (
          <li key={index}>{book.titulo}</li>
        ))}
      </ul>
    </div>
  );
};

export default Recommendations;
