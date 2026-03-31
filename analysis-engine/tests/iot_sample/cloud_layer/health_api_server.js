/**
 * Cloud Layer — health_api_server.js
 * ====================================
 * Node.js / Express REST API that receives data from the phone bridge.
 *
 * Cross-layer clone targets (REST endpoints canonicalize to match Kotlin names):
 *   GET  /heart-rate     → canonical: getHeartRate    ↔ both Kotlin layers
 *   GET  /user/profile   → canonical: getUserProfile  ↔ both Kotlin layers
 *   POST /activity/log   → canonical: postActivityLog ↔ both Kotlin layers
 *   GET  /sleep/data     → canonical: getSleepData    ↔ both Kotlin layers
 *
 * The CodeSpectra engine canonicalises REST endpoints via _rest_to_canonical():
 *   GET  /heart-rate   → getHeartRate
 *   GET  /user/profile → getUserProfile
 *   POST /activity/log → postActivityLog
 *   GET  /sleep/data   → getSleepData
 * ...which then matches the Kotlin function names extracted from the other layers.
 */

'use strict';

const express = require('express');
const app     = express();
app.use(express.json());

// ── In-memory store (replace with DB in production) ─────────────────────────
const store = {
  heartRate: [],
  activities: [],
  sleep: [],
  users: { 'demo-user': { name: 'Demo User', age: 28, deviceId: 'wear-001' } },
};

// ── Health check ─────────────────────────────────────────────────────────────

app.get('/health', (req, res) => {
  res.json({ status: 'ok', uptime: process.uptime() });
});

// ── Heart-rate endpoint ───────────────────────────────────────────────────────
// canonical name: getHeartRate  (matches both Kotlin layers)

app.get('/heart-rate', (req, res) => {
  const latest = store.heartRate.at(-1) ?? { bpm: 0, timestamp: null };
  res.json({ bpm: latest.bpm, timestamp: latest.timestamp, unit: 'bpm' });
});

app.post('/heart-rate', (req, res) => {
  const { bpm, timestamp, source } = req.body;
  if (typeof bpm !== 'number') return res.status(400).json({ error: 'bpm required' });
  store.heartRate.push({ bpm, timestamp: timestamp ?? Date.now(), source });
  res.status(201).json({ stored: true, bpm });
});

// ── User profile endpoint ─────────────────────────────────────────────────────
// canonical name: getUserProfile  (matches both Kotlin layers)

app.get('/user/profile', (req, res) => {
  const id      = req.query.id ?? 'demo-user';
  const profile = store.users[id];
  if (!profile) return res.status(404).json({ error: 'User not found' });
  res.json({ userId: id, ...profile });
});

app.put('/user/profile', (req, res) => {
  const { id, ...updates } = req.body;
  if (!id) return res.status(400).json({ error: 'id required' });
  store.users[id] = { ...(store.users[id] ?? {}), ...updates };
  res.json({ updated: true, userId: id });
});

// ── Activity log endpoint ─────────────────────────────────────────────────────
// canonical name: postActivityLog  (matches both Kotlin layers)

app.post('/activity/log', (req, res) => {
  const { type, duration, startTime, source } = req.body;
  if (!type || !duration) return res.status(400).json({ error: 'type and duration required' });
  const entry = { type, duration, startTime: startTime ?? Date.now(), source };
  store.activities.push(entry);
  res.status(201).json({ logged: true, entry });
});

app.get('/activity/log', (req, res) => {
  const { from, to } = req.query;
  let results = store.activities;
  if (from) results = results.filter(a => a.startTime >= Number(from));
  if (to)   results = results.filter(a => a.startTime <= Number(to));
  res.json({ count: results.length, activities: results });
});

// ── Sleep data endpoint ───────────────────────────────────────────────────────
// canonical name: getSleepData  (matches both Kotlin layers)

app.get('/sleep/data', (req, res) => {
  const { date } = req.query;
  const record   = store.sleep.find(s => s.date === date) ?? { sleepMinutes: 0, date };
  res.json(record);
});

app.post('/sleep/data', (req, res) => {
  const { sleepMinutes, date, source } = req.body;
  if (sleepMinutes == null || !date) return res.status(400).json({ error: 'sleepMinutes and date required' });
  store.sleep.push({ sleepMinutes, date, source });
  res.status(201).json({ stored: true, date });
});

// ── Server start ─────────────────────────────────────────────────────────────

const PORT = process.env.PORT ?? 3000;
app.listen(PORT, () => {
  console.log(`[Cloud API] Health API server running on port ${PORT}`);
  console.log('[Cloud API] Cross-layer endpoints:');
  console.log('  GET  /heart-rate    → canonical: getHeartRate');
  console.log('  GET  /user/profile  → canonical: getUserProfile');
  console.log('  POST /activity/log  → canonical: postActivityLog');
  console.log('  GET  /sleep/data    → canonical: getSleepData');
});

module.exports = app;
