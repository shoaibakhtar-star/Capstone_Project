import React, { useState } from "react";
import { registerUser, loginUser, getProfile } from "./api";

function App() {
  const [form, setForm] = useState({ username: "", password: "" });
  const [token, setToken] = useState("");
  const [message, setMessage] = useState("");
  const [profile, setProfile] = useState(null);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const register = async () => {
    setMessage("");
    const res = await registerUser(form);

    if (res.message) {
      setMessage("✅ User registered successfully");
    } else {
      setMessage("❌ " + (res.detail || "Registration failed"));
    }
  };

  const login = async () => {
    setMessage("");
    const res = await loginUser(form);

    if (res.access_token) {
      setToken(res.access_token);
      setMessage("✅ Logged in successfully");
    } else {
      setMessage("❌ Wrong credentials");
    }
  };

  const fetchProfile = async () => {
    if (!token) {
      setMessage("❌ Please login first");
      return;
    }

    const res = await getProfile(token);

    if (res.user_id) {
      setProfile(res);
      setMessage("👤 Profile loaded");
    } else {
      setMessage("❌ Invalid token");
    }
  };

  const logout = () => {
    setToken("");
    setProfile(null);
    setMessage("👋 Logged out");
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2>🔐 Auth System</h2>

        {/* INPUTS */}
        <input
          name="username"
          placeholder="Username"
          onChange={handleChange}
          style={styles.input}
        />

        <input
          name="password"
          type="password"
          placeholder="Password"
          onChange={handleChange}
          style={styles.input}
        />

        {/* BUTTONS */}
        <div style={styles.buttonGroup}>
          <button onClick={register} style={styles.buttonBlue}>
            Register
          </button>
          <button onClick={login} style={styles.buttonGreen}>
            Login
          </button>
        </div>

        <button onClick={fetchProfile} style={styles.buttonPurple}>
          Get Profile
        </button>

        {token && (
          <button onClick={logout} style={styles.buttonRed}>
            Logout
          </button>
        )}

        {/* STATUS MESSAGE */}
        {message && <p style={styles.message}>{message}</p>}

        {/* PROFILE SECTION */}
        {profile && (
          <div style={styles.profile}>
            <h3>👤 Profile</h3>
            <p>User ID: {profile.user_id}</p>
          </div>
        )}

        {/* LOGIN STATUS */}
        <div style={styles.status}>
          {token ? "🟢 Logged In" : "🔴 Not Logged In"}
        </div>
      </div>
    </div>
  );
}

export default App;

const styles = {
  container: {
    height: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "#0f172a",
    color: "#fff",
    fontFamily: "Arial",
  },
  card: {
    background: "#1e293b",
    padding: "30px",
    borderRadius: "12px",
    width: "300px",
    textAlign: "center",
    boxShadow: "0 0 20px rgba(0,0,0,0.5)",
  },
  input: {
    width: "100%",
    padding: "10px",
    margin: "10px 0",
    borderRadius: "6px",
    border: "none",
  },
  buttonGroup: {
    display: "flex",
    justifyContent: "space-between",
  },
  buttonBlue: {
    background: "#3b82f6",
    color: "#fff",
    border: "none",
    padding: "10px",
    borderRadius: "6px",
    cursor: "pointer",
    width: "48%",
  },
  buttonGreen: {
    background: "#22c55e",
    color: "#fff",
    border: "none",
    padding: "10px",
    borderRadius: "6px",
    cursor: "pointer",
    width: "48%",
  },
  buttonPurple: {
    background: "#a855f7",
    color: "#fff",
    border: "none",
    padding: "10px",
    borderRadius: "6px",
    cursor: "pointer",
    width: "100%",
    marginTop: "10px",
  },
  buttonRed: {
    background: "#ef4444",
    color: "#fff",
    border: "none",
    padding: "10px",
    borderRadius: "6px",
    cursor: "pointer",
    width: "100%",
    marginTop: "10px",
  },
  message: {
    marginTop: "10px",
    fontSize: "14px",
  },
  profile: {
    marginTop: "15px",
    background: "#334155",
    padding: "10px",
    borderRadius: "6px",
  },
  status: {
    marginTop: "15px",
    fontSize: "14px",
    opacity: 0.8,
  },
};