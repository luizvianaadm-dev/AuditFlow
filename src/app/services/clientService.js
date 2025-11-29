const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const getHeaders = (isMultipart = false) => {
  const token = localStorage.getItem('auditflow_token');
  const headers = {
    'Authorization': `Bearer ${token}`,
  };
  if (!isMultipart) {
      headers['Content-Type'] = 'application/json';
  }
  return headers;
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

export const getEngagements = async (clientId) => {
  const response = await fetch(`${API_URL}/clients/${clientId}/engagements`, {
    headers: getHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch engagements');
  return response.json();
};

export const createEngagement = async (clientId, name, year) => {
  const response = await fetch(`${API_URL}/clients/${clientId}/engagements`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ name, year }),
  });
  if (!response.ok) throw new Error('Failed to create engagement');
  return response.json();
};

export const getTransactions = async (engagementId) => {
    const response = await fetch(`${API_URL}/engagements/${engagementId}/transactions`, {
        headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch transactions');
    return response.json();
};

export const uploadTransactionFile = async (engagementId, file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_URL}/engagements/${engagementId}/upload`, {
        method: 'POST',
        headers: getHeaders(true), // isMultipart = true
        body: formData,
    });
    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Failed to upload file');
    }
    return response.json();
};

export const runBenfordAnalysis = async (engagementId) => {
    const response = await fetch(`${API_URL}/engagements/${engagementId}/run-benford`, {
        method: 'POST',
        headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to run Benford analysis');
    return response.json();
};

export const getAnalysisResults = async (engagementId) => {
    const response = await fetch(`${API_URL}/engagements/${engagementId}/results`, {
        headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch results');
    return response.json();
};

export const downloadReport = async (engagementId, engagementName) => {
    const response = await fetch(`${API_URL}/engagements/${engagementId}/report`, {
        headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to download report');

    // Create blob and download link
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Relatorio_${engagementName.replace(/\s/g, '_')}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
};
