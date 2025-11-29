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

export const getFinancialSummary = async (engagementId) => {
    const response = await fetch(`${API_URL}/engagements/${engagementId}/financial-summary`, {
        headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch financial summary');
    return response.json();
};

export const saveMateriality = async (engagementId, data) => {
    const response = await fetch(`${API_URL}/engagements/${engagementId}/materiality`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to save materiality');
    return response.json();
};

export const uploadClientLogo = async (clientId, file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_URL}/circularization/clients/${clientId}/logo`, {
        method: 'POST',
        headers: getHeaders(true),
        body: formData,
    });
    if (!response.ok) throw new Error('Failed to upload logo');
    return response.json();
};

export const generateCircularization = async (engagementId, requests) => {
    // requests = [{type, recipient_name, recipient_email}]
    const response = await fetch(`${API_URL}/circularization/engagements/${engagementId}/generate`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(requests),
    });
    if (!response.ok) throw new Error('Failed to generate requests');
    return response.json();
};

export const downloadCircularizationZip = async (engagementId) => {
    const response = await fetch(`${API_URL}/circularization/engagements/${engagementId}/download`, {
        headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to download letters');

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Circularizacoes.zip`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
};

export const getClientAcceptance = async (clientId) => {
    const response = await fetch(`${API_URL}/clients/${clientId}/acceptance`, {
        headers: getHeaders(),
    });
    // Return null if 404/not found (meaning not created yet)
    if (response.status === 404) return null;
    if (!response.ok) return null;
    return response.json();
};

export const saveClientAcceptance = async (clientId, data) => {
    const response = await fetch(`${API_URL}/clients/${clientId}/acceptance`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to save acceptance');
    return response.json();
};

export const getTeam = async () => {
    const response = await fetch(`${API_URL}/firm/team`, {
        headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch team');
    return response.json();
};

export const inviteUser = async (data) => {
    const response = await fetch(`${API_URL}/firm/team/invite`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(data),
    });
    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Failed to invite user');
    }
    return response.json();
};

export const runRandomSampling = async (engagementId, sampleSize) => {
    const response = await fetch(`${API_URL}/engagements/${engagementId}/sampling/random`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ sample_size: sampleSize }),
    });
    if (!response.ok) throw new Error('Failed to run random sampling');
    return response.json();
};

export const runStratifiedSampling = async (engagementId, threshold, sampleSizeBelow) => {
    const response = await fetch(`${API_URL}/engagements/${engagementId}/sampling/stratified`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ threshold, sample_size_below: sampleSizeBelow }),
    });
    if (!response.ok) throw new Error('Failed to run stratified sampling');
    return response.json();
};
