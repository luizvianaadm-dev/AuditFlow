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

export const getStandardAccounts = async () => {
  const response = await fetch(`${API_URL}/mapping/standard-accounts`, {
    headers: getHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch standard accounts');
  return response.json();
};

export const uploadTrialBalanceForMapping = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_URL}/mapping/upload-trial-balance`, {
        method: 'POST',
        headers: getHeaders(true),
        body: formData,
    });
    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Failed to analyze file');
    }
    return response.json(); // Returns list of unmapped strings
};

export const saveMappings = async (mappings) => {
    // mappings = [{client_description, standard_account_id}, ...]
    const response = await fetch(`${API_URL}/mapping/bulk-map`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(mappings),
    });
    if (!response.ok) throw new Error('Failed to save mappings');
    return response.json();
};
