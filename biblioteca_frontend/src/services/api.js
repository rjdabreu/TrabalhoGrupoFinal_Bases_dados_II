import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:5000', // URL do backend
});

// Nova função para Pesquisar livros no Open Library
export const searchExternalBooks = async (query) => {
  const response = await api.get(`/external-books?query=${query}`);
  return response.data;
};

export default api;
