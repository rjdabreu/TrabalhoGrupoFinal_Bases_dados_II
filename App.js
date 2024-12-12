import React from 'react';
import BookList from './components/BookList';
import BorrowBook from './components/BorrowBook';
import Recommendations from './components/Recommendations';

function App() {
    return (
        <div>
            <h1>Biblioteca Online</h1>
            <BookList />
            <BorrowBook />
            <Recommendations />
        </div>
    );
}

export default App;
