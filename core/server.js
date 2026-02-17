require("dotenv").config();
const http = require("http");
const app = require("./src/app");
const { pool, testConnection } = require("./src/db/pool");

const server = http.createServer(app);

const PORT = process.env.PORT || 5000;

server.listen(PORT, async () => {
  try {
    await testConnection();       // verifies DB
    await pool.query("SELECT 1"); // test query
    console.log(`🚀 Server running on port ${PORT}`);
  } catch (err) {
    console.error("❌ Database connection failed:", err);
  }
});
