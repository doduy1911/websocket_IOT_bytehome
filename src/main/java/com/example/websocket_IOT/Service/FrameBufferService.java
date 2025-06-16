package com.example.websocket_IOT.Service;

import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class FrameBufferService {
    private final Map<String, byte[]> frameBuffer = new ConcurrentHashMap<>();

    public void saveFrame(String userId, String deviceId, byte[] frame) {
        if (frame != null && frame.length > 0) {
            frameBuffer.put(userId + "_" + deviceId, frame);
        }
    }

    public byte[] getFrame(String userId, String deviceId) {
        return frameBuffer.get(userId + "_" + deviceId);
    }
}