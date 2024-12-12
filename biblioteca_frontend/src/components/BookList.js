import React, { useState, useEffect } from 'react';
import api from '../services/api'; // SCaso tenha configurado um serviço de API

const BookList = () => {
  const [books, setBooks] = useState([]); // Estado para guardar os livros
  const [error, setError] = useState(null); // Estado para erros

  useEffect(() => {
    const fetchBooks = async () => {
      try {
        const response = await api.get('/books'); // Chamada à API
        setBooks(response.data); // Define os livros no estado
      } catch (error) {
        console.error('Erro ao pesquisar livros:', error);
        setError('Erro ao pesquisar a lista de livros. Tente novamente mais tarde.');
      }
    };

    fetchBooks(); // Executa a função de pesquisa
  }, []);

  return (
    <div>
      <h1>Lista de Livros</h1>
      {/* Mostra mensagem de erro se ocorrer */}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {/* Renderiza a lista de livros */}
      <ul>
        {books.length > 0 ? (
          books.map(book => (
            <li key={book.id}>
              <strong>ID:</strong> {book.id} - <strong>Título:</strong> {book.titulo} - <strong>Autor:</strong> {book.autor}
            </li>
          ))
        ) : (
          !error && <p>Nenhum livro disponível.</p>
        )}
      </ul>
    </div>
  );
};

export default BookList;
