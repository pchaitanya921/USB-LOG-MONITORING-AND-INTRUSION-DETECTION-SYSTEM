#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Animation Module
Provides animated backgrounds and UI effects
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QRadialGradient, QPainterPath, QFont

import random
import math

class NetworkNode:
    """Class representing a node in the network animation"""
    def __init__(self, x, y, size=4):
        self.x = x
        self.y = y
        self.size = size
        self.connections = []
        self.speed_x = random.uniform(-0.5, 0.5)
        self.speed_y = random.uniform(-0.5, 0.5)
        self.color = QColor(0, 255, 0, 150)  # Green with transparency
        self.pulse_size = size
        self.pulse_direction = 0.1
        self.pulse_speed = random.uniform(0.05, 0.15)
        self.highlight = False
        self.highlight_duration = 0

    def move(self, width, height, bounds_margin=50):
        """Move the node"""
        self.x += self.speed_x
        self.y += self.speed_y

        # Bounce off edges
        if self.x < bounds_margin or self.x > width - bounds_margin:
            self.speed_x *= -1
        if self.y < bounds_margin or self.y > height - bounds_margin:
            self.speed_y *= -1

        # Keep within bounds
        self.x = max(bounds_margin, min(width - bounds_margin, self.x))
        self.y = max(bounds_margin, min(height - bounds_margin, self.y))

        # Pulse effect
        self.pulse_size += self.pulse_direction * self.pulse_speed
        if self.pulse_size > self.size * 1.5 or self.pulse_size < self.size * 0.8:
            self.pulse_direction *= -1

        # Update highlight
        if self.highlight:
            self.highlight_duration -= 1
            if self.highlight_duration <= 0:
                self.highlight = False

class ScanLine:
    """Class representing a horizontal scanning line"""
    def __init__(self, y, width, speed=2, color=QColor(0, 255, 0, 100)):
        self.y = y
        self.width = width
        self.speed = speed
        self.color = color
        self.active = True
        self.direction = 1  # 1 for down, -1 for up
        self.thickness = 2
        self.glow_size = 10

    def move(self, height):
        """Move the scan line"""
        self.y += self.speed * self.direction

        # Reset when reaching bottom
        if self.y > height + self.glow_size:
            self.active = False

        # Reset when reaching top
        if self.y < -self.glow_size:
            self.active = False

class AnimatedBackground(QWidget):
    """Widget providing an animated background with network nodes and scanning effects"""
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set attributes
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Initialize nodes
        self.nodes = []
        self.scan_lines = []
        self.data_packets = []
        self.text_overlays = []

        # Animation settings
        self.node_count = 20  # Reduced number of nodes
        self.connection_distance = 150
        self.scan_interval = 3000  # ms
        self.packet_interval = 1000  # ms
        self.text_interval = 5000  # ms

        # Initialize animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)  # 30ms for ~33fps

        # Initialize scan timer
        self.scan_timer = QTimer(self)
        self.scan_timer.timeout.connect(self.add_scan_line)
        self.scan_timer.start(self.scan_interval)

        # Initialize data packet timer
        self.packet_timer = QTimer(self)
        self.packet_timer.timeout.connect(self.add_data_packet)
        self.packet_timer.start(self.packet_interval)

        # Initialize text overlay timer
        self.text_timer = QTimer(self)
        self.text_timer.timeout.connect(self.add_text_overlay)
        self.text_timer.start(self.text_interval)

        # Create initial nodes
        self.create_nodes()

    def create_nodes(self):
        """Create initial network nodes"""
        self.nodes = []
        width = self.width() or 800
        height = self.height() or 600

        for _ in range(self.node_count):
            x = random.uniform(50, width - 50)
            y = random.uniform(50, height - 50)
            size = random.uniform(2, 5)
            self.nodes.append(NetworkNode(x, y, size))

    def update_animation(self):
        """Update animation state"""
        width = self.width()
        height = self.height()

        # Move nodes
        for node in self.nodes:
            node.move(width, height)

        # Update connections
        for i, node in enumerate(self.nodes):
            node.connections = []
            for j, other_node in enumerate(self.nodes):
                if i != j:
                    distance = math.sqrt((node.x - other_node.x) ** 2 + (node.y - other_node.y) ** 2)
                    if distance < self.connection_distance:
                        node.connections.append((j, distance))

        # Move scan lines
        for scan_line in self.scan_lines[:]:
            scan_line.move(height)
            if not scan_line.active:
                self.scan_lines.remove(scan_line)

        # Move data packets
        for packet in self.data_packets[:]:
            packet['progress'] += 0.02
            if packet['progress'] >= 1.0:
                self.data_packets.remove(packet)

        # Update text overlays
        for overlay in self.text_overlays[:]:
            overlay['duration'] -= 1
            if overlay['duration'] <= 0:
                self.text_overlays.remove(overlay)

        # Trigger repaint
        self.update()

    def add_scan_line(self):
        """Add a new scan line"""
        width = self.width()
        height = self.height()

        # Randomly start from top or bottom
        if random.random() > 0.5:
            y = -10
            direction = 1
        else:
            y = height + 10
            direction = -1

        # Create scan line with random color
        hue = random.uniform(100, 160)  # Green to blue-green range
        color = QColor.fromHsvF(hue/360, 1.0, 1.0, 0.2)

        scan_line = ScanLine(y, width, speed=random.uniform(1.5, 3.5), color=color)
        scan_line.direction = direction
        scan_line.thickness = random.uniform(1, 3)

        self.scan_lines.append(scan_line)

        # Highlight nodes near the scan line
        for node in self.nodes:
            if abs(node.y - y) < 50:
                node.highlight = True
                node.highlight_duration = 20
                node.color = QColor.fromHsvF(hue/360, 1.0, 1.0, 0.7)

    def add_data_packet(self):
        """Add a new data packet animation between random nodes"""
        if len(self.nodes) < 2:
            return

        # Select random nodes
        node1_idx = random.randint(0, len(self.nodes) - 1)
        node2_idx = random.randint(0, len(self.nodes) - 1)

        # Ensure different nodes
        while node2_idx == node1_idx:
            node2_idx = random.randint(0, len(self.nodes) - 1)

        # Create data packet
        packet = {
            'start_node': node1_idx,
            'end_node': node2_idx,
            'progress': 0.0,
            'color': QColor(0, 255, 0, 200)
        }

        self.data_packets.append(packet)

        # Highlight the nodes
        self.nodes[node1_idx].highlight = True
        self.nodes[node1_idx].highlight_duration = 20
        self.nodes[node2_idx].highlight = True
        self.nodes[node2_idx].highlight_duration = 20

    def add_text_overlay(self):
        """Add a random text overlay"""
        width = self.width()
        height = self.height()

        # Ethical hacking related terms
        terms = [
            "USB MONITORING",
            "SCANNING",
            "DEVICE DETECTION",
            "THREAT ANALYSIS",
            "MALWARE SCAN",
            "SECURITY CHECK",
            "SYSTEM PROTECTION",
            "INTRUSION DETECTION",
            "DEVICE VERIFICATION",
            "ACCESS CONTROL"
        ]

        text = random.choice(terms)
        x = random.uniform(100, width - 100)
        y = random.uniform(100, height - 100)

        overlay = {
            'text': text,
            'x': x,
            'y': y,
            'size': random.uniform(10, 16),
            'color': QColor(0, 255, 0, 100),
            'duration': random.randint(50, 150)
        }

        self.text_overlays.append(overlay)

    def paintEvent(self, event):
        """Paint the background animation"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background
        painter.fillRect(self.rect(), QColor(10, 15, 20))

        # Draw grid lines
        self.draw_grid(painter)

        # Draw scan lines
        for scan_line in self.scan_lines:
            self.draw_scan_line(painter, scan_line)

        # Draw connections
        for i, node in enumerate(self.nodes):
            for j, distance in node.connections:
                other_node = self.nodes[j]
                self.draw_connection(painter, node, other_node, distance)

        # Draw data packets
        for packet in self.data_packets:
            self.draw_data_packet(painter, packet)

        # Draw nodes
        for node in self.nodes:
            self.draw_node(painter, node)

        # Draw text overlays
        for overlay in self.text_overlays:
            self.draw_text_overlay(painter, overlay)

    def draw_grid(self, painter):
        """Draw a subtle grid pattern"""
        width = self.width()
        height = self.height()

        # Set pen for grid lines
        pen = QPen(QColor(30, 50, 40, 50))
        pen.setWidth(1)
        painter.setPen(pen)

        # Draw horizontal grid lines
        grid_spacing = 30
        for y in range(0, height, grid_spacing):
            painter.drawLine(0, y, width, y)

        # Draw vertical grid lines
        for x in range(0, width, grid_spacing):
            painter.drawLine(x, 0, x, height)

    def draw_node(self, painter, node):
        """Draw a network node"""
        # Set brush for node
        if node.highlight:
            brush = QBrush(QColor(0, 255, 200, 200))
        else:
            brush = QBrush(node.color)

        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)

        # Draw node
        painter.drawEllipse(QPointF(node.x, node.y), node.pulse_size, node.pulse_size)

        # Draw glow effect
        if node.highlight:
            glow = QRadialGradient(node.x, node.y, node.size * 4)
            glow.setColorAt(0, QColor(0, 255, 200, 100))
            glow.setColorAt(1, QColor(0, 255, 200, 0))
            painter.setBrush(QBrush(glow))
            painter.drawEllipse(QPointF(node.x, node.y), node.size * 4, node.size * 4)

    def draw_connection(self, painter, node1, node2, distance):
        """Draw a connection between nodes"""
        # Calculate opacity based on distance
        opacity = 1.0 - (distance / self.connection_distance)

        # Set pen for connection
        pen = QPen(QColor(0, 255, 0, int(opacity * 100)))
        pen.setWidth(1)
        painter.setPen(pen)

        # Draw line
        painter.drawLine(QPointF(node1.x, node1.y), QPointF(node2.x, node2.y))

    def draw_scan_line(self, painter, scan_line):
        """Draw a horizontal scanning line"""
        # Draw glow effect
        gradient = QLinearGradient(0, scan_line.y - scan_line.glow_size, 0, scan_line.y + scan_line.glow_size)
        gradient.setColorAt(0, QColor(scan_line.color.red(), scan_line.color.green(), scan_line.color.blue(), 0))
        gradient.setColorAt(0.5, scan_line.color)
        gradient.setColorAt(1, QColor(scan_line.color.red(), scan_line.color.green(), scan_line.color.blue(), 0))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRect(QRectF(0, int(scan_line.y - scan_line.glow_size),
                               scan_line.width, int(scan_line.glow_size * 2)))

        # Draw line
        pen = QPen(QColor(255, 255, 255, 150))
        pen.setWidth(int(scan_line.thickness))
        painter.setPen(pen)
        painter.drawLine(0, int(scan_line.y), scan_line.width, int(scan_line.y))

    def draw_data_packet(self, painter, packet):
        """Draw a data packet animation"""
        start_node = self.nodes[packet['start_node']]
        end_node = self.nodes[packet['end_node']]

        # Calculate current position
        x = start_node.x + (end_node.x - start_node.x) * packet['progress']
        y = start_node.y + (end_node.y - start_node.y) * packet['progress']

        # Draw packet
        painter.setBrush(QBrush(packet['color']))
        painter.setPen(Qt.NoPen)

        # Draw as small square
        size = 4
        painter.drawRect(QRectF(x - size/2, y - size/2, size, size))

        # Draw trail
        trail_length = 10
        for i in range(1, trail_length):
            trail_progress = packet['progress'] - (i * 0.01)
            if trail_progress >= 0:
                trail_x = start_node.x + (end_node.x - start_node.x) * trail_progress
                trail_y = start_node.y + (end_node.y - start_node.y) * trail_progress
                opacity = 1.0 - (i / trail_length)

                trail_color = QColor(packet['color'].red(), packet['color'].green(), packet['color'].blue(),
                                    int(packet['color'].alpha() * opacity * 0.5))
                painter.setBrush(QBrush(trail_color))

                trail_size = size * (1.0 - (i / trail_length))
                painter.drawRect(QRectF(trail_x - trail_size/2, trail_y - trail_size/2, trail_size, trail_size))

    def draw_text_overlay(self, painter, overlay):
        """Draw a text overlay"""
        # Set font
        font = QFont("Courier New", int(overlay['size']))
        font.setBold(True)
        painter.setFont(font)

        # Calculate opacity
        opacity = min(1.0, overlay['duration'] / 30.0)
        color = QColor(overlay['color'].red(), overlay['color'].green(), overlay['color'].blue(),
                      int(overlay['color'].alpha() * opacity))

        # Draw text
        painter.setPen(color)
        painter.drawText(QPointF(overlay['x'], overlay['y']), overlay['text'])

    def resizeEvent(self, event):
        """Handle resize event"""
        super().resizeEvent(event)

        # Recreate nodes when resized
        self.create_nodes()
