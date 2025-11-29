export const analyzeBenford = async (values) => {
  try {
    const response = await fetch('http://localhost:8000/analyze/benford', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ values }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Erro ao realizar a análise');
    }

    return await response.json();
  } catch (error) {
    console.error("Audit Service Error:", error);
    throw error;
  }
};
