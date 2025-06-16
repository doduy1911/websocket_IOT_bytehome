package com.example.websocket_IOT.Controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/user")
public class DeviceController {
    private final WebsocketController websocketController;

    public DeviceController(WebsocketController websocketController) {
        this.websocketController = websocketController;
    }

    @PostMapping("/{userId}/device/{deviceId}/startcam")
    public ResponseEntity<String> startCamera(@PathVariable String userId, @PathVariable String deviceId) {

        try {
            // System.out.println(userId + deviceId );
            websocketController.SendCommand(userId, deviceId, "START_CAMERA");
            return ResponseEntity.ok().body("Camera start command sent");
        } catch (Exception e) {
            return ResponseEntity.status(500).body(e.getMessage());
        }
    }

    @PostMapping("/{userId}/device/{deviceId}/stopcam")
    public ResponseEntity<String> stopCamera(@PathVariable String userId, @PathVariable String deviceId) {

        try {
            // System.out.println(userId + deviceId );
            websocketController.SendCommand(userId, deviceId, "STOP_CAMERA");
            return ResponseEntity.ok().body("Camera start command sent");
        } catch (Exception e) {
            return ResponseEntity.status(500).body(e.getMessage());
        }
    }

    @GetMapping("/connected")
    public ResponseEntity<List<String>> getConnectedDevices() {
        List<String> connected = websocketController.getConnectedDevices();
        return ResponseEntity.ok(connected);
    }

}
