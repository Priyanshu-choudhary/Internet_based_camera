package com.example.MjpegServer.Controllers;
import com.example.MjpegServer.service.FrameService;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import jakarta.servlet.http.HttpServletResponse;
import java.io.OutputStream;

@RestController
public class StreamController {
    private final FrameService frameService;

    public StreamController(FrameService frameService) {
        this.frameService = frameService;
    }

    // --- Camera upload endpoint ---
    @PostMapping("/upload")
    public String uploadFrame(@RequestParam String cam_id, @RequestBody byte[] data) {
        frameService.updateFrame(cam_id, data);
        frameService.recordStats(cam_id, data.length);

        // Example: dynamic control (from DB, memory, or API)
        String command = frameService.getCommandForCam(cam_id);
        return command != null ? command : "OK";
    }
    @PostMapping("/command/{camId}")
    public void setCommand(@PathVariable String camId, @RequestBody String command) {
        frameService.setCommandForCam(camId, command);
    }



    // --- MJPEG stream for viewers ---
    @GetMapping(value = "/stream/{camId}", produces = MediaType.MULTIPART_MIXED_VALUE)
    public void stream(@PathVariable String camId, HttpServletResponse response) throws Exception {
        response.setContentType("multipart/x-mixed-replace; boundary=frame");
        OutputStream out = response.getOutputStream();

        while (true) {
            if (frameService.hasFrame(camId)) {
                byte[] frame = frameService.getFrame(camId);
                out.write(("--frame\r\nContent-Type: image/jpeg\r\n\r\n").getBytes());
                out.write(frame);
                out.write("\r\n".getBytes());
                out.flush();

                Thread.sleep(50);
            }

        }
    }
}
