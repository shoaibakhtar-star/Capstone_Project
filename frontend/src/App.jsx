import React, { useState } from "react";
import { registerUser, loginUser, getProfile } from "./api";

function App() {
  const [form, setForm] = useState({ username: "", password: "" });
  const [token, setToken] = useState("");
  const [message, setMessage] = useState("");
  const [profile, setProfile] = useState(null);
  const [backend, setBackend] = useState(localStorage.getItem("backend_target") || "round-robin");

  const handleBackendChange = (e) => {
    const value = e.target.value;
    setBackend(value);
    localStorage.setItem("backend_target", value);
    setMessage(`Target changed to: ${value}`);
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const register = async () => {
    try {
      setMessage("Registering...");
      const res = await registerUser(form);
      if (res.message) setMessage("✅ Success: " + res.message);
      else setMessage("❌ Error: " + (res.detail || "Failed"));
    } catch (err) {
      setMessage("❌ Network Error - Check Console");
    }
  };

  const login = async () => {
    try {
      setMessage("Logging in...");
      const res = await loginUser(form);
      if (res.access_token) {
        setToken(res.access_token);
        setMessage("✅ Logged in successfully");
      } else {
        setMessage("❌ Wrong credentials");
      }
    } catch (err) {
      setMessage("❌ Network Error");
    }
  };

  const fetchProfile = async () => {
    if (!token) return setMessage("❌ Login first");
    try {
      const res = await getProfile(token);
      setProfile(res);
      setMessage("👤 Profile loaded");
    } catch (err) {
      setMessage("❌ Failed to fetch profile");
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={{ marginBottom: "20px" }}>🔐 Auth System</h2>

        {/* BACKEND SELECTOR */}
        <div style={styles.selectorContainer}>
          <label style={styles.label}>Route via:</label>
          <select value={backend} onChange={handleBackendChange} style={styles.select}>
            <option value="round-robin"> ROUND ROBIN</option>
            <option value="fastapi"> FastAPI</option>
            <option value="django"> Django</option>
            <option value="node"> Node.js</option>
            <option value="dotnet"> .NET</option>
          </select>
        </div>

        <input name="username" placeholder="Username" onChange={handleChange} style={styles.input} />
        <input name="password" type="password" placeholder="Password" onChange={handleChange} style={styles.input} />

        <div style={styles.buttonGroup}>
          <button onClick={register} style={styles.buttonBlue}>Register</button>
          <button onClick={login} style={styles.buttonGreen}>Login</button>
        </div>

        <button onClick={fetchProfile} style={styles.buttonPurple}>Get Profile</button>

        {token && <button onClick={() => {setToken(""); setProfile(null); setMessage("👋 Logged out")}} style={styles.buttonRed}>Logout</button>}

        {message && <p style={styles.message}>{message}</p>}

        {profile && (
          <div style={styles.profile}>
            <p>ID: {profile.user_id}</p>
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: { height: "100vh", display: "flex", justifyContent: "center", alignItems: "center", background: "#0f172a", color: "#fff", fontFamily: "sans-serif" },
  card: { background: "#1e293b", padding: "30px", borderRadius: "12px", width: "320px", textAlign: "center", boxShadow: "0 10px 25px rgba(0,0,0,0.3)" },
  selectorContainer: { marginBottom: "15px", textAlign: "left", background: "#334155", padding: "10px", borderRadius: "8px" },
  label: { fontSize: "11px", color: "#94a3b8", textTransform: "uppercase", fontWeight: "bold" },
  select: { width: "100%", background: "transparent", color: "#fff", border: "1px solid #475569", padding: "5px", borderRadius: "4px", marginTop: "5px" },
  input: { width: "100%", padding: "10px", margin: "8px 0", borderRadius: "6px", border: "1px solid #334155", background: "#0f172a", color: "#fff", boxSizing: "border-box" },
  buttonGroup: { display: "flex", justifyContent: "space-between", gap: "10px" },
  buttonBlue: { background: "#3b82f6", color: "#fff", border: "none", padding: "10px", borderRadius: "6px", cursor: "pointer", flex: 1 },
  buttonGreen: { background: "#22c55e", color: "#fff", border: "none", padding: "10px", borderRadius: "6px", cursor: "pointer", flex: 1 },
  buttonPurple: { background: "#a855f7", color: "#fff", border: "none", padding: "10px", borderRadius: "6px", cursor: "pointer", width: "100%", marginTop: "10px" },
  buttonRed: { background: "#ef4444", color: "#fff", border: "none", padding: "10px", borderRadius: "6px", cursor: "pointer", width: "100%", marginTop: "10px" },
  message: { marginTop: "15px", fontSize: "13px", color: "#38bdf8" },
  profile: { marginTop: "15px", background: "#334155", padding: "10px", borderRadius: "6px" }
};

export default App;