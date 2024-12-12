import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import BookList from './components/BookList';
import BorrowBook from './components/BorrowBook';
import ReturnBook from './components/ReturnBook';
import Recommendations from './components/Recommendations';
import RegisterUser from './components/RegisterUser';
import ExternalBookSearch from './components/ExternalBookSearch';
import UserHistory from './components/UserHistory';
import AdvancedSearch from './components/AdvancedSearch';

const App = () => {
  return (
    <div>
      {/* Barra de navegação */}
      <nav>
        <ul>
          <li><Link to="/">Lista de Livros</Link></li>
          <li><Link to="/borrow">Registrar Empréstimo</Link></li>
          <li><Link to="/return">Registrar Devolução</Link></li>
          <li><Link to="/recommendations">Recomendações</Link></li>
          <li><Link to="/register">Registrar Utilizador</Link></li>
          <li><Link to="/external-books">Pesquisar Livros Externos</Link></li> {/* Nova rota */}
		  <li><Link to="/history">Histórico de Leitura</Link></li>
		  <li><Link to="/advanced-search">Pesquisa Avançada</Link></li>
        </ul>
      </nav>

      {/* Rotas da aplicação */}
      <Routes>
        <Route path="/" element={<BookList />} />
        <Route path="/borrow" element={<BorrowBook />} />
        <Route path="/return" element={<ReturnBook />} />
        <Route path="/recommendations" element={<Recommendations />} />
        <Route path="/register" element={<RegisterUser />} />
        <Route path="/external-books" element={<ExternalBookSearch />} /> {/* Nova rota */}
		<Route path="/history" element={<UserHistory />} />
		<Route path="/advanced-search" element={<AdvancedSearch />} />
      </Routes>
    </div>
  );
};

export default App;
