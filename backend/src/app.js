const express = require("express");
const cors = require("cors");
require("dotenv").config();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Routes
const serverRoutes = require("./routes/serverRoutes");
app.use("/api/servers", serverRoutes);

// Root Test Route
app.get("/", (req, res) => {
    res.send("HangHive Backend is Running 🚀");
});

// Start Server
const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
