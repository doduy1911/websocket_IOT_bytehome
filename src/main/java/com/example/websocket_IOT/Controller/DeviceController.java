package com.example.websocket_IOT.Controller;


import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/user")
public class DeviceController {
    private final WebsocketController websocketController;
    public DeviceController(WebsocketController websocketController) {
        this.websocketController = websocketController;
    }
    @PostMapping("/{userId}/device/{deviceId}/startcam")
    public ResponseEntity<String> startCamera(@PathVariable String userId, @PathVariable String deviceId) {
        try{
            websocketController.SendCommand(userId,deviceId,"START_CAMERA");
            return ResponseEntity.ok().body("Camera start command sent");
        }catch (Exception e){
            return ResponseEntity.status(500).body(e.getMessage());
        }
    }

     
}
