package com.example.websocket_IOT.Service.Service;

import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class StreamFrameService {
    private final Map<String, byte[]> latestFrames = new ConcurrentHashMap<>();

    public void updateFrame(String userId, String deviceId, byte[] imageBytes) {
        String key = userId + ":" + deviceId;
        latestFrames.put(key, imageBytes);
    }

    public byte[] getLatestFrame(String userId, String deviceId) {
        String key = userId + ":" + deviceId;
        return latestFrames.get(key);
    }
}