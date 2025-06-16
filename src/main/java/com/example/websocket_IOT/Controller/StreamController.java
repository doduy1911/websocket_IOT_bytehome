package com.example.websocket_IOT.Controller;

import com.example.websocket_IOT.Service.FrameBufferService;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.StreamingResponseBody;

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
        frameBufferService.saveFrame(userId, deviceId, image);
        return ResponseEntity.ok("ok");
    }

    // Stream MJPEG về frontend
    @GetMapping(value = "/stream-view/{userId}/{deviceId}", produces = "multipart/x-mixed-replace;boundary=frame")
    public ResponseEntity<StreamingResponseBody> streamView(
            @PathVariable String userId,
            @PathVariable String deviceId
    ) {
        StreamingResponseBody responseBody = outputStream -> {
            while (true) {
                byte[] frame = frameBufferService.getFrame(userId, deviceId);
                if (frame != null) {
                    outputStream.write((
                            "--frame\r\n" +
                                    "Content-Type: image/jpeg\r\n" +
                                    "Content-Length: " + frame.length + "\r\n\r\n").getBytes());
                    outputStream.write(frame);
                    outputStream.write("\r\n".getBytes());
                    outputStream.flush();
                }

                try {
                    Thread.sleep(100); // Gửi frame mỗi 100ms
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt(); // Ngắt luồng đúng cách
                    break; // Thoát nếu bị ngắt
                }
            }
        };

        return ResponseEntity.ok(responseBody);
    }
}
