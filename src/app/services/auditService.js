// src/app/services/auditService.js
// Service to communicate with AuditFlow API

const API_BASE_URL = 'http://localhost:8000'; // Or configure via ENV

/**
 * Sends a list of transactions to the backend for Benford's Law analysis.
 * @param {number[]} transactions - List of monetary values.
 * @returns {Promise<Object>} - The analysis result (expected, observed, anomalies).
 */
export async function analyzeBenford(transactions) {
  try {
    const response = await fetch(`${API_BASE_URL}/analyze/benford`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ transactions }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to analyze data');
    }

    return await response.json();
  } catch (error) {
    console.error('Audit Service Error:', error);
    throw error;
  }
}
