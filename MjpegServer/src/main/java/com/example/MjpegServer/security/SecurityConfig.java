package com.example.MjpegServer.security;


import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.core.userdetails.*;
import org.springframework.security.provisioning.InMemoryUserDetailsManager;
import org.springframework.security.crypto.password.NoOpPasswordEncoder;

@Configuration
public class SecurityConfig {

    @Bean
    public InMemoryUserDetailsManager userDetailsService() {
        // --- Camera credentials ---
        UserDetails cam1 = User.withUsername("cam_1")
                .password("cam123")
                .roles("CAMERA")
                .build();

        UserDetails cam2 = User.withUsername("cam_back")
                .password("back123")
                .roles("CAMERA")
                .build();

        // --- Viewer credentials ---
        UserDetails admin = User.withUsername("admin")
                .password("admin123")
                .roles("VIEWER")
                .build();

        UserDetails guest = User.withUsername("guest")
                .password("guest123")
                .roles("VIEWER")
                .build();

        return new InMemoryUserDetailsManager(cam1, cam2, admin, guest);
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .csrf(csrf -> csrf.disable())
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/upload").hasRole("CAMERA")
                        .requestMatchers("/stream/**").hasRole("VIEWER")
                        .anyRequest().authenticated()
                )
                .httpBasic(basic -> {});// simple Basic Auth for ESP32 + browsers
        return http.build();
    }

    // For demo only — disables password encryption
    @Bean
    public static org.springframework.security.crypto.password.PasswordEncoder passwordEncoder() {
        return NoOpPasswordEncoder.getInstance();
    }
}
