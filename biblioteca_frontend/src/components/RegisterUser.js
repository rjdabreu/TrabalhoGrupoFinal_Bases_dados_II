import React, { useState } from 'react';
import api from '../services/api';

const RegisterUser = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');

  const handleRegister = (e) => {
    e.preventDefault();
    api.post('/users', { name, email })
      .then(response => {
        setMessage('Utilizador registrado com sucesso!');
        setName('');
        setEmail('');
      })
      .catch(error => {
        console.error('Erro ao registrar utilizador:', error);
        setMessage('Erro ao registrar utilizador.');
      });
  };

  return (
    <div>
      <h1>Registrar Utilizador</h1>
      <form onSubmit={handleRegister}>
        <div>
          <label>Nome:</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <button type="submit">Registrar</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default RegisterUser;
