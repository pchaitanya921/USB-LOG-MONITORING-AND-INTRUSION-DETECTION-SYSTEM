#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Create Navigation Icons Module
Creates icons for the navigation bar
"""

from PIL import Image, ImageDraw
import os

def create_refresh_icon():
    """Create a refresh icon"""
    # Create directory if it doesn't exist
    os.makedirs("usb_monitor_desktop/assets/icons", exist_ok=True)
    
    # Create a new image with a transparent background
    icon_size = 64
    icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Draw refresh circular arrow
    color = (0, 255, 0, 255)  # Green
    
    # Draw circular arrow
    arrow_width = 4
    outer_radius = icon_size // 2 - 8
    inner_radius = outer_radius - arrow_width
    center = (icon_size // 2, icon_size // 2)
    
    # Draw the circular part (270 degrees to 90 degrees)
    for r in range(inner_radius, outer_radius + 1):
        for angle in range(270, 450):
            x = center[0] + int(r * (angle - 360) / 180 * 3.14159) if angle > 360 else center[0] + int(r * (angle) / 180 * 3.14159)
            y = center[1] + int(r * (angle - 270) / 180 * 3.14159)
            if 0 <= x < icon_size and 0 <= y < icon_size:
                icon.putpixel((x, y), color)
    
    # Draw arrowhead at the end
    arrow_points = [
        (center[0] + outer_radius, center[1]),
        (center[0] + outer_radius - 8, center[1] - 8),
        (center[0] + outer_radius + 4, center[1] - 4)
    ]
    draw.polygon(arrow_points, fill=color)
    
    # Save the icon
    icon_path = "usb_monitor_desktop/assets/icons/refresh.png"
    icon.save(icon_path)
    print(f"Refresh icon created at {icon_path}")
    return icon_path

def create_scan_icon():
    """Create a scan icon"""
    # Create directory if it doesn't exist
    os.makedirs("usb_monitor_desktop/assets/icons", exist_ok=True)
    
    # Create a new image with a transparent background
    icon_size = 64
    icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Draw scan lines
    color = (0, 255, 0, 255)  # Green
    
    # Draw horizontal scan lines
    line_spacing = 8
    line_width = 2
    
    for y in range(10, icon_size - 10, line_spacing):
        draw.rectangle((10, y, icon_size - 10, y + line_width), fill=color)
    
    # Draw scanning frame
    frame_width = 3
    draw.rectangle((5, 5, icon_size - 5, icon_size - 5), outline=color, width=frame_width)
    
    # Draw scanning beam
    beam_width = 6
    beam_height = icon_size - 10
    beam_x = icon_size // 2 - beam_width // 2
    
    # Semi-transparent beam
    beam_color = (0, 255, 0, 100)
    draw.rectangle((beam_x, 5, beam_x + beam_width, 5 + beam_height), fill=beam_color)
    
    # Save the icon
    icon_path = "usb_monitor_desktop/assets/icons/scan.png"
    icon.save(icon_path)
    print(f"Scan icon created at {icon_path}")
    return icon_path

def create_user_icon():
    """Create a user icon"""
    # Create directory if it doesn't exist
    os.makedirs("usb_monitor_desktop/assets/icons", exist_ok=True)
    
    # Create a new image with a transparent background
    icon_size = 64
    icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Draw user icon
    color = (0, 255, 0, 255)  # Green
    
    # Draw head (circle)
    head_radius = icon_size // 6
    head_center = (icon_size // 2, icon_size // 3)
    draw.ellipse((head_center[0] - head_radius, head_center[1] - head_radius,
                 head_center[0] + head_radius, head_center[1] + head_radius), outline=color, width=3)
    
    # Draw body (trapezoid)
    body_top_width = head_radius * 2
    body_bottom_width = head_radius * 3
    body_height = icon_size // 2
    body_top_y = head_center[1] + head_radius + 2
    
    body_points = [
        (head_center[0] - body_top_width // 2, body_top_y),
        (head_center[0] + body_top_width // 2, body_top_y),
        (head_center[0] + body_bottom_width // 2, body_top_y + body_height),
        (head_center[0] - body_bottom_width // 2, body_top_y + body_height)
    ]
    draw.polygon(body_points, outline=color, width=3)
    
    # Save the icon
    icon_path = "usb_monitor_desktop/assets/icons/user.png"
    icon.save(icon_path)
    print(f"User icon created at {icon_path}")
    return icon_path

if __name__ == "__main__":
    create_refresh_icon()
    create_scan_icon()
    create_user_icon()
