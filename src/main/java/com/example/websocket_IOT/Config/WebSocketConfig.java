package com.example.websocket_IOT.Config;

import com.example.websocket_IOT.Controller.WebsocketController;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.config.annotation.EnableWebSocket;
import org.springframework.web.socket.config.annotation.WebSocketConfigurer;
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry;

@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {
    private final WebsocketController websocketController;
    public WebSocketConfig(WebsocketController websocketController) {
        this.websocketController = websocketController;
    }

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(websocketController, "/ws").setAllowedOrigins("*");
    }
}
