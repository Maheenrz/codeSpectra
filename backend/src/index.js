const express = require("express");
const cors    = require("cors");
const path    = require("path");
require("dotenv").config();

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use("/uploads", express.static(path.join(__dirname, "..", "uploads")));

const pool = require("./config/database");
pool.testConnection().catch(() => {
  console.error("Failed to connect to database — exiting");
  process.exit(1);
});

const analysisScheduler = require('./services/analysisScheduler');
analysisScheduler.start();

app.get("/", (req, res) => {
  res.json({
    message: "CodeSpectra API",
    version: "2.0.0",
    endpoints: {
      auth:        "/api/auth",
      users:       "/api/users",
      courses:     "/api/courses",
      assignments: "/api/assignments",
      submissions: "/api/submissions",
      analysis:    "/api/analysis",
    },
  });
});

app.get("/health", (req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString(), database: "connected" });
});

app.use("/api/auth",        require("./routes/auth.routes"));
app.use("/api/users",       require("./routes/users.routes"));
app.use("/api/courses",     require("./routes/courses.routes"));
app.use("/api/assignments", require("./routes/assignments.routes"));
app.use("/api/submissions", require("./routes/submissions.routes"));
app.use("/api/analysis",    require("./routes/analysis.routes"));

app.use((req, res) => {
  res.status(404).json({ error: "Route not found" });
});

app.use((err, req, res, next) => {
  console.error("Unhandled error:", err.stack);

  if (err.name === "MulterError") {
    if (err.code === "LIMIT_FILE_SIZE") {
      return res.status(400).json({ error: "File too large. Max size is 10MB" });
    }
    return res.status(400).json({ error: err.message });
  }

  res.status(500).json({
    message: "Something went wrong",
    error: process.env.NODE_ENV === "development" ? err.message : "Internal server error",
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`\n   🚀 CodeSpectra Backend — port ${PORT} (${process.env.NODE_ENV || "development"})\n`);
});
