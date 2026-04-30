// const API = "http://localhost:8000"; // fastApi

// const API = "http://localhost:8001"; // django

// const API = "http://localhost:8002"; // nodejs

// const API = "http://localhost:8003"; // .net


// const API = "http://localhost"; // nginx

const API = import.meta.env.VITE_API_BASE_URL || "";

// Helper to construct the URL based on selection
const getUrl = (path) => {
  const selection = localStorage.getItem("backend_target") || "round-robin";
  // If round-robin, use /auth/path. Otherwise use /django/auth/path, etc.
  const prefix = (selection === "round-robin" || !selection) ? "" : `/${selection}`;
  return `${API}${prefix}${path}`;
};

const getHeaders = (token = null) => {
  const headers = {
    "Content-Type": "application/json",
    "X-Backend-Select": localStorage.getItem("backend_target") || "round-robin",
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
};

export const registerUser = async (data) => {
  const res = await fetch(getUrl("/auth/register"), {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return res.json();
};

export const loginUser = async (data) => {
  const res = await fetch(getUrl("/auth/login"), {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return res.json();
};

export const getProfile = async (token) => {
  const res = await fetch(getUrl("/auth/profile"), {
    headers: getHeaders(token),
  });
  return res.json();
};