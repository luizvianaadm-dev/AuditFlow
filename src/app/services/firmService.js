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
};
