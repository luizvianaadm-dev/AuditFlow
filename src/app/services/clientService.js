const API_URL = 'http://localhost:8000';

const getHeaders = () => {
  const token = localStorage.getItem('auditflow_token');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
};

export const getClients = async () => {
  const response = await fetch(`${API_URL}/clients/`, {
    headers: getHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch clients');
  return response.json();
};

export const createClient = async (name) => {
  const response = await fetch(`${API_URL}/clients/`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ name }),
  });
  if (!response.ok) throw new Error('Failed to create client');
  return response.json();
};
