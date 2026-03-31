package com.example.iot.bridge

import com.google.android.gms.wearable.ChannelClient
import com.google.android.gms.wearable.DataClient
import com.google.android.gms.wearable.DataEventBuffer
import com.google.android.gms.wearable.Wearable

/**
 * Bridge Layer — PhoneGatewayService.kt
 * =======================================
 * Runs on the phone (or any intermediary gateway node — could equally be a
 * Raspberry Pi running Python, an AWS Greengrass edge device, or a BLE proxy).
 *
 * Its sole job is to receive data from the device layer and forward it to
 * the cloud REST API, and vice versa.
 *
 * Cross-layer clone sources (matches device layer + cloud layer):
 *   getHeartRate()    — matches HealthSensorService + GET /heart-rate
 *   getUserProfile()  — matches HealthSensorService + GET /user/profile
 *   postActivityLog() — matches HealthSensorService + POST /activity/log
 *   getSleepData()    — matches HealthSensorService + GET /sleep/data
 *
 * Additionally, fetchHeartRate() normalises to getHeartRate (synonym match).
 */
class PhoneGatewayService : DataClient.OnDataChangedListener {

    private val cloudBaseUrl = "https://api.health-example.com"

    // ── Data forwarding — device → cloud ────────────────────────────────────

    /**
     * Receive heart-rate reading from the device and forward to cloud.
     * EXACT MATCH with HealthSensorService.getHeartRate() (canonical: getHeartRate)
     * MATCHES cloud endpoint: GET /heart-rate (canonical: getHeartRate)
     */
    fun getHeartRate(): Int {
        val response = getFromCloud("/heart-rate")
        return parseIntField(response, "bpm")
    }

    /**
     * SYNONYM MATCH demo — fetchHeartRate normalises to getHeartRate.
     * The engine will recognise this as a synonym-type cross-layer clone.
     */
    fun fetchHeartRate(): Int {
        // same logic as getHeartRate — intentional synonym for demo
        val response = getFromCloud("/heart-rate")
        return parseIntField(response, "bpm")
    }

    /**
     * Retrieve user profile; bridge serves as local cache + cloud relay.
     * EXACT MATCH with HealthSensorService.getUserProfile()
     * MATCHES cloud endpoint: GET /user/profile (canonical: getUserProfile)
     */
    fun getUserProfile(userId: String): Map<String, Any> {
        val response = getFromCloud("/user/profile?id=$userId")
        return mapOf("userId" to userId, "raw" to response, "source" to "bridge")
    }

    /**
     * Buffer and forward activity log entries to the cloud.
     * EXACT MATCH with HealthSensorService.postActivityLog()
     * MATCHES cloud endpoint: POST /activity/log (canonical: postActivityLog)
     */
    fun postActivityLog(activityType: String, durationMinutes: Int) {
        val body = """{"type":"$activityType","duration":$durationMinutes,"source":"bridge"}"""
        postToCloud("/activity/log", body)
    }

    /**
     * Request sleep data and forward to cloud analytics pipeline.
     * EXACT MATCH with HealthSensorService.getSleepData()
     * MATCHES cloud endpoint: GET /sleep/data (canonical: getSleepData)
     */
    fun getSleepData(date: String): Map<String, Any> {
        val response = getFromCloud("/sleep/data?date=$date")
        return mapOf("date" to date, "raw" to response)
    }

    // ── Wearable data event handler ──────────────────────────────────────────

    override fun onDataChanged(events: DataEventBuffer) {
        events.forEach { event -> routeToCloud(event) }
    }

    // ── HTTP helpers (stub — real impl uses OkHttp / Retrofit) ───────────────

    private fun postToCloud(path: String, body: String) {
        // POST to $cloudBaseUrl$path with JSON body
    }

    private fun getFromCloud(path: String): String {
        // GET $cloudBaseUrl$path and return JSON string
        return "{}"
    }

    private fun routeToCloud(event: Any) { /* parse event path and call appropriate forwarder */ }

    private fun parseIntField(json: String, field: String): Int = 0
}
