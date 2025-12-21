const API_URL = import.meta.env.VITE_API_URL || 'https://auditflow-api.railway.app';
import { getAuthHeader } from './authService';

const getHeaders = () => {
    const token = localStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
};

export const inviteUser = async (userData) => {
    try {
        const response = await fetch(`${API_URL}/firm/team/invite`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(userData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to invite user');
        }
        return await response.json();
    } catch (error) {
        throw error;
    }
};

export const getFirmUsers = async () => { // If needed
    const response = await fetch(`${API_URL}/firm/team`, {
        headers: getHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch team');
    return response.json();
};
