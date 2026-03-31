package com.example.iot.device

import com.google.android.gms.wearable.DataClient
import com.google.android.gms.wearable.DataEventBuffer
import com.google.android.gms.wearable.PutDataMapRequest
import com.google.android.gms.wearable.Wearable
import com.google.android.gms.wearable.WearableListenerService

/**
 * Device Layer — HealthSensorService.kt
 * ======================================
 * Runs on the wearable device (Wear OS in this example, but the architecture
 * is the same for any device SDK — Fitbit, custom BLE, MQTT node, etc.).
 *
 * Reads sensor data and pushes it to the phone bridge layer via the
 * platform's data channel (here: Wearable DataClient).
 *
 * Cross-layer clone targets (same canonical names appear in bridge + cloud):
 *   getHeartRate()    ↔  PhoneGatewayService.getHeartRate()   ↔  GET /heart-rate
 *   getUserProfile()  ↔  PhoneGatewayService.getUserProfile() ↔  GET /user/profile
 *   postActivityLog() ↔  PhoneGatewayService.postActivityLog()↔  POST /activity/log
 *   getSleepData()    ↔  PhoneGatewayService.getSleepData()   ↔  GET /sleep/data
 */
class HealthSensorService : WearableListenerService() {

    private val dataClient: DataClient by lazy { Wearable.getDataClient(this) }

    // ── Sensor reads ────────────────────────────────────────────────────────

    /**
     * Read the current heart-rate BPM from the on-device sensor and push
     * it to the bridge layer over the wearable data channel.
     *
     * CLONE TARGET: PhoneGatewayService.getHeartRate() and GET /heart-rate
     */
    fun getHeartRate(): Int {
        val bpm = readHeartRateSensor()
        val request = PutDataMapRequest.create("/heart-rate").apply {
            dataMap.putInt("bpm", bpm)
            dataMap.putLong("timestamp", System.currentTimeMillis())
        }
        dataClient.putDataItem(request.asPutDataRequest())
        return bpm
    }

    /**
     * Retrieve the stored user profile from local device storage.
     *
     * CLONE TARGET: PhoneGatewayService.getUserProfile() and GET /user/profile
     */
    fun getUserProfile(userId: String): Map<String, Any> {
        val messageClient = Wearable.getMessageClient(this)
        messageClient.sendMessage("", "/user/profile", userId.toByteArray())
        return mapOf("userId" to userId, "source" to "device")
    }

    /**
     * Log a completed workout activity into the device's local data store
     * and sync it to the bridge layer.
     *
     * CLONE TARGET: PhoneGatewayService.postActivityLog() and POST /activity/log
     */
    fun postActivityLog(activityType: String, durationMinutes: Int) {
        val request = PutDataMapRequest.create("/activity/log").apply {
            dataMap.putString("type", activityType)
            dataMap.putInt("duration", durationMinutes)
            dataMap.putLong("startTime", System.currentTimeMillis())
            dataMap.putString("source", "device")
        }
        dataClient.putDataItem(request.asPutDataRequest())
    }

    /**
     * Collect overnight sleep data from the sleep-tracking sensor.
     *
     * CLONE TARGET: PhoneGatewayService.getSleepData() and GET /sleep/data
     */
    fun getSleepData(date: String): Map<String, Any> {
        val sleepMinutes = readSleepSensor(date)
        val request = PutDataMapRequest.create("/sleep/data").apply {
            dataMap.putInt("sleepMinutes", sleepMinutes)
            dataMap.putString("date", date)
        }
        dataClient.putDataItem(request.asPutDataRequest())
        return mapOf("sleepMinutes" to sleepMinutes, "date" to date)
    }

    // ── Lifecycle ────────────────────────────────────────────────────────────

    override fun onDataChanged(events: DataEventBuffer) {
        super.onDataChanged(events)
        events.forEach { processIncomingData(it) }
    }

    // ── Private sensor stubs (platform-specific implementation) ─────────────

    private fun readHeartRateSensor(): Int = 72                  // stub: real impl reads HW register
    private fun readSleepSensor(date: String): Int = 480         // stub: 8 hours in minutes
    private fun processIncomingData(event: Any) { /* handle replies from phone */ }
}
