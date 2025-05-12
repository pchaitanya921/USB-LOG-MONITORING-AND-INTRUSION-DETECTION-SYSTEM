#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Create Icon Module
Creates a simple USB monitor icon for the application
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_usb_icon():
    """Create a simple USB monitor icon"""
    # Create directory if it doesn't exist
    os.makedirs("usb_monitor_desktop/assets/icons", exist_ok=True)
    
    # Create a new image with a transparent background
    icon_size = 256
    icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Draw a dark background circle
    circle_color = (10, 15, 20, 255)  # Dark blue-gray
    draw.ellipse((10, 10, icon_size-10, icon_size-10), fill=circle_color)
    
    # Draw USB symbol
    usb_color = (0, 255, 0, 255)  # Green
    
    # USB connector body
    connector_width = icon_size * 0.4
    connector_height = icon_size * 0.6
    connector_x = (icon_size - connector_width) / 2
    connector_y = (icon_size - connector_height) / 2
    
    # Draw USB connector outline
    draw.rectangle((connector_x, connector_y, connector_x + connector_width, connector_y + connector_height), 
                  outline=usb_color, width=6)
    
    # Draw USB connector pins
    pin_width = connector_width * 0.2
    pin_height = connector_height * 0.15
    pin_spacing = connector_width * 0.2
    
    # Left pin
    pin_x = connector_x + pin_spacing
    pin_y = connector_y + connector_height * 0.2
    draw.rectangle((pin_x, pin_y, pin_x + pin_width, pin_y + pin_height), 
                  fill=usb_color)
    
    # Right pin
    pin_x = connector_x + connector_width - pin_spacing - pin_width
    draw.rectangle((pin_x, pin_y, pin_x + pin_width, pin_y + pin_height), 
                  fill=usb_color)
    
    # Draw USB cable
    cable_width = connector_width * 0.3
    cable_x = connector_x + (connector_width - cable_width) / 2
    cable_y = connector_y + connector_height
    cable_height = icon_size * 0.15
    draw.rectangle((cable_x, cable_y, cable_x + cable_width, cable_y + cable_height), 
                  fill=usb_color)
    
    # Draw scanning lines
    scan_color = (0, 255, 0, 150)  # Semi-transparent green
    scan_spacing = icon_size * 0.1
    scan_width = 3
    
    for i in range(3):
        scan_y = connector_y - scan_spacing * (i + 1)
        if scan_y > 20:  # Make sure we're still inside the circle
            draw.line((20, scan_y, icon_size-20, scan_y), fill=scan_color, width=scan_width)
    
    # Save the icon in multiple sizes
    icon_path = "usb_monitor_desktop/assets/icons/usb_monitor.png"
    icon.save(icon_path)
    
    # Create ICO file (Windows icon)
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icons = []
    
    for size in icon_sizes:
        resized_icon = icon.resize(size)
        icons.append(resized_icon)
    
    ico_path = "usb_monitor_desktop/assets/icons/usb_monitor.ico"
    icons[0].save(ico_path, format='ICO', sizes=[(i.width, i.height) for i in icons])
    
    print(f"Icon created at {icon_path} and {ico_path}")
    return ico_path

if __name__ == "__main__":
    create_usb_icon()
