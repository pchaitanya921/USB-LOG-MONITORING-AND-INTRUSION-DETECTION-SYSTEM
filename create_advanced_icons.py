#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Create Advanced Icons Module
Creates more advanced and visible icons for the application
"""

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import os
import math

def create_advanced_refresh_icon():
    """Create an advanced refresh icon with better visibility"""
    # Create directory if it doesn't exist
    os.makedirs("usb_monitor_desktop/assets/icons", exist_ok=True)
    
    # Create a new image with a transparent background
    icon_size = 128
    icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Colors
    primary_color = (0, 255, 0, 255)  # Bright green
    glow_color = (0, 255, 0, 100)     # Semi-transparent green for glow
    
    # Draw circular arrow
    center = (icon_size // 2, icon_size // 2)
    outer_radius = icon_size // 2 - 15
    inner_radius = outer_radius - 10
    
    # Draw the circular part (300 degrees to 60 degrees)
    points = []
    
    # Outer arc
    for angle in range(300, 421, 2):  # 300 to 60 degrees (normalized to 420 for the loop)
        rad_angle = math.radians(angle if angle <= 360 else angle - 360)
        x = center[0] + int(outer_radius * math.cos(rad_angle))
        y = center[1] + int(outer_radius * math.sin(rad_angle))
        points.append((x, y))
    
    # Inner arc (in reverse)
    for angle in range(420, 299, -2):  # 60 to 300 degrees (normalized from 420)
        rad_angle = math.radians(angle if angle <= 360 else angle - 360)
        x = center[0] + int(inner_radius * math.cos(rad_angle))
        y = center[1] + int(inner_radius * math.sin(rad_angle))
        points.append((x, y))
    
    # Draw the arrow shape
    draw.polygon(points, fill=primary_color)
    
    # Draw arrowhead at the start
    arrow_size = 15
    arrow_angle = math.radians(300)
    arrow_center_x = center[0] + int(outer_radius * math.cos(arrow_angle))
    arrow_center_y = center[1] + int(outer_radius * math.sin(arrow_angle))
    
    arrow_points = [
        (arrow_center_x, arrow_center_y),
        (arrow_center_x - arrow_size, arrow_center_y - arrow_size),
        (arrow_center_x - arrow_size, arrow_center_y + arrow_size)
    ]
    draw.polygon(arrow_points, fill=primary_color)
    
    # Draw arrowhead at the end
    arrow_angle = math.radians(60)
    arrow_center_x = center[0] + int(outer_radius * math.cos(arrow_angle))
    arrow_center_y = center[1] + int(outer_radius * math.sin(arrow_angle))
    
    arrow_points = [
        (arrow_center_x, arrow_center_y),
        (arrow_center_x + arrow_size, arrow_center_y - arrow_size),
        (arrow_center_x + arrow_size, arrow_center_y + arrow_size)
    ]
    draw.polygon(arrow_points, fill=primary_color)
    
    # Add glow effect
    glow = icon.copy()
    glow = glow.filter(ImageFilter.GaussianBlur(5))
    enhancer = ImageEnhance.Brightness(glow)
    glow = enhancer.enhance(1.5)
    
    # Composite the glow and the original icon
    result = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
    result.paste(glow, (0, 0), glow)
    result.paste(icon, (0, 0), icon)
    
    # Resize to 64x64 for consistency with other icons
    result = result.resize((64, 64), Image.LANCZOS)
    
    # Save the icon
    icon_path = "usb_monitor_desktop/assets/icons/refresh.png"
    result.save(icon_path)
    print(f"Advanced refresh icon created at {icon_path}")
    return icon_path

def create_advanced_scan_icon():
    """Create an advanced scan icon with better visibility"""
    # Create directory if it doesn't exist
    os.makedirs("usb_monitor_desktop/assets/icons", exist_ok=True)
    
    # Create a new image with a transparent background
    icon_size = 128
    icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Colors
    primary_color = (0, 255, 0, 255)  # Bright green
    scan_color = (0, 255, 0, 150)     # Semi-transparent green
    glow_color = (0, 255, 0, 100)     # Semi-transparent green for glow
    
    # Draw USB symbol
    usb_width = icon_size * 0.4
    usb_height = icon_size * 0.6
    usb_x = (icon_size - usb_width) / 2
    usb_y = (icon_size - usb_height) / 2
    
    # Draw USB connector outline
    draw.rectangle((usb_x, usb_y, usb_x + usb_width, usb_y + usb_height), 
                  outline=primary_color, width=4)
    
    # Draw USB connector pins
    pin_width = usb_width * 0.15
    pin_height = usb_height * 0.2
    pin_spacing = usb_width * 0.2
    pin_y = usb_y + usb_height * 0.2
    
    # Left pin
    pin_x = usb_x + pin_spacing
    draw.rectangle((pin_x, pin_y, pin_x + pin_width, pin_y + pin_height), 
                  fill=primary_color)
    
    # Right pin
    pin_x = usb_x + usb_width - pin_spacing - pin_width
    draw.rectangle((pin_x, pin_y, pin_x + pin_width, pin_y + pin_height), 
                  fill=primary_color)
    
    # Draw scanning lines
    scan_spacing = icon_size * 0.1
    scan_width = 3
    scan_length = icon_size * 0.8
    scan_x = (icon_size - scan_length) / 2
    
    for i in range(5):
        scan_y = usb_y - scan_spacing * (i + 1)
        if scan_y > 10:  # Make sure we're still inside the icon
            draw.line((scan_x, scan_y, scan_x + scan_length, scan_y), 
                     fill=scan_color, width=scan_width)
    
    # Add scanning beam
    beam_width = usb_width * 0.2
    beam_x = usb_x + (usb_width - beam_width) / 2
    beam_y1 = 10
    beam_y2 = usb_y
    
    # Draw beam
    points = [
        (beam_x, beam_y2),
        (beam_x + beam_width, beam_y2),
        (beam_x + beam_width * 1.5, beam_y1),
        (beam_x - beam_width * 0.5, beam_y1)
    ]
    draw.polygon(points, fill=glow_color)
    
    # Add glow effect
    glow = icon.copy()
    glow = glow.filter(ImageFilter.GaussianBlur(5))
    enhancer = ImageEnhance.Brightness(glow)
    glow = enhancer.enhance(1.5)
    
    # Composite the glow and the original icon
    result = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
    result.paste(glow, (0, 0), glow)
    result.paste(icon, (0, 0), icon)
    
    # Resize to 64x64 for consistency with other icons
    result = result.resize((64, 64), Image.LANCZOS)
    
    # Save the icon
    icon_path = "usb_monitor_desktop/assets/icons/scan.png"
    result.save(icon_path)
    print(f"Advanced scan icon created at {icon_path}")
    return icon_path

def create_advanced_scan_all_icon():
    """Create an advanced scan all devices icon"""
    # Create directory if it doesn't exist
    os.makedirs("usb_monitor_desktop/assets/icons", exist_ok=True)
    
    # Create a new image with a transparent background
    icon_size = 128
    icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Colors
    primary_color = (0, 255, 0, 255)  # Bright green
    secondary_color = (0, 200, 0, 255)  # Slightly darker green
    glow_color = (0, 255, 0, 100)     # Semi-transparent green for glow
    
    # Draw multiple USB devices
    usb_size = icon_size * 0.25
    positions = [
        (icon_size * 0.25, icon_size * 0.25),  # Top left
        (icon_size * 0.6, icon_size * 0.25),   # Top right
        (icon_size * 0.25, icon_size * 0.6),   # Bottom left
        (icon_size * 0.6, icon_size * 0.6)     # Bottom right
    ]
    
    # Draw each USB device
    for pos in positions:
        # Draw USB connector
        usb_x, usb_y = pos
        draw.rectangle((usb_x, usb_y, usb_x + usb_size, usb_y + usb_size * 1.2), 
                      outline=primary_color, width=3)
        
        # Draw USB connector details
        pin_width = usb_size * 0.15
        pin_height = usb_size * 0.2
        pin_spacing = usb_size * 0.2
        pin_y = usb_y + usb_size * 0.2
        
        # Left pin
        pin_x = usb_x + pin_spacing
        draw.rectangle((pin_x, pin_y, pin_x + pin_width, pin_y + pin_height), 
                      fill=primary_color)
        
        # Right pin
        pin_x = usb_x + usb_size - pin_spacing - pin_width
        draw.rectangle((pin_x, pin_y, pin_x + pin_width, pin_y + pin_height), 
                      fill=primary_color)
    
    # Draw scanning circle
    center = (icon_size // 2, icon_size // 2)
    radius = icon_size * 0.45
    draw.ellipse((center[0] - radius, center[1] - radius, 
                 center[0] + radius, center[1] + radius), 
                outline=primary_color, width=3)
    
    # Draw scanning lines
    for angle in range(0, 360, 45):
        rad_angle = math.radians(angle)
        x1 = center[0] + int(radius * 0.7 * math.cos(rad_angle))
        y1 = center[1] + int(radius * 0.7 * math.sin(rad_angle))
        x2 = center[0] + int(radius * 0.9 * math.cos(rad_angle))
        y2 = center[1] + int(radius * 0.9 * math.sin(rad_angle))
        draw.line((x1, y1, x2, y2), fill=primary_color, width=3)
    
    # Add glow effect
    glow = icon.copy()
    glow = glow.filter(ImageFilter.GaussianBlur(5))
    enhancer = ImageEnhance.Brightness(glow)
    glow = enhancer.enhance(1.5)
    
    # Composite the glow and the original icon
    result = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
    result.paste(glow, (0, 0), glow)
    result.paste(icon, (0, 0), icon)
    
    # Resize to 64x64 for consistency with other icons
    result = result.resize((64, 64), Image.LANCZOS)
    
    # Save the icon
    icon_path = "usb_monitor_desktop/assets/icons/scan_all.png"
    result.save(icon_path)
    print(f"Advanced scan all icon created at {icon_path}")
    return icon_path

if __name__ == "__main__":
    create_advanced_refresh_icon()
    create_advanced_scan_icon()
    create_advanced_scan_all_icon()
