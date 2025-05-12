#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Radial Scanning Animation
Provides animated radial scanning and networking effects for background
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF, QLineF
from PyQt5.QtGui import QPainter, QColor, QRadialGradient, QPen, QBrush, QPainterPath
import random
import math

class NetworkNode:
    """Class representing a network node in the animation"""
    def __init__(self, x, y, size=4):
        self.x = x
        self.y = y
        self.size = size
        self.base_size = size
        self.color = QColor(0, 255, 0, 150)
        self.connections = []
        self.speed_x = random.uniform(-0.5, 0.5)
        self.speed_y = random.uniform(-0.5, 0.5)
        self.pulse_size = 1.0
        self.pulse_direction = random.uniform(0.01, 0.03)
        self.pulse_speed = random.uniform(0.01, 0.03)
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

class RadarScan:
    """Class representing a radar scan animation"""
    def __init__(self, center_x, center_y, max_radius=300, color=QColor(0, 255, 0, 100)):
        self.center_x = center_x
        self.center_y = center_y
        self.current_radius = 0
        self.max_radius = max_radius
        self.color = color
        self.angle = 0
        self.rotation_speed = 2  # degrees per frame
        self.expansion_speed = 2
        self.active = True
        self.scan_width = 30  # degrees
        self.pulse_opacity = 1.0
        self.pulse_direction = -0.01

    def update(self):
        """Update the radar scan"""
        # Rotate the scan
        self.angle = (self.angle + self.rotation_speed) % 360

        # Expand the radius
        self.current_radius += self.expansion_speed
        if self.current_radius > self.max_radius:
            self.current_radius = 0

        # Pulse the opacity
        self.pulse_opacity += self.pulse_direction
        if self.pulse_opacity < 0.3 or self.pulse_opacity > 1.0:
            self.pulse_direction *= -1

class DataPacket:
    """Class representing a data packet in the animation"""
    def __init__(self, start_x, start_y, end_x, end_y, color=QColor(0, 255, 0, 200)):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.progress = 0.0
        self.speed = random.uniform(0.01, 0.03)
        self.color = color
        self.size = random.uniform(2, 4)
        self.active = True

    def update(self):
        """Update the data packet"""
        self.progress += self.speed
        if self.progress >= 1.0:
            self.active = False

class RadialScanningBackground(QWidget):
    """Widget providing an animated radial scanning background with network nodes"""
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set attributes
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Ensure visibility but stay behind other widgets
        self.setAutoFillBackground(False)
        self.lower()  # Make sure it's behind other widgets

        # Initialize animation elements
        self.nodes = []
        self.radar_scans = []
        self.data_packets = []
        self.scan_lines = []

        # Animation settings
        self.node_count = 30
        self.connection_distance = 150
        self.radar_count = 2
        self.scan_interval = 5000  # ms
        self.packet_interval = 500  # ms
        self.scan_line_interval = 3000  # ms

        # Initialize animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)  # 30ms for ~33fps

        # Initialize radar scan timer
        self.radar_timer = QTimer(self)
        self.radar_timer.timeout.connect(self.add_radar_scan)
        self.radar_timer.start(self.scan_interval)

        # Initialize data packet timer
        self.packet_timer = QTimer(self)
        self.packet_timer.timeout.connect(self.add_data_packet)
        self.packet_timer.start(self.packet_interval)

        # Initialize scan line timer
        self.scan_line_timer = QTimer(self)
        self.scan_line_timer.timeout.connect(self.add_scan_line)
        self.scan_line_timer.start(self.scan_line_interval)

        # Create initial nodes
        self.create_nodes()

        # Add initial radar scans
        for _ in range(self.radar_count):
            self.add_radar_scan()

    def create_nodes(self):
        """Create network nodes"""
        # Clear existing nodes
        self.nodes = []

        # Get widget dimensions
        width = max(self.width(), 800)
        height = max(self.height(), 600)

        # Create nodes
        for _ in range(self.node_count):
            x = random.uniform(50, width - 50)
            y = random.uniform(50, height - 50)
            size = random.uniform(2, 5)

            node = NetworkNode(x, y, size)

            # Randomize color slightly
            hue = random.uniform(100, 140)  # Green range
            node.color = QColor.fromHsvF(hue/360, 0.8, 1.0, 0.6)

            self.nodes.append(node)

    def add_radar_scan(self):
        """Add a new radar scan"""
        width = max(self.width(), 800)
        height = max(self.height(), 600)

        # Random position
        center_x = random.uniform(width * 0.3, width * 0.7)
        center_y = random.uniform(height * 0.3, height * 0.7)

        # Random radius
        max_radius = min(width, height) * 0.4

        # Random color (green to cyan range) with higher opacity
        hue = random.uniform(100, 180)
        color = QColor.fromHsvF(hue/360, 0.8, 1.0, 0.4)  # Increased opacity

        # Create radar scan
        radar = RadarScan(center_x, center_y, max_radius, color)
        radar.rotation_speed = random.uniform(1, 3)
        radar.expansion_speed = random.uniform(1, 3)
        radar.scan_width = random.uniform(30, 60)  # Wider scan for better visibility

        self.radar_scans.append(radar)

        # Limit the number of active radar scans
        if len(self.radar_scans) > 3:
            self.radar_scans.pop(0)

    def add_data_packet(self):
        """Add a new data packet between random nodes"""
        if len(self.nodes) < 2:
            return

        # Select random source and target nodes
        source_idx = random.randint(0, len(self.nodes) - 1)
        target_idx = random.randint(0, len(self.nodes) - 1)

        # Ensure source and target are different
        while target_idx == source_idx:
            target_idx = random.randint(0, len(self.nodes) - 1)

        source_node = self.nodes[source_idx]
        target_node = self.nodes[target_idx]

        # Random color (green to cyan range)
        hue = random.uniform(100, 180)
        color = QColor.fromHsvF(hue/360, 0.8, 1.0, 0.7)

        # Create data packet
        packet = DataPacket(source_node.x, source_node.y, target_node.x, target_node.y, color)
        self.data_packets.append(packet)

        # Highlight source and target nodes
        source_node.highlight = True
        source_node.highlight_duration = 30
        target_node.highlight = True
        target_node.highlight_duration = 30

    def add_scan_line(self):
        """Add a horizontal scan line"""
        width = max(self.width(), 800)
        height = max(self.height(), 600)

        # Random y position
        y = random.uniform(50, height - 50)

        # Random direction (up or down)
        direction = 1 if random.random() > 0.5 else -1

        # Random color (green to cyan range) with higher opacity
        hue = random.uniform(100, 180)
        color = QColor.fromHsvF(hue/360, 0.9, 1.0, 0.6)  # Brighter and more opaque

        # Create scan line
        scan_line = {
            'y': y,
            'width': width,
            'speed': random.uniform(1, 3),
            'color': color,
            'direction': direction,
            'active': True
        }

        self.scan_lines.append(scan_line)

    def update_animation(self):
        """Update animation state"""
        width = max(self.width(), 800)
        height = max(self.height(), 600)

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

        # Update radar scans
        for radar in self.radar_scans:
            radar.update()

        # Update data packets
        for packet in self.data_packets[:]:
            packet.update()
            if not packet.active:
                self.data_packets.remove(packet)

        # Update scan lines
        for scan_line in self.scan_lines[:]:
            scan_line['y'] += scan_line['speed'] * scan_line['direction']
            if scan_line['y'] < 0 or scan_line['y'] > height:
                scan_line['active'] = False

            if not scan_line['active']:
                self.scan_lines.remove(scan_line)

        # Trigger repaint
        self.update()

    def paintEvent(self, event):
        """Paint the background animation"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background with high transparency to ensure visibility of animations
        # but not interfere with UI elements
        bg_color = QColor(10, 15, 20, 100)  # More transparent background
        painter.fillRect(self.rect(), bg_color)

        # Draw grid
        self.draw_grid(painter)

        # Draw radar scans
        for radar in self.radar_scans:
            self.draw_radar_scan(painter, radar)

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

    def draw_grid(self, painter):
        """Draw a grid background"""
        width = self.width()
        height = self.height()

        # Set pen for grid lines - brighter color for better visibility
        pen = QPen(QColor(0, 100, 0, 80))  # Brighter green with transparency
        pen.setWidth(1)
        painter.setPen(pen)

        # Draw horizontal grid lines
        grid_spacing = 50
        for y in range(0, height, grid_spacing):
            painter.drawLine(0, y, width, y)

        # Draw vertical grid lines
        for x in range(0, width, grid_spacing):
            painter.drawLine(x, 0, x, height)

    def draw_node(self, painter, node):
        """Draw a network node"""
        # Set brush for node
        if node.highlight:
            # Highlighted node
            brush = QBrush(QColor(0, 255, 255, 200))
        else:
            # Normal node
            brush = QBrush(node.color)

        painter.setPen(Qt.NoPen)
        painter.setBrush(brush)

        # Draw node with pulse effect
        size = node.base_size * node.pulse_size
        painter.drawEllipse(QPointF(node.x, node.y), size, size)

        # Draw glow effect
        glow_gradient = QRadialGradient(node.x, node.y, size * 3)
        glow_color = QColor(node.color)
        glow_color.setAlpha(50)
        glow_gradient.setColorAt(0, glow_color)
        glow_color.setAlpha(0)
        glow_gradient.setColorAt(1, glow_color)

        painter.setBrush(QBrush(glow_gradient))
        painter.drawEllipse(QPointF(node.x, node.y), size * 3, size * 3)

    def draw_connection(self, painter, node1, node2, distance):
        """Draw a connection between two nodes"""
        # Calculate opacity based on distance
        opacity = 1.0 - (distance / self.connection_distance)

        # Set pen for connection
        pen = QPen(QColor(0, 255, 0, int(opacity * 100)))
        pen.setWidth(1)
        painter.setPen(pen)

        # Draw line
        painter.drawLine(QPointF(node1.x, node1.y), QPointF(node2.x, node2.y))

    def draw_radar_scan(self, painter, radar):
        """Draw a radar scan"""
        # Calculate start and end angles for the scan arc
        start_angle = radar.angle - radar.scan_width / 2
        span_angle = radar.scan_width

        # Set brush for scan
        color = QColor(radar.color)
        color.setAlpha(int(color.alpha() * radar.pulse_opacity))

        # Create gradient for the scan
        gradient = QRadialGradient(radar.center_x, radar.center_y, radar.current_radius)
        gradient.setColorAt(0.8, color)
        color.setAlpha(0)
        gradient.setColorAt(1, color)

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)

        # Draw scan arc
        path = QPainterPath()
        path.moveTo(radar.center_x, radar.center_y)

        # Convert angles to 16ths of a degree as required by Qt
        start_angle_16 = int(start_angle * 16)
        span_angle_16 = int(span_angle * 16)

        # Add arc to path
        rect = QRectF(
            radar.center_x - radar.current_radius,
            radar.center_y - radar.current_radius,
            radar.current_radius * 2,
            radar.current_radius * 2
        )
        path.arcTo(rect, start_angle, span_angle)
        path.closeSubpath()

        # Draw the path
        painter.drawPath(path)

        # Draw radar center
        painter.setBrush(QBrush(QColor(0, 255, 0, 150)))
        painter.drawEllipse(QPointF(radar.center_x, radar.center_y), 5, 5)

        # Draw radar line
        pen = QPen(QColor(0, 255, 0, 150))
        pen.setWidth(2)
        painter.setPen(pen)

        # Calculate end point of radar line
        end_x = radar.center_x + radar.current_radius * math.cos(math.radians(radar.angle))
        end_y = radar.center_y + radar.current_radius * math.sin(math.radians(radar.angle))

        painter.drawLine(QPointF(radar.center_x, radar.center_y), QPointF(end_x, end_y))

    def draw_data_packet(self, painter, packet):
        """Draw a data packet"""
        # Calculate current position
        current_x = packet.start_x + (packet.end_x - packet.start_x) * packet.progress
        current_y = packet.start_y + (packet.end_y - packet.start_y) * packet.progress

        # Draw packet
        painter.setBrush(QBrush(packet.color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(current_x, current_y), packet.size, packet.size)

        # Draw trail
        trail_length = 0.1
        if packet.progress > trail_length:
            trail_start_progress = packet.progress - trail_length
            trail_start_x = packet.start_x + (packet.end_x - packet.start_x) * trail_start_progress
            trail_start_y = packet.start_y + (packet.end_y - packet.start_y) * trail_start_progress

            # Create gradient for trail
            gradient = QRadialGradient(current_x, current_y, packet.size * 5)
            trail_color = QColor(packet.color)
            gradient.setColorAt(0, trail_color)
            trail_color.setAlpha(0)
            gradient.setColorAt(1, trail_color)

            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(QPointF(current_x, current_y), packet.size * 5, packet.size * 5)

    def draw_scan_line(self, painter, scan_line):
        """Draw a horizontal scan line"""
        # Set pen for scan line with increased width
        pen = QPen(scan_line['color'])
        pen.setWidth(3)  # Thicker line
        painter.setPen(pen)

        # Draw line
        painter.drawLine(0, int(scan_line['y']), scan_line['width'], int(scan_line['y']))

        # Draw enhanced glow effect
        glow_gradient = QRadialGradient(scan_line['width'] / 2, scan_line['y'], 30)  # Larger radius
        glow_color = QColor(scan_line['color'])
        glow_color.setAlpha(100)  # More visible glow
        glow_gradient.setColorAt(0, glow_color)
        glow_color.setAlpha(0)
        glow_gradient.setColorAt(1, glow_color)

        painter.setBrush(QBrush(glow_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRect(QRectF(0, scan_line['y'] - 15, scan_line['width'], 30))  # Taller glow area

    def resizeEvent(self, event):
        """Handle resize event"""
        super().resizeEvent(event)

        # Recreate nodes when resized
        self.create_nodes()
