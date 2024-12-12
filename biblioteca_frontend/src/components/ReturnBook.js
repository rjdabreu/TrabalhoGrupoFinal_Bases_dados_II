import React, { useState } from 'react';
import api from '../services/api';

const ReturnBook = () => {
  const [userId, setUserId] = useState('');
  const [bookId, setBookId] = useState('');
  const [message, setMessage] = useState('');

  const handleReturn = () => {
    api.put('/return', { user_id: parseInt(userId), book_id: parseInt(bookId) })
      .then(response => {
        setMessage(response.data.message);
      })
      .catch(error => {
        setMessage(error.response?.data?.error || 'Erro ao registrar devolução.');
      });
  };

  return (
    <div>
      <h1>Registrar Devolução</h1>
      <input
        type="text"
        placeholder="ID do Utilizador"
        value={userId}
        onChange={e => setUserId(e.target.value)}
      />
      <input
        type="text"
        placeholder="ID do Livro"
        value={bookId}
        onChange={e => setBookId(e.target.value)}
      />
      <button onClick={handleReturn}>Registrar</button>
      {message && <p>{message}</p>}
    </div>
  );
};

export default ReturnBook;
