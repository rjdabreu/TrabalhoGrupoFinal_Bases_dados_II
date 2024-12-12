import React, { useState } from 'react';
import api from '../services/api';

const BorrowBook = () => {
  const [userId, setUserId] = useState('');
  const [bookId, setBookId] = useState('');
  const [message, setMessage] = useState('');

  const handleBorrow = () => {
    api.post('/borrow', { user_id: parseInt(userId), book_id: parseInt(bookId) })
      .then(response => {
        setMessage(response.data.message);
      })
      .catch(error => {
        setMessage(error.response?.data?.error || 'Erro ao registrar empréstimo.');
      });
  };

  return (
    <div>
      <h1>Registrar Empréstimo</h1>
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
      <button onClick={handleBorrow}>Registrar</button>
      {message && <p>{message}</p>}
    </div>
  );
};

export default BorrowBook;
