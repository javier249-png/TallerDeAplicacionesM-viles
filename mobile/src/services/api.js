import axios from 'axios';

// Reemplaza 10.0.2.2 o tu IP local seg�n donde corra tu backend
const API = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default API;
