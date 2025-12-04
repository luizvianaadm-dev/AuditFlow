const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const getHeaders = () => {
  const token = localStorage.getItem('auditflow_token');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
};

export const getFSContext = async (engagementId) => {
  const response = await fetch(`${API_URL}/engagements/${engagementId}/fs/context`, {
    headers: getHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch FS context');
  return response.json();
};

export const updateFSContext = async (engagementId, data) => {
  const response = await fetch(`${API_URL}/engagements/${engagementId}/fs/context`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to update FS context');
  return response.json();
};

export const generateFS = async (engagementId) => {
  const response = await fetch(`${API_URL}/engagements/${engagementId}/fs/generate`, {
    headers: getHeaders(),
  });
  if (!response.ok) throw new Error('Failed to generate Financial Statements');
  return response.json();
};

export const calculateCashFlow = async (engagementId, inputData) => {
  const response = await fetch(`${API_URL}/engagements/${engagementId}/fs/cash-flow`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(inputData),
  });
  if (!response.ok) throw new Error('Failed to calculate Cash Flow');
  return response.json();
};
