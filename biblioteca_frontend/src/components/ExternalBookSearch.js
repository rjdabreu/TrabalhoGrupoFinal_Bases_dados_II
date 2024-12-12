import React, { useState } from 'react';
import api from '../services/api'; 

const ExternalBookSearch = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [books, setBooks] = useState([]);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!searchQuery) {
      setError('Digite um termo para pesquisar.');
      return;
    }

    try {
      const response = await api.get(`/external-books?query=${searchQuery}`);
      setBooks(response.data);
      setError(null);
    } catch (err) {
      setError('Erro ao pesquisar livros externos. Tente novamente.');
    }
  };

  return (
    <div>
      <h1>Pesquisar Livros Externos</h1>
      <input
        type="text"
        placeholder="Digite o título ou autor"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />
      <button onClick={handleSearch}>Pesquisar</button>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      <ul>
        {books.map((book, index) => (
          <li key={index}>
            <strong>{book.title}</strong> - {book.author || 'Autor desconhecido'}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ExternalBookSearch;
