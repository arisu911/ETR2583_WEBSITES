"""
Breakout Bites Studio - Commercial Promotional Food Advertisement Poster Generator
Target: 1080 x 1350 px (Instagram 4:5 portrait)
Output: breakout_bites_poster.png

Features:
- High-fidelity commercial food advertisement layout
- Prominently features both products: Biskut Ice Gem & Biskut Choco Bear
- Clearly marked agency-grade product presentation placeholders (Stand-up ziplock pouch)
- Automatically incorporates real photos if `product_ice_gem.png` / `product_choco_bear.png` are provided
- Integrates official brand lettermark and authentic transparent logo typography
- 100% clean vector-rendered icons and badges (zero missing glyphs / tofu boxes)
- 2x supersampled rendering (2160 x 2700) with Lanczos downsampling for razor-sharp visual fidelity
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

# ---------------------------------------------------------
# Configuration & Constants
# ---------------------------------------------------------
TARGET_W = 1080
TARGET_H = 1350
SCALE = 2  # 2x supersampling for high-DPI rasterization
W = TARGET_W * SCALE  # 2160
H = TARGET_H * SCALE  # 2700

OUTPUT_FILENAME = "breakout_bites_poster.png"
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------
# Typography Helper with Fallbacks
# ---------------------------------------------------------
def get_font(name_candidates, size_px, bold=False):
    """Load font with fallbacks from Windows font directory."""
    windir = os.environ.get("WINDIR", r"C:\Windows")
    fonts_dir = os.path.join(windir, "Fonts")

    if isinstance(name_candidates, str):
        name_candidates = [name_candidates]

    for name in name_candidates:
        path = os.path.join(fonts_dir, name)
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, int(size_px * SCALE))
            except Exception:
                continue
    
    return ImageFont.load_default()

# Primary font definitions
FONT_DISPLAY_BOLD = get_font(["bahnschrift.ttf", "segoeuib.ttf", "arialbd.ttf"], 36)
FONT_HERO_HEADLINE = get_font(["bahnschrift.ttf", "impact.ttf", "segoeuib.ttf"], 38)
FONT_CARD_TITLE = get_font(["bahnschrift.ttf", "segoeuib.ttf", "arialbd.ttf"], 27)
FONT_PRICE_MAIN = get_font(["bahnschrift.ttf", "segoeuib.ttf", "arialbd.ttf"], 23)
FONT_CTA_BUTTON = get_font(["bahnschrift.ttf", "segoeuib.ttf", "arialbd.ttf"], 25)
FONT_KICKER = get_font(["bahnschrift.ttf", "segoeuib.ttf"], 12)
FONT_SUBTITLE = get_font(["segoeui.ttf", "Candara.ttf", "arial.ttf"], 15)
FONT_BODY_BOLD = get_font(["segoeuib.ttf", "bahnschrift.ttf", "arialbd.ttf"], 13)
FONT_BODY_REGULAR = get_font(["segoeui.ttf", "arial.ttf"], 12)
FONT_MICRO_LABEL = get_font(["bahnschrift.ttf", "segoeuib.ttf"], 11)
FONT_BADGE = get_font(["bahnschrift.ttf", "segoeuib.ttf"], 11)

# ---------------------------------------------------------
# Color Palette
# ---------------------------------------------------------
CLR_BG_TOP = (9, 14, 25)         # Deep midnight navy
CLR_BG_MID = (15, 23, 40)        # Indigo slate
CLR_BG_BOT = (9, 13, 22)         # Midnight base
CLR_CYAN_ACCENT = (0, 229, 255)  # Brand cyan arrow
CLR_EMERALD = (0, 220, 130)      # Fresh mint/emerald
CLR_GOLD = (255, 190, 50)        # Warm golden biscuit
CLR_CARAMEL = (255, 145, 35)     # Caramel amber
CLR_PINK_ICE = (255, 110, 170)   # Pastel candy pink
CLR_MINT_ICE = (65, 225, 195)    # Pastel candy mint
CLR_LAV_ICE = (185, 140, 255)    # Pastel lavender
CLR_YELLOW_ICE = (255, 220, 75)  # Pastel candy yellow
CLR_CHOCO_DARK = (60, 32, 16)    # Rich dark cocoa
CLR_CHOCO_MED = (110, 62, 32)    # Milk chocolate
CLR_WHITE = (255, 255, 255)
CLR_OFFWHITE = (242, 246, 252)
CLR_MUTED_TEXT = (150, 168, 195)

# ---------------------------------------------------------
# Core Geometric & Drawing Primitives
# ---------------------------------------------------------
def draw_vertical_gradient(w, h, top_color, mid_color, bot_color):
    """Generate smooth 3-stop vertical gradient."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    mid_pos = int(h * 0.45)
    
    for y in range(mid_pos):
        t = y / mid_pos
        arr[y, :, 0] = int(top_color[0] * (1 - t) + mid_color[0] * t)
        arr[y, :, 1] = int(top_color[1] * (1 - t) + mid_color[1] * t)
        arr[y, :, 2] = int(top_color[2] * (1 - t) + mid_color[2] * t)
        
    for y in range(mid_pos, h):
        t = (y - mid_pos) / (h - mid_pos)
        arr[y, :, 0] = int(mid_color[0] * (1 - t) + bot_color[0] * t)
        arr[y, :, 1] = int(mid_color[1] * (1 - t) + bot_color[1] * t)
        arr[y, :, 2] = int(mid_color[2] * (1 - t) + bot_color[2] * t)
        
    return Image.fromarray(arr)

def add_radial_spotlight(canvas, center_x, center_y, radius, color_rgb, max_alpha=100):
    """Add a soft radial ambient light glow on the canvas."""
    glow = Image.new("RGBA", (canvas.width, canvas.height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    
    steps = 35
    for i in range(steps, 0, -1):
        r = radius * (i / steps)
        alpha = int(max_alpha * (1 - (i / steps)) ** 1.8)
        bbox = [center_x - r, center_y - r, center_x + r, center_y + r]
        glow_draw.ellipse(bbox, fill=(color_rgb[0], color_rgb[1], color_rgb[2], alpha))
        
    glow = glow.filter(ImageFilter.GaussianBlur(int(28 * SCALE)))
    canvas.alpha_composite(glow)

def draw_sparkle(draw, x, y, size, color):
    """Draw a vibrant 4-pointed food/sugar sparkle star."""
    points = [
        (x, y - size),
        (x + size * 0.22, y - size * 0.22),
        (x + size, y),
        (x + size * 0.22, y + size * 0.22),
        (x, y + size),
        (x - size * 0.22, y + size * 0.22),
        (x - size, y),
        (x - size * 0.22, y - size * 0.22),
    ]
    draw.polygon(points, fill=color)

def draw_diamond_bullet(draw, x, y, size, fill_color, border_color=None):
    """Draw a crisp diamond bullet for feature lists."""
    pts = [
        (x, y - size),
        (x + size, y),
        (x, y + size),
        (x - size, y)
    ]
    draw.polygon(pts, fill=fill_color)
    if border_color:
        draw.polygon(pts, outline=border_color)

def draw_shadowed_rounded_box(canvas, bbox, radius, fill_color, border_color=None, border_width=1, shadow_blur=16, shadow_offset=(0, 10), shadow_color=(0, 0, 0, 160)):
    """Draw a modern card with soft realistic drop shadow and stroke."""
    x0, y0, x1, y1 = bbox
    pad = int((shadow_blur * 2 + abs(shadow_offset[1]) + 20) * SCALE)
    
    sh_w = int((x1 - x0) + pad * 2)
    sh_h = int((y1 - y0) + pad * 2)
    sh_img = Image.new("RGBA", (sh_w, sh_h), (0, 0, 0, 0))
    sh_draw = ImageDraw.Draw(sh_img)
    
    box_sx0 = pad + int(shadow_offset[0] * SCALE)
    box_sy0 = pad + int(shadow_offset[1] * SCALE)
    box_sx1 = box_sx0 + (x1 - x0)
    box_sy1 = box_sy0 + (y1 - y0)
    
    sh_draw.rounded_rectangle([box_sx0, box_sy0, box_sx1, box_sy1], radius=radius, fill=shadow_color)
    sh_img = sh_img.filter(ImageFilter.GaussianBlur(int(shadow_blur * SCALE)))
    
    canvas.alpha_composite(sh_img, (int(x0 - pad), int(y0 - pad)))
    
    card_surface = Image.new("RGBA", (canvas.width, canvas.height), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(card_surface)
    c_draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill_color)
    
    if border_color and border_width > 0:
        c_draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, outline=border_color, width=int(border_width * SCALE))
        
    canvas.alpha_composite(card_surface)

def draw_centered_text(draw, text, y_center, font, fill, canvas_w, x_offset=0):
    """Helper to draw text horizontally centered on canvas."""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (canvas_w - text_w) // 2 + x_offset
    y = y_center - text_h // 2
    draw.text((x, y), text, font=font, fill=fill)
    return (x, y, text_w, text_h)

# ---------------------------------------------------------
# Vector Icon Primitives (Zero Tofu Boxes)
# ---------------------------------------------------------
def draw_clock_icon(draw, cx, cy, radius, color):
    """Draw a clean vector analog clock icon."""
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=color, width=int(1.8 * SCALE))
    draw.line([(cx, cy - int(radius * 0.55)), (cx, cy), (cx + int(radius * 0.45), cy)], fill=color, width=int(1.8 * SCALE))

def draw_location_pin_icon(draw, cx, cy, size, color):
    """Draw a clean vector map marker / pin icon."""
    head_r = int(size * 0.48)
    draw.ellipse([cx - head_r, cy - size + int(2*SCALE), cx + head_r, cy - size + int(2*SCALE) + head_r * 2], fill=color)
    pts = [
        (cx - int(head_r * 0.85), cy - size + head_r + int(3*SCALE)),
        (cx + int(head_r * 0.85), cy - size + head_r + int(3*SCALE)),
        (cx, cy + int(size * 0.25))
    ]
    draw.polygon(pts, fill=color)
    inner_r = int(head_r * 0.4)
    draw.ellipse([cx - inner_r, cy - size + int(2*SCALE) + head_r - inner_r, cx + inner_r, cy - size + int(2*SCALE) + head_r + inner_r], fill=(18, 26, 45))

def draw_payment_card_icon(draw, cx, cy, w_size, h_size, color):
    """Draw a clean vector payment card icon."""
    x0 = cx - w_size // 2
    y0 = cy - h_size // 2
    x1 = cx + w_size // 2
    y1 = cy + h_size // 2
    draw.rounded_rectangle([x0, y0, x1, y1], radius=int(3 * SCALE), outline=color, width=int(1.6 * SCALE))
    draw.line([(x0, y0 + int(h_size * 0.35)), (x1, y0 + int(h_size * 0.35))], fill=color, width=int(1.6 * SCALE))
    draw.rectangle([x0 + int(4 * SCALE), y1 - int(5 * SCALE), x0 + int(10 * SCALE), y1 - int(3 * SCALE)], fill=color)

def draw_flame_icon(draw, cx, cy, size, color):
    """Draw a clean vector flame badge icon."""
    pts = [
        (cx, cy - size),
        (cx + int(size * 0.5), cy - int(size * 0.2)),
        (cx + int(size * 0.7), cy + int(size * 0.4)),
        (cx + int(size * 0.3), cy + size),
        (cx - int(size * 0.3), cy + size),
        (cx - int(size * 0.7), cy + int(size * 0.4)),
        (cx - int(size * 0.5), cy - int(size * 0.2))
    ]
    draw.polygon(pts, fill=color)
    # Inner flame
    in_s = int(size * 0.5)
    in_pts = [
        (cx, cy - in_s + int(6*SCALE)),
        (cx + int(in_s * 0.5), cy + int(in_s * 0.5)),
        (cx, cy + in_s),
        (cx - int(in_s * 0.5), cy + int(in_s * 0.5))
    ]
    draw.polygon(in_pts, fill=(255, 255, 255))

def draw_instagram_vector_icon(draw, cx, cy, size, color):
    """Draw a clean vector camera icon for Instagram."""
    r = size // 2
    draw.rounded_rectangle([cx - r, cy - r, cx + r, cy + r], radius=int(6*SCALE), outline=color, width=int(1.8*SCALE))
    draw.ellipse([cx - int(r*0.48), cy - int(r*0.48), cx + int(r*0.48), cy + int(r*0.48)], outline=color, width=int(1.8*SCALE))
    draw.ellipse([cx + int(r*0.52), cy - int(r*0.52), cx + int(r*0.68), cy - int(r*0.36)], fill=color)

def draw_tiktok_vector_icon(draw, cx, cy, size, color):
    """Draw a clean vector musical note icon for TikTok."""
    x = cx - int(size * 0.25)
    y = cy - int(size * 0.45)
    w = int(size * 0.2)
    h = int(size * 0.8)
    draw.ellipse([x - int(size * 0.3), y + h - int(size * 0.4), x + int(size * 0.2), y + h], fill=color)
    draw.rectangle([x, y, x + w, y + h - int(size * 0.2)], fill=color)
    draw.arc([x, y, x + int(size * 0.75), y + int(size * 0.65)], start=270, end=360, fill=color, width=w)

# ---------------------------------------------------------
# Official Logo Extraction & Compositing
# ---------------------------------------------------------
def get_transparent_brand_logo(max_width_px):
    """
    Extracts the official BREAKOUT BITES STUDIO logo with its authentic
    typography and cyan arrow, removing the dark background into a clean alpha mask.
    """
    logo_path = os.path.join(WORKSPACE_DIR, "Breakout_Bites_Studio_logo_design_2K_20260912230154.png")
    if not os.path.exists(logo_path):
        return None
        
    try:
        raw_logo = Image.open(logo_path).convert("RGB")
        # Crop to the primary text area (BREAKOUT BITES STUDIO)
        crop = raw_logo.crop((360, 390, 2390, 940))
        
        arr = np.array(crop).astype(float)
        bg = np.array([15.0, 23.0, 41.0])
        diff = np.linalg.norm(arr - bg, axis=2)
        
        # High quality alpha keying with smooth anti-aliased edge
        alpha = np.clip((diff - 22.0) / 48.0 * 255.0, 0, 255).astype(np.uint8)
        
        rgba = np.dstack([arr.astype(np.uint8), alpha])
        logo_img = Image.fromarray(rgba)
        
        # Resize to fit header
        aspect = logo_img.height / logo_img.width
        target_w = int(max_width_px * SCALE)
        target_h = int(target_w * aspect)
        return logo_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    except Exception as e:
        print(f"[!] Note: Using text fallback for logo: {e}")
        return None

# ---------------------------------------------------------
# Stand-up Pouch Packaging Showcase & Placeholder
# ---------------------------------------------------------
def draw_pouch_packaging_mockup(canvas, box_bbox, product_type):
    """
    Renders an authentic, commercial food packaging showcase (stand-up ziplock pouch)
    featuring clearly marked product placeholders as specified in requirements.
    If actual product photos ('product_ice_gem.png' or 'product_choco_bear.png') are placed
    in the workspace, it automatically displays the real photograph seamlessly.
    """
    x0, y0, x1, y1 = box_bbox
    box_w = x1 - x0
    box_h = y1 - y0
    
    pw = int(box_w * 0.78)
    ph = int(box_h * 0.83)
    px0 = x0 + (box_w - pw) // 2
    py0 = y0 + int(box_h * 0.07)
    px1 = px0 + pw
    py1 = py0 + ph
    
    layer = Image.new("RGBA", (canvas.width, canvas.height), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    
    if product_type == "ice_gem":
        pouch_rim = (0, 210, 230, 210)
        pouch_bg = (24, 30, 52, 245)
        accent_clr = CLR_CYAN_ACCENT
        photo_filename = "product_ice_gem.png"
    else:
        pouch_rim = (255, 160, 45, 210)
        pouch_bg = (42, 26, 18, 245)
        accent_clr = CLR_GOLD
        photo_filename = "product_choco_bear.png"

    # 1. Pouch Drop Shadow
    sh_layer = Image.new("RGBA", (canvas.width, canvas.height), (0, 0, 0, 0))
    sh_draw = ImageDraw.Draw(sh_layer)
    sh_draw.rounded_rectangle([px0, py0, px1, py1], radius=int(22 * SCALE), fill=(0, 0, 0, 160))
    sh_layer = sh_layer.filter(ImageFilter.GaussianBlur(int(14 * SCALE)))
    canvas.alpha_composite(sh_layer)
    
    # 2. Pouch Body Outer Shell
    d.rounded_rectangle([px0, py0, px1, py1], radius=int(22 * SCALE), fill=pouch_bg, outline=pouch_rim, width=int(2.5 * SCALE))
    
    # 3. Metallic Heat-Seal Strip & Grip Texture
    seal_h = int(32 * SCALE)
    d.rectangle([px0 + int(3*SCALE), py0, px1 - int(3*SCALE), py0 + seal_h], fill=(pouch_bg[0]+22, pouch_bg[1]+22, pouch_bg[2]+22, 255))
    
    for rx in range(px0 + int(14 * SCALE), px1 - int(14 * SCALE), int(8 * SCALE)):
        d.line([(rx, py0 + int(6 * SCALE)), (rx, py0 + seal_h - int(6 * SCALE))], fill=(255, 255, 255, 40), width=int(1.5 * SCALE))
    
    # Left & Right Tear Notches
    notch_y = py0 + int(16 * SCALE)
    notch_s = int(8 * SCALE)
    bg_fill_card = (18, 28, 48) if product_type == "ice_gem" else (34, 24, 20)
    d.polygon([(px0 - int(2*SCALE), notch_y - notch_s), (px0 + notch_s, notch_y), (px0 - int(2*SCALE), notch_y + notch_s)], fill=bg_fill_card)
    d.polygon([(px1 + int(2*SCALE), notch_y - notch_s), (px1 - notch_s, notch_y), (px1 + int(2*SCALE), notch_y + notch_s)], fill=bg_fill_card)
    
    # Ziplock Line
    zip_y = py0 + seal_h + int(10 * SCALE)
    d.line([(px0 + int(12*SCALE), zip_y), (px1 - int(12*SCALE), zip_y)], fill=accent_clr + (190,), width=int(2 * SCALE))
    
    # 4. Translucent Front Food Window
    win_pad_x = int(22 * SCALE)
    win_x0 = px0 + win_pad_x
    win_x1 = px1 - win_pad_x
    win_y0 = zip_y + int(16 * SCALE)
    win_y1 = py1 - int(56 * SCALE)
    
    d.rounded_rectangle([win_x0, win_y0, win_x1, win_y1], radius=int(16 * SCALE), fill=(10, 16, 26, 235), outline=accent_clr + (110,), width=int(2 * SCALE))
    
    # Check for actual photo file in workspace
    real_photo_path = os.path.join(WORKSPACE_DIR, photo_filename)
    has_real_photo = os.path.exists(real_photo_path)
    
    win_cx = (win_x0 + win_x1) // 2
    win_cy = (win_y0 + win_y1) // 2 - int(16 * SCALE)
    
    if has_real_photo:
        try:
            # Composite real product photo inside window
            r_photo = Image.open(real_photo_path).convert("RGBA")
            p_w = win_x1 - win_x0 - int(12 * SCALE)
            p_h = win_y1 - win_y0 - int(48 * SCALE)
            r_photo = ImageOps.fit(r_photo, (p_w, p_h), Image.Resampling.LANCZOS)
            canvas.paste(r_photo, (win_x0 + int(6*SCALE), win_y0 + int(6*SCALE)), r_photo)
        except Exception as err:
            print(f"[!] Error loading real photo {photo_filename}: {err}")
            has_real_photo = False

    if not has_real_photo:
        # Render stylized confection packaging graphic
        if product_type == "ice_gem":
            # 5 stylized Ice Gem confections in a vibrant cluster
            gems = [
                (-int(64 * SCALE), int(8 * SCALE), CLR_PINK_ICE, int(22 * SCALE)),
                (-int(28 * SCALE), -int(18 * SCALE), CLR_YELLOW_ICE, int(25 * SCALE)),
                (int(12 * SCALE), int(10 * SCALE), CLR_MINT_ICE, int(22 * SCALE)),
                (int(54 * SCALE), -int(12 * SCALE), CLR_LAV_ICE, int(24 * SCALE)),
                (int(36 * SCALE), int(16 * SCALE), (120, 200, 255), int(20 * SCALE))
            ]
            for gx, gy, gcolor, gr in gems:
                cx = win_cx + gx
                cy = win_cy + gy
                
                # Biscuit base
                base_rx = gr
                base_ry = int(gr * 0.55)
                d.ellipse([cx - base_rx, cy + int(6*SCALE) - base_ry, cx + base_rx, cy + int(6*SCALE) + base_ry], fill=(215, 160, 75))
                d.ellipse([cx - base_rx*0.85, cy + int(5*SCALE) - base_ry*0.75, cx + base_rx*0.85, cy + int(5*SCALE) + base_ry*0.75], fill=(240, 185, 100))
                # Spun sugar icing star
                draw_sparkle(d, cx, cy - int(12 * SCALE), int(gr * 0.95), gcolor)
                draw_sparkle(d, cx, cy - int(12 * SCALE), int(gr * 0.45), CLR_WHITE)
                
        else:
            # Stylized Chocolate Bear Confections with rich cocoa swirl
            # Cocoa fudge wave in background
            d.ellipse([win_cx - int(90*SCALE), win_cy - int(10*SCALE), win_cx + int(90*SCALE), win_cy + int(50*SCALE)], fill=CLR_CHOCO_DARK)
            
            bears = [
                (-int(52 * SCALE), int(8 * SCALE), int(22 * SCALE)),
                (0, -int(16 * SCALE), int(27 * SCALE)),
                (int(52 * SCALE), int(8 * SCALE), int(22 * SCALE))
            ]
            for bx, by, br in bears:
                cx = win_cx + bx
                cy = win_cy + by
                
                # Bear ears
                ear_r = int(br * 0.38)
                d.ellipse([cx - int(br*0.7) - ear_r, cy - int(br*0.6) - ear_r, cx - int(br*0.7) + ear_r, cy - int(br*0.6) + ear_r], fill=(225, 168, 90))
                d.ellipse([cx + int(br*0.7) - ear_r, cy - int(br*0.6) - ear_r, cx + int(br*0.7) + ear_r, cy - int(br*0.6) + ear_r], fill=(225, 168, 90))
                
                # Head
                d.ellipse([cx - br, cy - int(br*0.85), cx + br, cy + int(br*0.85)], fill=(238, 186, 110), outline=(198, 138, 68), width=int(1.5*SCALE))
                # Muzzle
                muz_w = int(br * 0.48)
                muz_h = int(br * 0.35)
                d.ellipse([cx - muz_w, cy + int(2*SCALE) - muz_h, cx + muz_w, cy + int(2*SCALE) + muz_h], fill=(255, 230, 180))
                # Chocolate eyes & nose
                eye_r = int(2.5 * SCALE)
                d.ellipse([cx - int(br*0.35) - eye_r, cy - int(br*0.25) - eye_r, cx - int(br*0.35) + eye_r, cy - int(br*0.25) + eye_r], fill=CLR_CHOCO_DARK)
                d.ellipse([cx + int(br*0.35) - eye_r, cy - int(br*0.25) - eye_r, cx + int(br*0.35) + eye_r, cy - int(br*0.25) + eye_r], fill=CLR_CHOCO_DARK)
                d.ellipse([cx - int(3*SCALE), cy + int(br*0.05) - int(2.5*SCALE), cx + int(3*SCALE), cy + int(br*0.05) + int(2.5*SCALE)], fill=CLR_CHOCO_DARK)

    # 5. High-Impact Agency Placeholder Badge
    badge_h = int(30 * SCALE)
    badge_y0 = win_y1 - badge_h - int(8 * SCALE)
    badge_y1 = win_y1 - int(8 * SCALE)
    badge_x0 = win_x0 + int(10 * SCALE)
    badge_x1 = win_x1 - int(10 * SCALE)
    
    d.rounded_rectangle([badge_x0, badge_y0, badge_x1, badge_y1], radius=int(6*SCALE), fill=(12, 18, 30, 245), outline=accent_clr, width=int(1.5*SCALE))
    
    ph_text = "[ PRODUCT PHOTO PLACEHOLDER ]" if not has_real_photo else "[ OFFICIAL PACKAGING SNAPSHOT ]"
    tb = d.textbbox((0, 0), ph_text, font=FONT_MICRO_LABEL)
    tw = tb[2] - tb[0]
    th = tb[3] - tb[1]
    d.text((badge_x0 + (badge_x1 - badge_x0 - tw)//2, badge_y0 + (badge_h - th)//2), ph_text, font=FONT_MICRO_LABEL, fill=accent_clr)
    
    # 6. Lower Pouch Specs
    spec_text = "140g FOOD-GRADE STAND-UP ZIPLOCK POUCH"
    tb_s = d.textbbox((0, 0), spec_text, font=FONT_MICRO_LABEL)
    tw_s = tb_s[2] - tb_s[0]
    d.text((px0 + (pw - tw_s)//2, py1 - int(38 * SCALE)), spec_text, font=FONT_MICRO_LABEL, fill=CLR_MUTED_TEXT)
    
    # Gusset crease
    gusset_y = py1 - int(14 * SCALE)
    d.arc([px0 + int(18*SCALE), gusset_y - int(10*SCALE), px1 - int(18*SCALE), gusset_y + int(6*SCALE)], start=0, end=180, fill=(255, 255, 255, 60), width=int(1.5*SCALE))

    canvas.alpha_composite(layer)

# ---------------------------------------------------------
# Main Generator Routine
# ---------------------------------------------------------
def generate_breakout_bites_poster():
    print(f"[*] Initializing canvas at {W}x{H} (2x supersampled for {TARGET_W}x{TARGET_H} target)...")
    
    # 1. Base Gradient Canvas
    bg_rgb = draw_vertical_gradient(W, H, CLR_BG_TOP, CLR_BG_MID, CLR_BG_BOT)
    canvas = bg_rgb.convert("RGBA")
    
    # 2. Ambient Spotlights & Atmospheric Lighting
    print("[*] Rendering ambient spotlights and confection sparkles...")
    # Center-top branding cyan glow
    add_radial_spotlight(canvas, W // 2, int(150 * SCALE), int(360 * SCALE), CLR_CYAN_ACCENT, max_alpha=65)
    # Left card pastel pink glow
    add_radial_spotlight(canvas, int(285 * SCALE), int(620 * SCALE), int(420 * SCALE), CLR_PINK_ICE, max_alpha=75)
    # Right card warm amber/caramel glow
    add_radial_spotlight(canvas, int(795 * SCALE), int(620 * SCALE), int(420 * SCALE), CLR_CARAMEL, max_alpha=75)
    # Bottom CTA button teal-emerald glow
    add_radial_spotlight(canvas, W // 2, int(1135 * SCALE), int(380 * SCALE), CLR_CYAN_ACCENT, max_alpha=85)
    
    # Vector artwork & sparkles overlay
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_overlay = ImageDraw.Draw(overlay)
    
    np.random.seed(42)
    sparkle_palette = [CLR_CYAN_ACCENT, CLR_PINK_ICE, CLR_GOLD, CLR_WHITE, (180, 220, 255)]
    
    # Subtle bokeh circles
    for _ in range(28):
        bx = np.random.randint(int(40 * SCALE), W - int(40 * SCALE))
        by = np.random.randint(int(60 * SCALE), H - int(60 * SCALE))
        br = np.random.randint(int(6 * SCALE), int(22 * SCALE))
        bcolor = sparkle_palette[np.random.randint(0, len(sparkle_palette))]
        d_overlay.ellipse([bx - br, by - br, bx + br, by + br], fill=bcolor + (25,))
        
    # Crisp 4-point sugar sparkles
    for _ in range(48):
        sx = np.random.randint(int(30 * SCALE), W - int(30 * SCALE))
        sy = np.random.randint(int(40 * SCALE), H - int(40 * SCALE))
        if (int(150 * SCALE) < sy < int(290 * SCALE)) and (int(140 * SCALE) < sx < int(940 * SCALE)):
            continue
        ssize = np.random.randint(int(5 * SCALE), int(14 * SCALE))
        scolor = sparkle_palette[np.random.randint(0, len(sparkle_palette))] + (np.random.randint(140, 240),)
        draw_sparkle(d_overlay, sx, sy, ssize, scolor)
        
    canvas.alpha_composite(overlay)
    draw = ImageDraw.Draw(canvas)
    
    # ---------------------------------------------------------
    # SECTION A: TOP EYEBROW PILL BADGE
    # ---------------------------------------------------------
    print("[*] Drawing Header & Branding...")
    eyebrow_y = int(44 * SCALE)
    eyebrow_text = "NOCTURNAL SNACK INFRASTRUCTURE • CAMPUS DISPATCH"
    
    tb_eye = draw.textbbox((0, 0), eyebrow_text, font=FONT_KICKER)
    eye_w = tb_eye[2] - tb_eye[0]
    eye_h = tb_eye[3] - tb_eye[1]
    
    eye_pad_x = int(32 * SCALE)
    eye_pad_y = int(7 * SCALE)
    eye_box = [
        (W - eye_w) // 2 - eye_pad_x,
        eyebrow_y - eye_pad_y,
        (W + eye_w) // 2 + eye_pad_x,
        eyebrow_y + eye_h + eye_pad_y
    ]
    draw.rounded_rectangle(eye_box, radius=int(18 * SCALE), fill=(18, 28, 48, 225), outline=(0, 229, 255, 140), width=int(1.5 * SCALE))
    
    # Decorative sparkle stars on left and right of eyebrow
    draw_sparkle(draw, (W - eye_w) // 2 - int(16 * SCALE), eyebrow_y + eye_h // 2, int(6 * SCALE), CLR_CYAN_ACCENT)
    draw_sparkle(draw, (W + eye_w) // 2 + int(16 * SCALE), eyebrow_y + eye_h // 2, int(6 * SCALE), CLR_CYAN_ACCENT)
    draw.text(((W - eye_w) // 2, eyebrow_y), eyebrow_text, font=FONT_KICKER, fill=CLR_CYAN_ACCENT)
    
    # ---------------------------------------------------------
    # SECTION B: BRAND IDENTITY (Official Lettermark & Logo)
    # ---------------------------------------------------------
    brand_center_y = int(115 * SCALE)
    
    # Official Circular Lettermark Icon
    lettermark_path = os.path.join(WORKSPACE_DIR, "App_icon_lettermark_Breakout_Bites_2K_20260912230211.png")
    icon_size = int(68 * SCALE)
    icon_placed = False
    
    # Attempt to load the official transparent typography logo
    transparent_logo = get_transparent_brand_logo(max_width_px=380)
    
    if transparent_logo and os.path.exists(lettermark_path):
        try:
            lm_img = Image.open(lettermark_path).convert("RGBA")
            lm_img = lm_img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            
            mask = Image.new("L", (icon_size, icon_size), 0)
            m_draw = ImageDraw.Draw(mask)
            m_draw.ellipse([0, 0, icon_size, icon_size], fill=255)
            
            # Total width of icon + gap + logo
            total_brand_w = icon_size + int(18 * SCALE) + transparent_logo.width
            start_x = (W - total_brand_w) // 2
            
            icon_x = start_x
            icon_y = brand_center_y - icon_size // 2
            
            draw.ellipse([icon_x - int(3*SCALE), icon_y - int(3*SCALE), icon_x + icon_size + int(3*SCALE), icon_y + icon_size + int(3*SCALE)], outline=CLR_CYAN_ACCENT, width=int(2*SCALE))
            canvas.paste(lm_img, (icon_x, icon_y), mask)
            
            # Paste the official transparent logo typography
            logo_x = start_x + icon_size + int(18 * SCALE)
            logo_y = brand_center_y - transparent_logo.height // 2
            canvas.alpha_composite(transparent_logo, (logo_x, logo_y))
            icon_placed = True
        except Exception as e:
            print(f"[!] Warning: Fallback to drawn title: {e}")
            icon_placed = False
            
    if not icon_placed:
        brand_title = "BREAKOUT BITES STUDIO"
        tb_bt = draw.textbbox((0, 0), brand_title, font=FONT_DISPLAY_BOLD)
        btw = tb_bt[2] - tb_bt[0]
        draw_centered_text(draw, brand_title, brand_center_y - int(12 * SCALE), FONT_DISPLAY_BOLD, CLR_WHITE, W)

    # Brand motto kicker
    brand_motto = "WE DON'T SPECULATE ON CRAVINGS. WE EXECUTE ON DEMAND."
    draw_centered_text(draw, brand_motto, brand_center_y + int(42 * SCALE), FONT_MICRO_LABEL, CLR_CYAN_ACCENT, W)
    
    # Subtle separator line
    sep_y = int(180 * SCALE)
    draw.line([(int(50 * SCALE), sep_y), (W - int(50 * SCALE), sep_y)], fill=(50, 70, 105, 160), width=int(1 * SCALE))
    
    # ---------------------------------------------------------
    # SECTION C: MARKETING HEADLINE & HOOK
    # ---------------------------------------------------------
    headline_y = int(220 * SCALE)
    main_headline = "CRUNCH INTO SWEET NOSTALGIA!"
    
    # Subtle text drop shadow for extra depth
    draw_centered_text(draw, main_headline, headline_y + int(2 * SCALE), FONT_HERO_HEADLINE, (0, 0, 0, 180), W)
    draw_centered_text(draw, main_headline, headline_y, FONT_HERO_HEADLINE, CLR_GOLD, W)
    
    subtagline_y = int(264 * SCALE)
    subtagline_text = "Curated Confectionery Sealed for Peak Revision Crunch • Direct Hostel Delivery"
    draw_centered_text(draw, subtagline_text, subtagline_y, FONT_SUBTITLE, CLR_OFFWHITE, W)
    
    # ---------------------------------------------------------
    # SECTION D: DUAL HERO PRODUCT SHOWCASE CARDS
    # ---------------------------------------------------------
    print("[*] Constructing Dual Hero Product Cards...")
    card_y0 = int(302 * SCALE)
    card_h = int(618 * SCALE)
    card_y1 = card_y0 + card_h
    card1_y0 = card_y0
    card1_y1 = card_y1
    card2_y0 = card_y0
    card2_y1 = card_y1
    
    card_margin = int(45 * SCALE)
    gap = int(26 * SCALE)
    card_w = (W - (card_margin * 2) - gap) // 2  # ~997 px each at 2x
    
    card1_x0 = card_margin
    card1_x1 = card1_x0 + card_w
    
    card2_x0 = card1_x1 + gap
    card2_x1 = card2_x0 + card_w
    
    # Draw Card 1: Biskut Ice Gem (Pastel/Cyan Theme)
    draw_shadowed_rounded_box(
        canvas,
        [card1_x0, card1_y0, card1_x1, card1_y1],
        radius=int(24 * SCALE),
        fill_color=(18, 28, 48, 242),
        border_color=(0, 210, 225, 180),
        border_width=2,
        shadow_blur=18,
        shadow_offset=(0, 12),
        shadow_color=(0, 0, 0, 180)
    )
    
    # Draw Card 2: Biskut Choco Bear (Warm Cocoa/Caramel Theme)
    draw_shadowed_rounded_box(
        canvas,
        [card2_x0, card2_y0, card2_x1, card2_y1],
        radius=int(24 * SCALE),
        fill_color=(34, 24, 20, 242),
        border_color=(255, 160, 40, 180),
        border_width=2,
        shadow_blur=18,
        shadow_offset=(0, 12),
        shadow_color=(0, 0, 0, 180)
    )
    
    # ---------------------------------------------------------
    # CARD 1 CONTENT: BISKUT ICE GEM
    # ---------------------------------------------------------
    c1_pad = int(22 * SCALE)
    
    # Category badge
    c1_badge_text = "ITEM // BB-01 • NOSTALGIC CRUNCH"
    tb_b1 = draw.textbbox((0, 0), c1_badge_text, font=FONT_BADGE)
    draw.rounded_rectangle(
        [card1_x0 + c1_pad, card1_y0 + int(18*SCALE), card1_x0 + c1_pad + (tb_b1[2]-tb_b1[0]) + int(16*SCALE), card1_y0 + int(18*SCALE) + (tb_b1[3]-tb_b1[1]) + int(10*SCALE)],
        radius=int(6*SCALE),
        fill=(0, 180, 216, 50),
        outline=(0, 229, 255, 180),
        width=int(1.5*SCALE)
    )
    draw.text((card1_x0 + c1_pad + int(8*SCALE), card1_y0 + int(22*SCALE)), c1_badge_text, font=FONT_BADGE, fill=CLR_CYAN_ACCENT)
    
    # Product Title
    p1_title = "Biskut Ice Gem"
    draw.text((card1_x0 + c1_pad, card1_y0 + int(56*SCALE)), p1_title, font=FONT_CARD_TITLE, fill=CLR_WHITE)
    
    # Price Tag Pill
    price1_str = "RM 4.00"
    price1_sub = "/ 100g Pouch"
    tb_p1 = draw.textbbox((0, 0), price1_str, font=FONT_PRICE_MAIN)
    p1_tag_w = (tb_p1[2] - tb_p1[0]) + int(112 * SCALE)
    p1_tag_x = card1_x1 - c1_pad - p1_tag_w
    p1_tag_y = card1_y0 + int(48 * SCALE)
    draw.rounded_rectangle([p1_tag_x, p1_tag_y, card1_x1 - c1_pad, p1_tag_y + int(36*SCALE)], radius=int(8*SCALE), fill=(0, 229, 255, 230))
    draw.text((p1_tag_x + int(10*SCALE), p1_tag_y + int(5*SCALE)), price1_str, font=FONT_PRICE_MAIN, fill=(10, 20, 35))
    draw.text((p1_tag_x + int(10*SCALE) + (tb_p1[2]-tb_p1[0]) + int(6*SCALE), p1_tag_y + int(10*SCALE)), price1_sub, font=FONT_MICRO_LABEL, fill=(15, 30, 50))
    
    # Packaging Mockup Showcase Area
    pouch_box1 = [card1_x0 + c1_pad, card1_y0 + int(95*SCALE), card1_x1 - c1_pad, card1_y0 + int(465*SCALE)]
    draw_pouch_packaging_mockup(canvas, pouch_box1, "ice_gem")
    
    # Feature Bullet Points with Crisp Diamond Vectors
    f1_y = card1_y0 + int(480 * SCALE)
    f1_bullets = [
        ("Spun-Sugar Pastel Icing Crowns", CLR_PINK_ICE),
        ("Crispy Button Biscuit Base", CLR_GOLD),
        ("Food-Grade Ziplock Moisture Lock", CLR_CYAN_ACCENT)
    ]
    for bullet_text, icon_clr in f1_bullets:
        draw_diamond_bullet(draw, card1_x0 + c1_pad + int(6*SCALE), f1_y + int(7*SCALE), int(5*SCALE), icon_clr)
        draw.text((card1_x0 + c1_pad + int(20*SCALE), f1_y), bullet_text, font=FONT_BODY_BOLD, fill=CLR_OFFWHITE)
        f1_y += int(26 * SCALE)
        
    # ---------------------------------------------------------
    # CARD 2 CONTENT: BISKUT CHOCO BEAR
    # ---------------------------------------------------------
    c2_pad = int(22 * SCALE)
    
    # Category badge
    c2_badge_text = "ITEM // BB-02 • RICH CHOCOLATE"
    tb_b2 = draw.textbbox((0, 0), c2_badge_text, font=FONT_BADGE)
    draw.rounded_rectangle(
        [card2_x0 + c2_pad, card2_y0 + int(18*SCALE), card2_x0 + c2_pad + (tb_b2[2]-tb_b2[0]) + int(16*SCALE), card2_y0 + int(18*SCALE) + (tb_b2[3]-tb_b2[1]) + int(10*SCALE)],
        radius=int(6*SCALE),
        fill=(255, 140, 0, 50),
        outline=(255, 175, 45, 180),
        width=int(1.5*SCALE)
    )
    draw.text((card2_x0 + c2_pad + int(8*SCALE), card2_y0 + int(22*SCALE)), c2_badge_text, font=FONT_BADGE, fill=CLR_GOLD)
    
    # Product Title
    p2_title = "Biskut Choco Bear"
    draw.text((card2_x0 + c2_pad, card2_y0 + int(56*SCALE)), p2_title, font=FONT_CARD_TITLE, fill=CLR_WHITE)
    
    # Price Tag Pill
    price2_str = "RM 5.00"
    price2_sub = "/ 100g Pouch"
    tb_p2 = draw.textbbox((0, 0), price2_str, font=FONT_PRICE_MAIN)
    p2_tag_w = (tb_p2[2] - tb_p2[0]) + int(112 * SCALE)
    p2_tag_x = card2_x1 - c2_pad - p2_tag_w
    p2_tag_y = card2_y0 + int(48 * SCALE)
    draw.rounded_rectangle([p2_tag_x, p2_tag_y, card2_x1 - c2_pad, p2_tag_y + int(36*SCALE)], radius=int(8*SCALE), fill=(255, 165, 45, 230))
    draw.text((p2_tag_x + int(10*SCALE), p2_tag_y + int(5*SCALE)), price2_str, font=FONT_PRICE_MAIN, fill=(35, 18, 5))
    draw.text((p2_tag_x + int(10*SCALE) + (tb_p2[2]-tb_p2[0]) + int(6*SCALE), p2_tag_y + int(10*SCALE)), price2_sub, font=FONT_MICRO_LABEL, fill=(45, 25, 10))
    
    # Packaging Mockup Showcase Area
    pouch_box2 = [card2_x0 + c2_pad, card2_y0 + int(95*SCALE), card2_x1 - c2_pad, card2_y0 + int(465*SCALE)]
    draw_pouch_packaging_mockup(canvas, pouch_box2, "choco_bear")
    
    # Feature Bullet Points with Crisp Diamond Vectors
    f2_y = card2_y0 + int(480 * SCALE)
    f2_bullets = [
        ("Smooth Rich Chocolate Cream Core", CLR_CARAMEL),
        ("Golden Crisp Bear Biscuit Shell", CLR_GOLD),
        ("Late-Night Revision Sweet Energy Boost", (255, 125, 80))
    ]
    for bullet_text, icon_clr in f2_bullets:
        draw_diamond_bullet(draw, card2_x0 + c2_pad + int(6*SCALE), f2_y + int(7*SCALE), int(5*SCALE), icon_clr)
        draw.text((card2_x0 + c2_pad + int(20*SCALE), f2_y), bullet_text, font=FONT_BODY_BOLD, fill=CLR_OFFWHITE)
        f2_y += int(26 * SCALE)
        
    # ---------------------------------------------------------
    # SECTION E: COMBINED PACKAGE SPECIFICATION (Ice Gem + Choco Bear Bundle)
    # ---------------------------------------------------------
    print("[*] Drawing Combined Bundle Specification Banner...")
    b_y0 = int(942 * SCALE)
    b_h = int(82 * SCALE)
    b_y1 = b_y0 + b_h
    b_box = [card_margin, b_y0, W - card_margin, b_y1]
    
    draw_shadowed_rounded_box(
        canvas,
        b_box,
        radius=int(16 * SCALE),
        fill_color=(25, 34, 58, 252),
        border_color=(255, 195, 45, 210),
        border_width=2,
        shadow_blur=14,
        shadow_offset=(0, 6),
        shadow_color=(0, 0, 0, 150)
    )
    
    # Combo header line with flame icon
    draw_flame_icon(draw, (W // 2) - int(210 * SCALE), b_y0 + int(19 * SCALE), int(10 * SCALE), CLR_CARAMEL)
    draw_flame_icon(draw, (W // 2) + int(210 * SCALE), b_y0 + int(19 * SCALE), int(10 * SCALE), CLR_CARAMEL)
    draw_centered_text(draw, "COMBINED PACKAGE: ICE GEM + CHOCO BEAR BUNDLE", b_y0 + int(19 * SCALE), FONT_BODY_BOLD, CLR_GOLD, W)
    
    # Bundle Deal Pricing & Savings Pill
    b_detail_text = "100g Ice Gem + 100g Choco Bear — RM 8.00 (200g Total)"
    tb_det = draw.textbbox((0, 0), b_detail_text, font=FONT_PRICE_MAIN)
    det_w = tb_det[2] - tb_det[0]
    
    save_badge_text = "COMBINED BUNDLE"
    tb_sav = draw.textbbox((0, 0), save_badge_text, font=FONT_MICRO_LABEL)
    sav_w = tb_sav[2] - tb_sav[0]
    
    total_det_block_w = det_w + int(16 * SCALE) + sav_w + int(16 * SCALE)
    start_det_x = (W - total_det_block_w) // 2
    
    draw.text((start_det_x, b_y0 + int(34 * SCALE)), b_detail_text, font=FONT_PRICE_MAIN, fill=CLR_WHITE)
    
    # Emerald combined badge
    sav_px0 = start_det_x + det_w + int(14 * SCALE)
    sav_py0 = b_y0 + int(34 * SCALE)
    sav_px1 = sav_px0 + sav_w + int(16 * SCALE)
    sav_py1 = sav_py0 + int(24 * SCALE)
    draw.rounded_rectangle([sav_px0, sav_py0, sav_px1, sav_py1], radius=int(6*SCALE), fill=CLR_EMERALD)
    draw.text((sav_px0 + int(8*SCALE), sav_py0 + int(4*SCALE)), save_badge_text, font=FONT_MICRO_LABEL, fill=(10, 24, 38))
    
    b_perks = "100g (RM8) • 200g (RM14) • 300g (RM20) • 400g (RM25) • Symmetrical 1:1 Dual Package"
    draw_centered_text(draw, b_perks, b_y0 + int(67 * SCALE), FONT_MICRO_LABEL, CLR_CYAN_ACCENT, W)
    
    # ---------------------------------------------------------
    # SECTION F: HIGH-IMPACT CALL TO ACTION ("ORDER NOW!")
    # ---------------------------------------------------------
    print("[*] Drawing Call-To-Action Button and Dispatch Info...")
    cta_btn_w = int(520 * SCALE)
    cta_btn_h = int(64 * SCALE)
    cta_btn_x0 = (W - cta_btn_w) // 2
    cta_btn_y0 = int(1045 * SCALE)
    cta_btn_x1 = cta_btn_x0 + cta_btn_w
    cta_btn_y1 = cta_btn_y0 + cta_btn_h
    
    # Glowing back-layer for CTA button
    cta_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cta_glow_draw = ImageDraw.Draw(cta_glow)
    cta_glow_draw.rounded_rectangle(
        [cta_btn_x0 - int(8*SCALE), cta_btn_y0 - int(4*SCALE), cta_btn_x1 + int(8*SCALE), cta_btn_y1 + int(10*SCALE)],
        radius=int(36 * SCALE),
        fill=(0, 229, 255, 150)
    )
    cta_glow = cta_glow.filter(ImageFilter.GaussianBlur(int(14 * SCALE)))
    canvas.alpha_composite(cta_glow)
    
    # Button Surface
    btn_surf = Image.new("RGBA", (canvas.width, canvas.height), (0, 0, 0, 0))
    btn_draw = ImageDraw.Draw(btn_surf)
    btn_draw.rounded_rectangle(
        [cta_btn_x0, cta_btn_y0, cta_btn_x1, cta_btn_y1],
        radius=int(32 * SCALE),
        fill=(0, 229, 255, 255),
        outline=CLR_WHITE,
        width=int(2.5 * SCALE)
    )
    canvas.alpha_composite(btn_surf)
    
    # Clean CTA Button Text with Arrow vectors
    cta_label = "ORDER NOW!  >>"
    draw_centered_text(draw, cta_label, cta_btn_y0 + cta_btn_h // 2, FONT_CTA_BUTTON, (8, 20, 36), W)
    
    # Campus Delivery & Dispatch Metadata Pills (Vector Icons)
    meta_y = int(1128 * SCALE)
    meta_h = int(54 * SCALE)
    col_w = (W - (card_margin * 2)) // 3
    
    meta_cards = [
        ("ACTIVE WINDOW", "8:00 PM – 1:00 AM Daily", "clock"),
        ("CAMPUS DISPATCH", "Siswa Door / Surau Point", "pin"),
        ("PAYMENT METHOD", "DuitNow QR Instant Cashless", "card")
    ]
    
    for i, (m_tag, m_val, icon_type) in enumerate(meta_cards):
        cx = card_margin + i * col_w + col_w // 2
        pw = col_w - int(12 * SCALE)
        
        # Rounded metadata pill
        draw.rounded_rectangle(
            [cx - pw // 2, meta_y, cx + pw // 2, meta_y + meta_h],
            radius=int(10 * SCALE),
            fill=(18, 26, 45, 220),
            outline=(50, 75, 115, 170),
            width=int(1.2 * SCALE)
        )
        
        # Tag header line with vector icon
        tb_tag = draw.textbbox((0, 0), m_tag, font=FONT_MICRO_LABEL)
        tag_w = tb_tag[2] - tb_tag[0]
        
        header_start_x = cx - tag_w // 2 + int(10 * SCALE)
        icon_cx = header_start_x - int(14 * SCALE)
        icon_cy = meta_y + int(15 * SCALE)
        
        if icon_type == "clock":
            draw_clock_icon(draw, icon_cx, icon_cy, int(6 * SCALE), CLR_CYAN_ACCENT)
        elif icon_type == "pin":
            draw_location_pin_icon(draw, icon_cx, icon_cy, int(8 * SCALE), CLR_CYAN_ACCENT)
        else:
            draw_payment_card_icon(draw, icon_cx, icon_cy, int(14 * SCALE), int(10 * SCALE), CLR_CYAN_ACCENT)
            
        draw.text((header_start_x, meta_y + int(9 * SCALE)), m_tag, font=FONT_MICRO_LABEL, fill=CLR_CYAN_ACCENT)
        
        # Value line
        tb_val = draw.textbbox((0, 0), m_val, font=FONT_BODY_BOLD)
        val_w = tb_val[2] - tb_val[0]
        draw.text((cx - val_w // 2, meta_y + int(29 * SCALE)), m_val, font=FONT_BODY_BOLD, fill=CLR_WHITE)

    # ---------------------------------------------------------
    # SECTION G: FOOTER STRIP & SOCIALS
    # ---------------------------------------------------------
    foot_sep_y = int(1204 * SCALE)
    draw.line([(card_margin, foot_sep_y), (W - card_margin, foot_sep_y)], fill=(45, 62, 95, 160), width=int(1 * SCALE))
    
    foot_y = int(1228 * SCALE)
    
    # Social strip with clean vector icons
    soc_text = "Order via WhatsApp & Follow  @breakoutbites.studio  on Instagram & TikTok"
    tb_soc = draw.textbbox((0, 0), soc_text, font=FONT_SUBTITLE)
    soc_w = tb_soc[2] - tb_soc[0]
    
    start_soc_x = (W - soc_w) // 2
    draw.text((start_soc_x, foot_y), soc_text, font=FONT_SUBTITLE, fill=CLR_OFFWHITE)
    
    # Draw vector IG and TikTok icons next to the handle text
    draw_instagram_vector_icon(draw, start_soc_x - int(24 * SCALE), foot_y + int(10 * SCALE), int(14 * SCALE), CLR_CYAN_ACCENT)
    draw_tiktok_vector_icon(draw, start_soc_x + soc_w + int(20 * SCALE), foot_y + int(10 * SCALE), int(14 * SCALE), CLR_CYAN_ACCENT)
    
    copyright_text = "Breakout Bites Studio • Curated Confectionery & Nocturnal Snack Infrastructure • Bandar Penawar"
    draw_centered_text(draw, copyright_text, foot_y + int(36 * SCALE), FONT_MICRO_LABEL, CLR_MUTED_TEXT, W)
    
    # ---------------------------------------------------------
    # FINAL RASTERIZATION: High-Quality Lanczos Downsampling
    # ---------------------------------------------------------
    print(f"[*] Downsampling poster from {W}x{H} to target {TARGET_W}x{TARGET_H} via Lanczos filter...")
    final_poster = canvas.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
    
    output_path = os.path.join(WORKSPACE_DIR, OUTPUT_FILENAME)
    final_poster.save(output_path, "PNG", optimize=True)
    print(f"[SUCCESS] Saved final promotional poster to: {output_path}")
    print(f"Dimensions: {final_poster.size}, Format: {final_poster.format or 'PNG'}")

if __name__ == "__main__":
    generate_breakout_bites_poster()
