from PIL import Image, ImageDraw, ImageFont
import aggdraw
import os
import qrcode


def generate_price_tag(product_name, item_id, old_price, new_price, discount_type):
    # 1. Choose base template depending on the discount type
    # .strip() removes invisible spaces, .lower() makes it lowercase
    if str(discount_type).strip().lower() == "member card":
        template_filename = 'template_card.png'
    else:
        template_filename = 'template.png'
        
    try:
        tag = Image.open(template_filename)
    except FileNotFoundError: # run this in case we didnt find our file
        print(f"❌ Error: Could not find '{template_filename}'.")
        return

    draw = ImageDraw.Draw(tag) # use out pillow library to draw things on it
        
    # 2. Set up fonts
    try:
        name_font = ImageFont.truetype("Roboto-Bold.ttf", 50)
        title_font = ImageFont.truetype("Roboto-Bold.ttf", 70) 
        price_font = ImageFont.truetype("Roboto-Bold.ttf", 140) 
        small_font = ImageFont.truetype("Roboto-Bold.ttf", 20)
    except IOError:
        title_font = ImageFont.load_default()
        price_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        
    # 3. Calculate Coordinates for writing 
    
    # Product Name
    draw.text((50, 30), product_name, fill="black", font=name_font)
    
    # Item ID (Shoved much closer to the left)
    draw.text((130, 123), str(item_id), fill="black", font=small_font)
    
    # Date 
    draw.text((360, 123), "31 OCT 2026", fill="black", font=small_font)
    
    # Was part 
    draw.text((60, 180), "Was", fill="black", font=name_font)
    
    # Old Price 
    old_price_text = f"${old_price:.2f}"
    start_x = 170
    start_y = 180
    
    draw.text((start_x, start_y), old_price_text, fill="black", font=name_font)
    # Calculate the exact size of the text box
    bbox = draw.textbbox((start_x, start_y), old_price_text, font=name_font)
    left = bbox[0]
    top = bbox[1]
    right = bbox[2]
    bottom = bbox[3]
    
    # To be able to change size of the line
    padding_x = 1
    padding_y = 10 
    
    new_left = left + padding_x
    new_top = top + padding_y
    new_right = right - padding_x
    new_bottom = bottom - padding_y
    
    # Use aggdraw for lines
    canvas = aggdraw.Draw(tag)
    smooth_pen = aggdraw.Pen("black", width=5)
    
    # Draw a diagonal line from top-left to bottom-right
    canvas.line((new_right, new_top, new_left, new_bottom), smooth_pen)
    
    # 4. Flush the aggdraw canvas to permanently apply it to your Pillow image
    canvas.flush()
    
    # New Price 
    draw.text((55, 235), f"${new_price:.2f}", fill="#1a2b56", font=price_font)

    # Percentage OFF
    percent_off = int((1 - (new_price / old_price)) * 100)
    draw.text((55, 400), f"{percent_off}% OFF", fill="#3B5998", font=title_font)
    
    #5. Qrcode set up for each item
    
    # 1. Placeholder URL
    ''' Here can be inserted maybe a link to the item specificaly or if needed changed to the barcode'''
    qr_data = f"www.linkedin.com/in/platon-yesin"
    
    # 2. QR code
    qr_image = qrcode.make(qr_data)
    
    # 3. Size set up
    qr_size = 170  
    qr_image = qr_image.resize((qr_size, qr_size), Image.Resampling.NEAREST)
    
    # 4. Paste it onto the tag
    qr_x = 1004
    qr_y = 382
    tag.paste(qr_image, (qr_x, qr_y))
    
    # 6. Save new made tags
    # Folder to store ready tags
    output_folder = "ready_tags"
    
    # Save
    clean_name = product_name.replace(" ", "_")
    output_filename = f"{clean_name}_tag.jpg"
    
    final_path = os.path.join(output_folder, output_filename)
    
    tag.save(final_path, quality=95) 
    print(f"🖨️  Successfully printed: {output_filename}")
    
    return final_path
    
if __name__ == "__main__":
    generate_price_tag("Organic Gala Apples", 12345, 4, 3.25, "Member Card")
    