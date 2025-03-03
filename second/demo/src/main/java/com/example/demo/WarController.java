package com.example.demo;

import org.springframework.web.bind.annotation.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import java.util.List;

@CrossOrigin(origins = "*") // Allow all origins
@RestController
@RequestMapping("/api/events")
public class WarController {

    @Autowired
    private EventRepository eventRepository;

    @GetMapping("/events")
    public ResponseEntity<List<Event>> getEvents() {
        List<Event> events = eventRepository.findAll();
        return ResponseEntity.ok(events);
    }

}
