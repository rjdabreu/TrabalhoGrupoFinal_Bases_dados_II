import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

const UserHistory = () => {
    const [loans, setLoans] = useState([]);
    const [userId, setUserId] = useState('');
    const [error, setError] = useState('');

    // Função fetchLoans encapsulada com useCallback para estabilidade
    const fetchLoans = useCallback(async () => {
        if (!userId) {
            setLoans([]);
            setError('Por favor, insira o ID do utilizador.');
            return;
        }

        try {
            const response = await api.get(`/loans`, {
                params: { user_id: userId }
            });
            setLoans(response.data);
            setError('');
        } catch (err) {
            setError('Erro ao pesquisar o histórico de leitura.');
            setLoans([]); // Limpar os dados em caso de erro
        }
    }, [userId]);

    // useEffect para carregar o histórico quando userId muda
    useEffect(() => {
        fetchLoans();
    }, [fetchLoans]);

    return (
        <div>
            <h1>Histórico de Leitura</h1>
            <div style={{ marginBottom: '20px' }}>
                <input
                    type="text"
                    placeholder="Digite o ID do utilizador"
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    style={{
                        padding: '8px',
                        marginRight: '10px',
                        border: '1px solid #ccc',
                        borderRadius: '4px',
                    }}
                />
                <button
                    onClick={fetchLoans}
                    style={{
                        padding: '8px 15px',
                        backgroundColor: '#007BFF',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                    }}
                >
                    Buscar
                </button>
            </div>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            {loans.length > 0 ? (
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                        <tr>
                            <th style={{ border: '1px solid #ddd', padding: '8px' }}>Livro</th>
                            <th style={{ border: '1px solid #ddd', padding: '8px' }}>Data Empréstimo</th>
                            <th style={{ border: '1px solid #ddd', padding: '8px' }}>Data Devolução</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loans.map((loan) => (
                            <tr key={loan.id}>
                                <td style={{ border: '1px solid #ddd', padding: '8px' }}>{loan.livro}</td>
                                <td style={{ border: '1px solid #ddd', padding: '8px' }}>{loan.data_emprestimo}</td>
                                <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                                    {loan.data_devolucao || 'Não devolvido'}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            ) : !error && <p>Nenhum histórico encontrado para este utilizador.</p>}
        </div>
    );
};

export default UserHistory;
