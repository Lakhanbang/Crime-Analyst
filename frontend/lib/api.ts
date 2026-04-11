import axios from "axios";

// Create an Axios instance
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
});

export const getStates = async () => {
  const response = await api.get("/states");
  return response.data;
};

export const getStateData = async (state: string) => {
  const response = await api.get(`/states/${state}`);
  return response.data;
};

export const getCrimeData = async (state: string, crime: string) => {
  const response = await api.get(`/states/${state}/crime/${crime}`);
  return response.data;
};

export const getNationalAnalytics = async () => {
  const response = await api.get("/analytics/national");
  return response.data;
};

export const predictCrime = async (data: { state: string; crimeType: string; year: number }) => {
  const response = await api.post("/predict", data);
  return response.data;
};

export default api;
