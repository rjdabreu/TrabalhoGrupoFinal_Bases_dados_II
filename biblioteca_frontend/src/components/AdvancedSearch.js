import React, { useState } from 'react';
import api from '../services/api';

const AdvancedSearch = () => {
    const [search, setSearch] = useState('');
    const [sortBy, setSortBy] = useState('titulo');
    const [books, setBooks] = useState([]);
    const [error, setError] = useState('');

    const fetchBooks = async () => {
        try {
            const response = await api.get('/books', {
                params: { search, sort_by: sortBy }
            });
            setBooks(response.data);
            setError('');
        } catch (err) {
            setError('Erro ao buscar livros.');
        }
    };

    return (
        <div>
            <h1>Busca Avançada</h1>
            <input
                type="text"
                placeholder="Digite título ou autor"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
            />
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                <option value="titulo">Título</option>
                <option value="autor">Autor</option>
            </select>
            <button onClick={fetchBooks}>Buscar</button>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <table>
                <thead>
                    <tr>
                        <th>Título</th>
                        <th>Autor</th>
                    </tr>
                </thead>
                <tbody>
                    {books.map((book) => (
                        <tr key={book.id}>
                            <td>{book.titulo}</td>
                            <td>{book.autor}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default AdvancedSearch;
