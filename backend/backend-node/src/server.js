const express = require("express");
const cors = require("cors");
const pool = require("./db");
const { createToken } = require("./auth");
const authMiddleware = require("./middleware");

require("dotenv").config();

const app = express();

app.use(cors());
app.use(express.json());

app.use((req, res, next) => {
  const start = Date.now();

  console.log(`➡️ ${req.method} ${req.url}`);

  res.on("finish", () => {
    const duration = Date.now() - start;
    console.log(`⬅️ ${res.statusCode} ${req.method} ${req.url} - ${duration}ms`);
  });

  next();
});

/* ---------------- HEALTH ---------------- */
app.get("/health", async (req, res) => {
  try {
    await pool.query("SELECT 1");
    res.json({ status: "healthy nodejs" });
  } catch {
    res.status(503).json({ status: "unhealthy nodejs" });
  }
});

/* ---------------- REGISTER ---------------- */
app.post("/auth/register", async (req, res) => {
  const { username, password } = req.body;

  try {
    await pool.query(
      "INSERT INTO users (username, password) VALUES (?, ?)",
      [username, password]
    );

    res.json({ message: "User registered" });
  } catch (err) {
    res.status(400).json({ message: "User already exists" });
  }
});

/* ---------------- LOGIN ---------------- */
app.post("/auth/login", async (req, res) => {
  const { username, password } = req.body;

  const [rows] = await pool.query(
    "SELECT id, password FROM users WHERE username = ?",
    [username]
  );

  if (rows.length === 0) {
    return res.status(401).json({ message: "Invalid credentials" });
  }

  const user = rows[0];

  if (password !== user.password) {
    return res.status(401).json({ message: "Invalid credentials" });
  }

  const token = createToken(user.id);

  res.json({ access_token: token });
});

/* ---------------- PROFILE (PROTECTED) ---------------- */
app.get("/auth/profile", authMiddleware, async (req, res) => {
  res.json({ user_id: req.user.user_id });
});

/* ---------------- START SERVER ---------------- */
app.listen(process.env.PORT, () => {
  console.log(`Server running on port ${process.env.PORT || 3000}`);
});