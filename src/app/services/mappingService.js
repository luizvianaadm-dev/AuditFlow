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

export const getMappingContext = async (engagementId) => {
    const response = await fetch(`${API_URL}/mapping/${engagementId}`, {
        headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch mapping context');
    return response.json();
};

export const saveAsStandard = async (engagementId) => {
    const response = await fetch(`${API_URL}/mapping/${engagementId}/save-as-standard`, {
        method: 'POST',
        headers: getHeaders(),
    });
    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Failed to save as standard');
    }
    return response.json();
};

export const setChartMode = async (engagementId, mode) => {
    const response = await fetch(`${API_URL}/mapping/${engagementId}/set-standard?chart_mode=${mode}`, {
        method: 'POST',
        headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to set chart mode');
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
    return response.json(); // Returns list of unmapped strings (legacy) or full data
};

export const saveMappings = async (mappings) => {
    // mappings = [{client_description, client_account_code, standard_account_id}, ...]
    const response = await fetch(`${API_URL}/mapping/bulk-map`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(mappings),
    });
    if (!response.ok) throw new Error('Failed to save mappings');
    return response.json();
};
