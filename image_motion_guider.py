import torch
import nodes
import folder_paths

class ImageMotionGuider:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": { 
            "image": ("IMAGE",),
            "move_range_x": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.05}),
            "move_range_y": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.05}),
            "zoom": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 0.5, "step": 0.05}),
            "frame_num": ("INT", {"default": 10, "min": 2, "max": 150}),
            "resize_mode": (["disabled", "custom", "keep_ratio"],),
            "target_width": ("INT", {"default": 512, "min": 64, "max": 2048}),
            "target_height": ("INT", {"default": 512, "min": 64, "max": 2048}),
            "center_crop": ("BOOLEAN", {"default": False}),
        }}
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "guide_motion"
    CATEGORY = "image/animation"

    def get_size(self, image):
        image_size = image.size()
        return int(image_size[2]), int(image_size[1])

    def resize_image(self, image, resize_mode, target_width, target_height):
        img_width, img_height = self.get_size(image)
        
        if resize_mode == "disabled":
            return image
            
        if resize_mode == "keep_ratio":
            # Calculate height maintaining aspect ratio
            aspect_ratio = img_height / img_width
            new_height = int(target_width * aspect_ratio)
            target_height = new_height
            
        # Perform resize using interpolation
        resized = torch.nn.functional.interpolate(
            image.permute(0, 3, 1, 2),
            size=(target_height, target_width),
            mode='bilinear',
            align_corners=False
        ).permute(0, 2, 3, 1)
        
        return resized

    def center_crop_image(self, image, should_crop):
        if not should_crop:
            return image
            
        img_width, img_height = self.get_size(image)
        crop_size = min(img_width, img_height)
        
        start_x = (img_width - crop_size) // 2
        start_y = (img_height - crop_size) // 2
        
        cropped = image[:, start_y:start_y + crop_size, start_x:start_x + crop_size, :]
        return cropped

    def guide_motion(self, image, move_range_x, move_range_y, zoom, frame_num, resize_mode, target_width, target_height, center_crop):
        # First apply resize
        image = self.resize_image(image, resize_mode, target_width, target_height)
        
        # Then apply center crop if enabled
        image = self.center_crop_image(image, center_crop)
        
        img_width, img_height = self.get_size(image)
        
        # Convert normalized ranges (-1.0 to 1.0) to pixel values
        pixel_move_range_x = int(move_range_x * img_width)
        pixel_move_range_y = int(move_range_y * img_height)
        
        step_size_x = abs(pixel_move_range_x) / (frame_num - 1) if pixel_move_range_x != 0 else 0
        step_size_y = abs(pixel_move_range_y) / (frame_num - 1) if pixel_move_range_y != 0 else 0
        
        start_x = 0 if pixel_move_range_x > 0 else abs(pixel_move_range_x)
        start_y = 0 if pixel_move_range_y > 0 else abs(pixel_move_range_y)
        
        # For negative motion, adjust the starting positions
        if pixel_move_range_x < 0:
            start_x -= img_width
        if pixel_move_range_y < 0:
            start_y -= img_height
        
        batch = []
        mirrored_x = torch.flip(image, [2])  # Flip horizontally
        mirrored_y = torch.flip(image, [1])  # Flip vertically
        mirrored_both = torch.flip(image, [1, 2])  # Flip both
        
        for i in range(frame_num):
            x_pos = start_x + (step_size_x * i * (-1 if pixel_move_range_x < 0 else 1))
            y_pos = start_y + (step_size_y * i * (-1 if pixel_move_range_y < 0 else 1))
            x_pos = int(x_pos)
            y_pos = int(y_pos)
            x_pos = x_pos % img_width if pixel_move_range_x != 0 else 0
            y_pos = y_pos % img_height if pixel_move_range_y != 0 else 0
            
            # Calculate zoom for current frame
            current_zoom = (i / (frame_num - 1)) * zoom if zoom > 0 else 0
            if current_zoom > 0:
                crop_width = int(img_width * (1 - current_zoom))
                crop_height = int(img_height * (1 - current_zoom))
                x_start = (img_width - crop_width) // 2
                y_start = (img_height - crop_height) // 2
                
                zoomed_original = torch.nn.functional.interpolate(
                    image[:, y_start:y_start + crop_height, x_start:x_start + crop_width, :].permute(0, 3, 1, 2),
                    size=(img_height, img_width),
                    mode='bilinear'
                ).permute(0, 2, 3, 1)
                
                zoomed_mirror_x = torch.nn.functional.interpolate(
                    mirrored_x[:, y_start:y_start + crop_height, x_start:x_start + crop_width, :].permute(0, 3, 1, 2),
                    size=(img_height, img_width),
                    mode='bilinear'
                ).permute(0, 2, 3, 1)
                
                zoomed_mirror_y = torch.nn.functional.interpolate(
                    mirrored_y[:, y_start:y_start + crop_height, x_start:x_start + crop_width, :].permute(0, 3, 1, 2),
                    size=(img_height, img_width),
                    mode='bilinear'
                ).permute(0, 2, 3, 1)
                
                zoomed_mirror_both = torch.nn.functional.interpolate(
                    mirrored_both[:, y_start:y_start + crop_height, x_start:x_start + crop_width, :].permute(0, 3, 1, 2),
                    size=(img_height, img_width),
                    mode='bilinear'
                ).permute(0, 2, 3, 1)
            else:
                zoomed_original = image
                zoomed_mirror_x = mirrored_x
                zoomed_mirror_y = mirrored_y
                zoomed_mirror_both = mirrored_both
            
            canvas = torch.zeros((1, img_height, img_width, image.shape[3]))
            
            # Process vertical sections
            for y_section in range(0, img_height, img_height):
                remaining_height = min(img_height - y_section, img_height)
                current_y = (y_pos + y_section) % img_height
                use_flipped_y = ((y_pos + y_section) // img_height) % 2 == 1
                
                # Process horizontal sections for each vertical section
                for x_section in range(0, img_width, img_width):
                    remaining_width = min(img_width - x_section, img_width)
                    current_x = (x_pos + x_section) % img_width
                    use_flipped_x = ((x_pos + x_section) // img_width) % 2 == 1
                    
                    # Select appropriate image based on flip states
                    if use_flipped_x and use_flipped_y:
                        current_image = zoomed_mirror_both
                    elif use_flipped_x:
                        current_image = zoomed_mirror_x
                    elif use_flipped_y:
                        current_image = zoomed_mirror_y
                    else:
                        current_image = zoomed_original
                    
                    # Calculate dimensions to copy
                    width = min(img_width - current_x, remaining_width)
                    height = min(img_height - current_y, remaining_height)
                    
                    # Copy the section
                    canvas[0, y_section:y_section + height, x_section:x_section + width, :] = \
                        current_image[0, current_y:current_y + height, current_x:current_x + width, :]
            
            batch.append(canvas)
            
        return (torch.cat(batch, dim=0),)

NODE_CLASS_MAPPINGS = {
    "Hunyuan Video Image To Guider": ImageMotionGuider,
}