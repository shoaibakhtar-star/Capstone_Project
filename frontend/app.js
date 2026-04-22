import React, { useState } from "react";
import { registerUser, loginUser, getProfile } from "./api";

function App() {
  const [form, setForm] = useState({ username: "", password: "" });
  const [token, setToken] = useState("");
  const [profile, setProfile] = useState(null);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const register = async () => {
    const res = await registerUser(form);
    alert(JSON.stringify(res));
  };

  const login = async () => {
    const res = await loginUser(form);
    if (res.access_token) setToken(res.access_token);
  };

  const fetchProfile = async () => {
    const res = await getProfile(token);
    setProfile(res);
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Auth App</h2>

      <input name="username" placeholder="Username" onChange={handleChange} />
      <input name="password" type="password" placeholder="Password" onChange={handleChange} />

      <br /><br />

      <button onClick={register}>Register</button>
      <button onClick={login}>Login</button>
      <button onClick={fetchProfile}>Profile</button>

      <pre>{JSON.stringify(profile, null, 2)}</pre>
    </div>
  );
}

export default App;