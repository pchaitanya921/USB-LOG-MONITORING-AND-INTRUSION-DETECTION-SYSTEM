#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
USB Animation Widget
Provides animated USB connection visualization
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt5.QtGui import QPainter, QColor, QLinearGradient, QPen, QBrush, QPainterPath

class USBAnimation(QWidget):
    """Widget providing an animated USB connection visualization"""
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set attributes
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)

        # Animation properties
        self.animation_step = 0
        self.max_steps = 60
        self.animation_direction = 1  # 1 for forward, -1 for backward
        self.pulse_size = 1.0
        self.pulse_direction = 0.02
        self.data_flow = []
        self.connected = True

        # Colors
        self.usb_color = QColor(0, 255, 0)
        self.port_color = QColor(30, 30, 30)
        self.highlight_color = QColor(0, 255, 0, 150)
        self.data_color = QColor(0, 255, 0, 200)

        # Set minimum size
        self.setMinimumSize(60, 30)

        # Initialize animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)  # 30ms for ~33fps

        # Add initial data flow particles
        self.add_data_particles()

    def add_data_particles(self):
        """Add data flow particles"""
        # Clear existing particles
        self.data_flow = []

        # Add new particles at different positions
        for i in range(5):
            position = i * 0.2  # Spread particles evenly
            self.data_flow.append({
                'position': position,
                'size': 2 + (i % 3),
                'speed': 0.01 + (i % 3) * 0.005
            })

    def update_animation(self):
        """Update animation state"""
        # Update pulse effect
        self.pulse_size += self.pulse_direction
        if self.pulse_size > 1.2 or self.pulse_size < 0.8:
            self.pulse_direction *= -1

        # Update data flow
        for particle in self.data_flow:
            if self.connected:
                particle['position'] += particle['speed']
                if particle['position'] > 1.0:
                    particle['position'] = 0.0

        # Update animation step
        if self.connected:
            self.animation_step += self.animation_direction
            if self.animation_step >= self.max_steps or self.animation_step <= 0:
                self.animation_direction *= -1

        # Trigger repaint
        self.update()

    def set_connected(self, connected):
        """Set the connection state"""
        self.connected = connected

    def paintEvent(self, event):
        """Paint the USB animation"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get widget dimensions
        width = self.width()
        height = self.height()

        # Calculate dimensions
        usb_width = width * 0.4
        usb_height = height * 0.6
        port_width = width * 0.5
        port_height = height * 0.7

        # Draw USB port (right side)
        port_rect = QRectF(
            width - port_width,
            (height - port_height) / 2,
            port_width,
            port_height
        )

        # Port gradient
        port_gradient = QLinearGradient(
            port_rect.topLeft(),
            port_rect.bottomRight()
        )
        port_gradient.setColorAt(0, QColor(40, 40, 40))
        port_gradient.setColorAt(1, QColor(20, 20, 20))

        # Draw port with rounded corners
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(port_gradient))
        painter.drawRoundedRect(port_rect, 2, 2)

        # Draw port inner cutout
        inner_margin = 3
        inner_rect = QRectF(
            port_rect.left() + inner_margin,
            port_rect.top() + inner_margin,
            port_rect.width() - inner_margin * 2,
            port_rect.height() - inner_margin * 2
        )
        painter.setBrush(QBrush(QColor(10, 10, 10)))
        painter.drawRoundedRect(inner_rect, 1, 1)

        # Calculate USB position based on animation
        if self.connected:
            # USB is connected or in the process of connecting
            progress = min(1.0, self.animation_step / (self.max_steps * 0.7))
            usb_x = width - port_width - usb_width + (port_width * 0.8 * progress)
        else:
            # USB is disconnected
            usb_x = width - port_width - usb_width - 5

        # Draw USB device (left side)
        usb_rect = QRectF(
            usb_x,
            (height - usb_height) / 2,
            usb_width,
            usb_height
        )

        # USB gradient with glow effect
        usb_gradient = QLinearGradient(
            usb_rect.topLeft(),
            usb_rect.bottomRight()
        )

        if self.connected:
            glow_intensity = 120 + int(80 * self.pulse_size)
            usb_gradient.setColorAt(0, QColor(0, glow_intensity, 0))
            usb_gradient.setColorAt(1, QColor(0, 180, 0))
        else:
            usb_gradient.setColorAt(0, QColor(100, 100, 100))
            usb_gradient.setColorAt(1, QColor(60, 60, 60))

        # Draw USB with rounded corners
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(usb_gradient))
        painter.drawRoundedRect(usb_rect, 3, 3)

        # Draw USB connector (right side of USB device)
        connector_width = usb_width * 0.3
        connector_height = usb_height * 0.6
        connector_rect = QRectF(
            usb_rect.right() - connector_width,
            usb_rect.top() + (usb_height - connector_height) / 2,
            connector_width,
            connector_height
        )

        # Connector gradient
        connector_gradient = QLinearGradient(
            connector_rect.topLeft(),
            connector_rect.bottomRight()
        )

        if self.connected:
            connector_gradient.setColorAt(0, QColor(0, 200, 0))
            connector_gradient.setColorAt(1, QColor(0, 150, 0))
        else:
            connector_gradient.setColorAt(0, QColor(80, 80, 80))
            connector_gradient.setColorAt(1, QColor(50, 50, 50))

        painter.setBrush(QBrush(connector_gradient))
        painter.drawRect(connector_rect)

        # Draw USB logo on the device
        if usb_rect.width() > 15:
            logo_size = min(usb_rect.width() * 0.5, usb_rect.height() * 0.5)
            logo_x = usb_rect.left() + (usb_rect.width() - logo_size) / 2 - connector_width * 0.5
            logo_y = usb_rect.top() + (usb_rect.height() - logo_size) / 2

            # Draw USB symbol
            painter.setPen(QPen(QColor(0, 0, 0, 180), 1))
            painter.setBrush(QBrush(QColor(255, 255, 255, 180)))

            # Create USB trident path
            path = QPainterPath()

            # Calculate dimensions
            trident_width = logo_size * 0.6
            trident_height = logo_size * 0.8

            # Start at the bottom center
            path.moveTo(logo_x + logo_size/2, logo_y + logo_size)

            # Draw up to the middle
            path.lineTo(logo_x + logo_size/2, logo_y + logo_size - trident_height/2)

            # Draw the three prongs
            # Left prong
            path.lineTo(logo_x + logo_size/2 - trident_width/2, logo_y + logo_size - trident_height/2)
            path.lineTo(logo_x + logo_size/2 - trident_width/2, logo_y + logo_size - trident_height)

            # Middle prong
            path.moveTo(logo_x + logo_size/2, logo_y + logo_size - trident_height/2)
            path.lineTo(logo_x + logo_size/2, logo_y + logo_size - trident_height)

            # Right prong
            path.moveTo(logo_x + logo_size/2, logo_y + logo_size - trident_height/2)
            path.lineTo(logo_x + logo_size/2 + trident_width/2, logo_y + logo_size - trident_height/2)
            path.lineTo(logo_x + logo_size/2 + trident_width/2, logo_y + logo_size - trident_height)

            # Draw the path
            painter.drawPath(path)

        # Draw data flow particles if connected
        if self.connected and progress > 0.8:
            # Calculate the data flow path
            flow_start_x = usb_rect.right() - connector_width * 0.5
            flow_end_x = port_rect.left() + inner_margin * 2
            flow_y = height / 2

            # Draw data particles
            for particle in self.data_flow:
                # Calculate position
                particle_x = flow_start_x + (flow_end_x - flow_start_x) * particle['position']

                # Draw particle
                particle_color = QColor(self.data_color)
                # Ensure alpha value is between 0 and 255
                alpha_value = min(255, max(0, int(150 + (100 * self.pulse_size))))
                particle_color.setAlpha(alpha_value)

                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(particle_color))
                painter.drawEllipse(
                    QPointF(particle_x, flow_y),
                    particle['size'] * self.pulse_size,
                    particle['size'] * self.pulse_size
                )
