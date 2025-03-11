package com.example.demo;

import org.springframework.web.bind.annotation.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import java.util.List;

@CrossOrigin(origins = "*") // Allow frontend calls
@RestController
@RequestMapping("/api/events")
public class EventController {

    @Autowired
    private EventRepository eventRepository;

    @GetMapping
    public ResponseEntity<List<Event>> getEvents() {
        System.out.println(" API Called: /api/events");
        List<Event> events = eventRepository.findAll();

        if (events.isEmpty()) {
            System.out.println(" No events found in MongoDB!");
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(List.of());
        }

        System.out.println(" Events Retrieved: " + events.size());
        return ResponseEntity.ok(events);
    }
}
