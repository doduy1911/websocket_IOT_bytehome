package com.example.websocket_IOT.Service;

import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class FrameBufferService {
    private final Map<String,byte[]> buffers = new ConcurrentHashMap<>();

    public void saveFrame(String userId , String deviceId , byte[] frame){
        String key = userId + ":" + deviceId;
        buffers.put(key,frame);
    }
    public byte[] getFrame(String userId , String deviceId){
       String key = userId + ":" + deviceId;
       return buffers.get(key);
    }
}
