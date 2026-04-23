const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");

require("dotenv").config();

const hashPassword = async (password) => {
  return await bcrypt.hash(password.slice(0, 72), 10);
};

const verifyPassword = async (password, hash) => {
  return await bcrypt.compare(password.slice(0, 72), hash);
};

const createToken = (userId) => {
  return jwt.sign(
    { user_id: userId },
    process.env.SECRET_KEY,
    { expiresIn: "30m" }
  );
};

const verifyToken = (token) => {
  return jwt.verify(token, process.env.SECRET_KEY);
};

module.exports = {
  hashPassword,
  verifyPassword,
  createToken,
  verifyToken,
};