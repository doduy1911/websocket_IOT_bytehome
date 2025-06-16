package com.example.websocket_IOT.Controller;

import com.example.websocket_IOT.Service.Service.StreamFrameService;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.StreamingResponseBody;

import java.io.IOException;

@RestController
@RequestMapping("/api")
public class StreamController {

    private final StreamFrameService streamFrameService;

    public StreamController(StreamFrameService streamFrameService) {
        this.streamFrameService = streamFrameService;
    }

    @PostMapping(value = "/{userId}/{deviceId}/startcam", consumes = MediaType.IMAGE_JPEG_VALUE)
    public ResponseEntity<?> receiveFrame(
            @PathVariable String userId,
            @PathVariable String deviceId,
            @RequestBody byte[] imageBytes
    ) {
        System.out.println("📸 Nhận ảnh từ " + userId + "/" + deviceId + " - size: " + imageBytes.length);

        streamFrameService.updateFrame(userId, deviceId, imageBytes);
        return ResponseEntity.ok().build();
    }

    @GetMapping(value = "/stream-view/{userId}/{deviceId}", produces = MediaType.IMAGE_JPEG_VALUE)
    public ResponseEntity<byte[]> getLatestFrame(
            @PathVariable String userId,
            @PathVariable String deviceId
    ) {
        byte[] image = streamFrameService.getLatestFrame(userId, deviceId);
        if (image == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(image);
    }
}
