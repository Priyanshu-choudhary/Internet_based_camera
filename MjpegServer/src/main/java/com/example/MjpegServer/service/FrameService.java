package com.example.MjpegServer.service;

import org.springframework.stereotype.Service;
import java.util.concurrent.ConcurrentHashMap;

@Service


public class FrameService {
    private final ConcurrentHashMap<String, byte[]> frames = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, Stats> statsMap = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, String> commandMap = new ConcurrentHashMap<>();

    public void updateFrame(String camId, byte[] data) {
        frames.put(camId, data);
    }

    public byte[] getFrame(String camId) {
        return frames.get(camId);
    }

    public boolean hasFrame(String camId) {
        return frames.containsKey(camId);
    }

    public void recordStats(String camId, int bytes) {
        Stats s = statsMap.computeIfAbsent(camId, k -> new Stats());
        s.totalBytes += bytes;
        s.frameCount++;
        long now = System.currentTimeMillis();
        if (now - s.lastTime >= 1000) {
            double fps = s.frameCount * 1000.0 / (now - s.lastTime);
            double kbPerSec = s.totalBytes / 1024.0 / ((now - s.lastTime) / 1000.0);
            System.out.printf("[CAM %s] FPS: %.2f, Bandwidth: %.2f KB/s%n", camId, fps, kbPerSec);
            s.frameCount = 0;
            s.totalBytes = 0;
            s.lastTime = now;
        }
    }

    static class Stats {
        int frameCount = 0;
        long totalBytes = 0;
        long lastTime = System.currentTimeMillis();
    }
    public void setCommandForCam(String camId, String cmd) {
        commandMap.put(camId, cmd);
    }

    public String getCommandForCam(String camId) {
        return commandMap.remove(camId); // remove after sending once
    }

}

