import axios, { AxiosError } from "axios";

const API_BASE_URL =
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (import.meta as any).env?.VITE_API_BASE_URL || "";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      if (typeof window !== "undefined" && window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export interface User {
  id: string;
  email: string;
  full_name: string;
  onboarding_completed: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export const authService = {
  async register(payload: {
    email: string;
    full_name: string;
    password: string;
  }): Promise<User> {
    const { data } = await api.post("/api/v1/auth/register", payload);
    return data;
  },

  async login(payload: {
    email: string;
    password: string;
  }): Promise<AuthResponse> {
    const { data } = await api.post("/api/v1/auth/login", payload);
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("user", JSON.stringify(data.user));
    return data;
  },

  async logout(): Promise<void> {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  },

  async getMe(): Promise<User> {
    const { data } = await api.get<User>("/api/v1/auth/me");
    return data;
  },

  async getConsents(): Promise<any[]> {
    const { data } = await api.get("/api/v1/consents");
    return data;
  },

  async saveConsent(payload: {
    consent_type: string;
    granted: boolean;
    version?: string;
    purpose?: string;
  }): Promise<any> {
    const { data } = await api.post("/api/v1/consents", payload);
    return data;
  },

  async uploadPhoto(
    photoType: string,
    file: File
  ): Promise<{ photo_id: string; photo_type: string; message: string }> {
    const formData = new FormData();
    formData.append("photo_type", photoType);
    formData.append("file", file);
    const { data } = await api.post("/api/v1/photos", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  },

  async getPhotos(): Promise<any[]> {
    const { data } = await api.get("/api/v1/photos");
    return data;
  },

  async saveQuestionnaire(payload: {
    answers: Array<{
      question_key: string;
      answer_value: string;
      answer_type?: string;
    }>;
  }): Promise<any> {
    const { data } = await api.post("/api/v1/questionnaires", payload);
    return data;
  },

  async getLatestQuestionnaire(): Promise<any> {
    const { data } = await api.get("/api/v1/questionnaires/latest");
    return data;
  },
};
