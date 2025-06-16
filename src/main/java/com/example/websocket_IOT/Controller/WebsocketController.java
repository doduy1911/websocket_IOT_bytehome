package com.example.websocket_IOT.Controller;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@Component
public class WebsocketController extends TextWebSocketHandler {
    private final Map<String , WebSocketSession> sessions = new ConcurrentHashMap<>();

    @Override
    public void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        ObjectMapper mapper = new ObjectMapper();
        JsonNode json = mapper.readTree(message.getPayload());
         if("REGISTER".equals(json.get("type").asText())){
             String userId = json.get("userId").asText();
             String deviceId = json.get("deviceId").asText();
             String key = userId + ":" + deviceId;
             sessions.put(key, session);
             System.out.println("Register" + ":" + key);
         }
    }

    public void SendCommand(String userId , String deviceId,String command ) throws Exception {
        String key = userId + ":" + deviceId;
        System.out.println(key);
        System.out.println(sessions.keySet());
        WebSocketSession session = sessions.get(key);
        System.out.println(session);
        if(session != null && session.isOpen()){
            ObjectMapper mapper = new ObjectMapper();
            Map<String,String> cmd = Map.of("command", command,"userId", userId,"deviceId", deviceId);
            System.out.println(cmd);
            System.out.println(userId);
            System.out.println(deviceId);
            System.out.println(command);
            session.sendMessage(new TextMessage(mapper.writeValueAsString(cmd)));
        }else {
            throw new Exception("Device not connected" + key);
        }
    }

    public List<String> getConnectedDevices() {
        return sessions.entrySet().stream()
                .filter(entry -> entry.getValue().isOpen())
                .map(Map.Entry::getKey)
                .collect(Collectors.toList());
    }
}
