package com.example.websocket_IOT.Controller;

import com.example.websocket_IOT.Service.FrameBufferService;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.StreamingResponseBody;

import java.io.IOException;

@RestController
@RequestMapping("/api")
public class StreamController {

    private final FrameBufferService frameBufferService;

    public StreamController(FrameBufferService frameBufferService) {
        this.frameBufferService = frameBufferService;
    }

    // Nhận frame từ client Pi
    @PostMapping(value = "/stream-frames/{userId}/{deviceId}", consumes = MediaType.IMAGE_JPEG_VALUE)
    public ResponseEntity<String> receiveFrame(
            @PathVariable String userId,
            @PathVariable String deviceId,
            @RequestBody byte[] image
    ) {
        if (image == null || image.length == 0) {
            return ResponseEntity.badRequest().body("Invalid or empty image data");
        }
        try {
            frameBufferService.saveFrame(userId, deviceId, image);
            return ResponseEntity.ok("ok");
        } catch (Exception e) {
            System.err.println("[Error saving frame]: " + e.getMessage());
            return ResponseEntity.status(500).body("Failed to save frame");
        }
    }

    // Stream MJPEG về frontend
    @GetMapping(value = "/stream-view/{userId}/{deviceId}", produces = "multipart/x-mixed-replace;boundary=frame")
    public ResponseEntity<StreamingResponseBody> streamView(
            @PathVariable String userId,
            @PathVariable String deviceId
    ) {
        StreamingResponseBody responseBody = outputStream -> {
            try {
                while (!Thread.currentThread().isInterrupted()) {
                    byte[] frame = frameBufferService.getFrame(userId, deviceId);
                    if (frame == null || frame.length == 0) {
                        Thread.sleep(50); // Đợi nếu không có frame mới
                        continue;
                    }

                    try {
                        outputStream.write((
                                "--frame\r\n" +
                                        "Content-Type: image/jpeg\r\n" +
                                        "Content-Length: " + frame.length + "\r\n\r\n").getBytes());
                        outputStream.write(frame);
                        outputStream.write("\r\n".getBytes());
                        outputStream.flush();
                    } catch (IOException e) {
                        System.err.println("[Stream error] IOException: " + e.getMessage());
                        break; // Thoát nếu client ngắt kết nối
                    }

                    Thread.sleep(100); // Gửi frame mỗi 100ms
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                System.err.println("[Stream interrupted]: " + e.getMessage());
            } finally {
                try {
                    outputStream.close();
                } catch (IOException e) {
                    System.err.println("[Stream close error]: " + e.getMessage());
                }
            }
        };

        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType("multipart/x-mixed-replace;boundary=frame"))
                .body(responseBody);
    }
}