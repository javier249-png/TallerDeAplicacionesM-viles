const API_URL = process.env.EXPO_PUBLIC_API_URL || process.env.API_URL;

export const fetchData = async (endpoint) => {
  try {
    const response = await fetch(`${API_URL}/${endpoint}`);
    if (!response.ok) {
      throw new Error(`Error HTTP! estado: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error al conectar con el servidor:", error);
    throw error;
  }
};
