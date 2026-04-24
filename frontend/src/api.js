// const API = "http://localhost:8000"; // fastApi

// const API = "http://localhost:8001"; // django

// const API = "http://localhost:8002"; // nodejs

// const API = "http://localhost:8003"; // .net


const API = "http://localhost"; // nginx

export const registerUser = async (data) => {
  const res = await fetch(`${API}/auth/register`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data),
  });
  return res.json();
};

export const loginUser = async (data) => {
  const res = await fetch(`${API}/auth/login`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data),
  });
  return res.json();
};

export const getProfile = async (token) => {
  const res = await fetch(`${API}/auth/profile`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.json();
};