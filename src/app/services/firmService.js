const API_URL = import.meta.env.VITE_API_URL || 'https://auditflow-api.railway.app';
import { getAuthHeader } from './authService'; // Assuming I can export this or recreate logic

const getHeaders = () => {
    const token = localStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
};

export const getDepartments = async () => {
    const response = await fetch(`${API_URL}/firm/departments`, {
        headers: getHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch departments');
    return response.json();
};

export const getJobRoles = async () => {
    const response = await fetch(`${API_URL}/firm/job-roles`, {
        headers: getHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch roles');
    return response.json();
    return response.json();
};

export const getFirmDetails = async () => {
    const response = await fetch(`${API_URL}/firm/`, {
        headers: getHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch firm details');
    return response.json();
};

export const updateFirmDetails = async (data) => {
    const response = await fetch(`${API_URL}/firm/`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to update firm details');
    return response.json();
};

export const uploadLetterhead = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    // Custom header specifically for file upload (auto-boundary)
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_URL}/firm/letterhead`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`
        },
        body: formData
    });

    if (!response.ok) throw new Error('Failed to upload letterhead');
    return response.json();
};
