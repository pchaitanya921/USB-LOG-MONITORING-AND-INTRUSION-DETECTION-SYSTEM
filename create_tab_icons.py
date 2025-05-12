#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Create Tab Icons Module
Creates icons for the tab bar
"""

from PIL import Image, ImageDraw
import os

def create_dashboard_icon():
    """Create a dashboard icon"""
    # Create directory if it doesn't exist
    os.makedirs("usb_monitor_desktop/assets/icons", exist_ok=True)
    
    # Create a new image with a transparent background
    icon_size = 64
    icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Draw dashboard grid
    color = (0, 255, 0, 255)  # Green
    
    # Draw grid of squares
    square_size = icon_size // 3
    padding = 4
    
    # Top row
    draw.rectangle((padding, padding, square_size - padding, square_size - padding), 
                  outline=color, width=2)
    draw.rectangle((square_size + padding, padding, 2 * square_size - padding, square_size - padding), 
                  outline=color, width=2)
    draw.rectangle((2 * square_size + padding, padding, 3 * square_size - padding, square_size - padding), 
                  outline=color, width=2)
    
    # Middle row
    draw.rectangle((padding, square_size + padding, square_size - padding, 2 * square_size - padding), 
                  outline=color, width=2)
    draw.rectangle((square_size + padding, square_size + padding, 2 * square_size - padding, 2 * square_size - padding), 
                  outline=color, width=2)
    draw.rectangle((2 * square_size + padding, square_size + padding, 3 * square_size - padding, 2 * square_size - padding), 
                  outline=color, width=2)
    
    # Bottom row
    draw.rectangle((padding, 2 * square_size + padding, square_size - padding, 3 * square_size - padding), 
                  outline=color, width=2)
    draw.rectangle((square_size + padding, 2 * square_size + padding, 2 * square_size - padding, 3 * square_size - padding), 
                  outline=color, width=2)
    draw.rectangle((2 * square_size + padding, 2 * square_size + padding, 3 * square_size - padding, 3 * square_size - padding), 
                  outline=color, width=2)
    
    # Save the icon
    icon_path = "usb_monitor_desktop/assets/icons/dashboard.png"
    icon.save(icon_path)
    print(f"Dashboard icon created at {icon_path}")
    return icon_path

def create_devices_icon():
    """Create a devices icon"""
    # Create directory if it doesn't exist
    os.makedirs("usb_monitor_desktop/assets/icons", exist_ok=True)
    
    # Create a new image with a transparent background
    icon_size = 64
    icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Draw USB symbol
    color = (0, 255, 0, 255)  # Green
    
    # Draw USB connector body
    connector_width = icon_size * 0.4
    connector_height = icon_size * 0.6
    connector_x = (icon_size - connector_width) / 2
    connector_y = (icon_size - connector_height) / 2
    
    # Draw USB connector outline
    draw.rectangle((connector_x, connector_y, connector_x + connector_width, connector_y + connector_height), 
                  outline=color, width=3)
    
    # Draw USB connector pins
    pin_width = connector_width * 0.2
    pin_height = connector_height * 0.15
    pin_spacing = connector_width * 0.2
    
    # Left pin
    pin_x = connector_x + pin_spacing
    pin_y = connector_y + connector_height * 0.2
    draw.rectangle((pin_x, pin_y, pin_x + pin_width, pin_y + pin_height), 
                  fill=color)
    
    # Right pin
    pin_x = connector_x + connector_width - pin_spacing - pin_width
    draw.rectangle((pin_x, pin_y, pin_x + pin_width, pin_y + pin_height), 
                  fill=color)
    
    # Draw USB cable
    cable_width = connector_width * 0.3
    cable_x = connector_x + (connector_width - cable_width) / 2
    cable_y = connector_y + connector_height
    cable_height = icon_size * 0.15
    draw.rectangle((cable_x, cable_y, cable_x + cable_width, cable_y + cable_height), 
                  fill=color)
    
    # Save the icon
    icon_path = "usb_monitor_desktop/assets/icons/devices.png"
    icon.save(icon_path)
    print(f"Devices icon created at {icon_path}")
    return icon_path

def create_alert_icon():
    """Create an alert icon"""
    # Create directory if it doesn't exist
    os.makedirs("usb_monitor_desktop/assets/icons", exist_ok=True)
    
    # Create a new image with a transparent background
    icon_size = 64
    icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Draw alert triangle
    color = (0, 255, 0, 255)  # Green
    
    # Triangle points
    triangle_points = [
        (icon_size // 2, 10),  # Top
        (10, icon_size - 15),  # Bottom left
        (icon_size - 10, icon_size - 15)  # Bottom right
    ]
    
    # Draw triangle outline
    draw.polygon(triangle_points, outline=color, width=3)
    
    # Draw exclamation mark
    # Vertical line
    exclamation_width = 4
    exclamation_height = icon_size * 0.3
    exclamation_x = icon_size // 2 - exclamation_width // 2
    exclamation_y = icon_size // 2 - exclamation_height // 2
    draw.rectangle((exclamation_x, exclamation_y, exclamation_x + exclamation_width, exclamation_y + exclamation_height), 
                  fill=color)
    
    # Dot
    dot_radius = 3
    dot_y = exclamation_y + exclamation_height + 5
    draw.ellipse((exclamation_x - dot_radius, dot_y, exclamation_x + exclamation_width + dot_radius, dot_y + 2 * dot_radius), 
                fill=color)
    
    # Save the icon
    icon_path = "usb_monitor_desktop/assets/icons/alert.png"
    icon.save(icon_path)
    print(f"Alert icon created at {icon_path}")
    return icon_path

def create_settings_icon():
    """Create a settings icon"""
    # Create directory if it doesn't exist
    os.makedirs("usb_monitor_desktop/assets/icons", exist_ok=True)
    
    # Create a new image with a transparent background
    icon_size = 64
    icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Draw gear icon
    color = (0, 255, 0, 255)  # Green
    
    # Draw outer circle
    outer_radius = icon_size // 2 - 5
    center = (icon_size // 2, icon_size // 2)
    draw.ellipse((center[0] - outer_radius, center[1] - outer_radius, 
                 center[0] + outer_radius, center[1] + outer_radius), 
                outline=color, width=3)
    
    # Draw inner circle
    inner_radius = outer_radius // 2
    draw.ellipse((center[0] - inner_radius, center[1] - inner_radius, 
                 center[0] + inner_radius, center[1] + inner_radius), 
                outline=color, width=2)
    
    # Draw gear teeth
    num_teeth = 8
    tooth_length = 8
    
    for i in range(num_teeth):
        angle = i * (360 / num_teeth)
        angle_rad = angle * 3.14159 / 180
        
        # Calculate tooth start and end points
        start_x = center[0] + outer_radius * (angle_rad)
        start_y = center[1] + outer_radius * (angle_rad)
        end_x = center[0] + (outer_radius + tooth_length) * (angle_rad)
        end_y = center[1] + (outer_radius + tooth_length) * (angle_rad)
        
        # Draw tooth
        draw.line((start_x, start_y, end_x, end_y), fill=color, width=3)
    
    # Save the icon
    icon_path = "usb_monitor_desktop/assets/icons/settings.png"
    icon.save(icon_path)
    print(f"Settings icon created at {icon_path}")
    return icon_path

if __name__ == "__main__":
    create_dashboard_icon()
    create_devices_icon()
    create_alert_icon()
    create_settings_icon()
