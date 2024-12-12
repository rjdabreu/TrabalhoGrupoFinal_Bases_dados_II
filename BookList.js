#npx create-react-app biblioteca-frontend
#cd biblioteca-frontend
#npm install axios



import React, { useState, useEffect } from 'react';
import axios from 'axios';

function BookList() {
    const [books, setBooks] = useState([]);

    useEffect(() => {
        axios.get('http://localhost:5000/books')
            .then(response => setBooks(response.data))
            .catch(error => console.error("Erro ao buscar livros:", error));
    }, []);

    return (
        <div>
            <h2>Livros Disponíveis</h2>
            <ul>
                {books.map(book => (
                    <li key={book.id}>{book.titulo} - {book.autor}</li>
                ))}
            </ul>
        </div>
    );
}

export default BookList;

