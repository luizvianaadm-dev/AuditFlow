const API_URL = import.meta.env.VITE_API_URL || 'https://auditflow-api.railway.app';

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

export const uploadLetterhead = async (engagementId, file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_URL}/engagements/${engagementId}/letterhead`, {
        method: 'POST',
        headers: getHeaders(true), // isMultipart = true
        body: formData,
    });
    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Failed to upload letterhead');
    }
    return response.json();
};

export const runBenfordAnalysis = async (engagementId) => {
    const response = await fetch(`${API_URL}/engagements/${engagementId}/run-benford`, {
        method: 'POST',
        headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to run Benford analysis');
    return response.json(); // Returns { task_id: ... }
};

export const getTaskStatus = async (taskId) => {
    const response = await fetch(`${API_URL}/engagements/tasks/${taskId}`, {
        headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to check task status');
    return response.json();
};

export const pollTask = async (taskId, interval = 2000, timeout = 60000) => {
    const startTime = Date.now();
    while (Date.now() - startTime < timeout) {
        const status = await getTaskStatus(taskId);
        if (status.status === 'SUCCESS') {
            return status.result;
        }
        if (status.status === 'FAILURE' || status.status === 'REVOKED') {
            throw new Error('Analysis failed');
        }
        await new Promise(resolve => setTimeout(resolve, interval));
    }
    throw new Error('Analysis timed out');
};

export const getAnalysisResults = async (engagementId) => {
    const response = await fetch(`${API_URL}/engagements/${engagementId}/results`, {
        headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch results');
    return response.json();
};

export const downloadReport = async (engagementId, engagementName, format = 'pdf') => {
    const response = await fetch(`${API_URL}/engagements/${engagementId}/report?format=${format}`, {
        headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to download report');

    // Create blob and download link
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Relatorio_${engagementName.replace(/\s/g, '_')}.${format}`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
};

export const downloadExport = async (engagementId, type, format = 'xlsx') => {
    // type: benford, duplicates, transactions, mistatements
    const response = await fetch(`${API_URL}/engagements/${engagementId}/export/${type}?format=${format}`, {
        headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to download export');

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${type}_${engagementId}.${format}`;
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

return response.json();
};

export const calculateMaterialitySuggestion = async (engagementId) => {
    const response = await fetch(`${API_URL}/engagements/${engagementId}/materiality/calculate`, {
        method: 'POST',
        headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to calculate materiality suggestion');
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

export const uploadPayroll = async (engagementId, file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_URL}/engagements/${engagementId}/payroll/upload`, {
        method: 'POST',
        headers: getHeaders(true),
        body: formData,
    });
    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Failed to upload payroll');
    }
    return response.json();
};

export const runPayrollReconciliation = async (engagementId) => {
    const response = await fetch(`${API_URL}/engagements/${engagementId}/payroll/reconcile`, {
        method: 'POST',
        headers: getHeaders(),
    });
    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Failed to reconcile payroll');
    }
    return response.json();
};

export const generateWorkPapers = async (engagementId) => {
    const response = await fetch(`${API_URL}/workpapers/engagements/${engagementId}/generate`, {
        method: 'POST',
        headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to generate workpapers');
    return response.json();
};

export const getWorkPapers = async (engagementId) => {
    const response = await fetch(`${API_URL}/workpapers/engagements/${engagementId}`, {
        headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch workpapers');
    return response.json();
};

export const updateWorkPaper = async (wpId, data) => {
    const response = await fetch(`${API_URL}/workpapers/${wpId}/update`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to update workpaper');
    return response.json();
};

export const addMistatement = async (engagementId, data) => {
    const response = await fetch(`${API_URL}/workpapers/engagements/${engagementId}/mistatements`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to add mistatement');
    return response.json();
};

export const getMistatementSummary = async (engagementId) => {
    const response = await fetch(`${API_URL}/workpapers/engagements/${engagementId}/summary-of-mistatements`, {
        headers: getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch mistatement summary');
    return response.json();
};

export const getPlans = async () => {
    const response = await fetch(`${API_URL}/billing/plans`, { headers: getHeaders() });
    return response.json();
};

export const getMySubscription = async () => {
    const response = await fetch(`${API_URL}/billing/my-subscription`, { headers: getHeaders() });
    return response.json();
};

export const subscribeToPlan = async (planId) => {
    const response = await fetch(`${API_URL}/billing/subscribe`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ plan_id: planId }),
    });
    if (!response.ok) throw new Error('Failed to subscribe');
    return response.json();
};
