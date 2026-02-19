const db = require("../db/database");

// Create Server
const createServer = (req, res) => {
    const { name } = req.body;

    if (!name) {
        return res.status(400).json({ message: "Server name is required" });
    }

    const id = Date.now().toString();

    const stmt = db.prepare("INSERT INTO servers (id, name) VALUES (?, ?)");
    stmt.run(id, name);

    const newServer = db.prepare("SELECT * FROM servers WHERE id = ?").get(id);

    res.status(201).json(newServer);
};

// Get All Servers
const getServers = (req, res) => {
    const servers = db.prepare("SELECT * FROM servers ORDER BY created_at DESC").all();
    res.json(servers);
};

module.exports = {
    createServer,
    getServers,
};
