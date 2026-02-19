const express = require("express");
const router = express.Router();

const {
    createServer,
    getServers,
} = require("../controllers/serverController");

// Create a new server
router.post("/", createServer);

// Get all servers
router.get("/", getServers);

module.exports = router;
