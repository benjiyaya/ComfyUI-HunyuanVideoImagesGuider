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
        
        for i in range(frame_num):
            x_pos = start_x + (step_size_x * i * (-1 if pixel_move_range_x < 0 else 1))
            y_pos = start_y + (step_size_y * i * (-1 if pixel_move_range_y < 0 else 1))
            x_pos = int(x_pos)
            y_pos = int(y_pos)
            
            # Calculate zoom for current frame
            current_zoom = (i / (frame_num - 1)) * zoom if zoom > 0 else 0
            if current_zoom > 0:
                crop_width = int(img_width * (1 - current_zoom))
                crop_height = int(img_height * (1 - current_zoom))
                x_start = (img_width - crop_width) // 2
                y_start = (img_height - crop_height) // 2
                
                zoomed = torch.nn.functional.interpolate(
                    image[:, y_start:y_start + crop_height, x_start:x_start + crop_width, :].permute(0, 3, 1, 2),
                    size=(img_height, img_width),
                    mode='bilinear'
                ).permute(0, 2, 3, 1)
            else:
                zoomed = image
            
            canvas = torch.zeros((1, img_height, img_width, image.shape[3]))
            
            # Fill the entire canvas with repeated images
            for y in range(-img_height, img_height * 2, img_height):
                for x in range(-img_width, img_width * 2, img_width):
                    # Calculate the position for this tile
                    tile_x = (x - x_pos) % img_width
                    tile_y = (y - y_pos) % img_height
                    
                    # Calculate where this tile should be placed on the canvas
                    canvas_x = tile_x
                    canvas_y = tile_y
                    
                    # Calculate the visible portion of this tile
                    width = min(img_width - canvas_x, img_width)
                    height = min(img_height - canvas_y, img_height)
                    
                    if width > 0 and height > 0:
                        # Copy the visible portion of the tile to the canvas
                        canvas[0, canvas_y:canvas_y + height, canvas_x:canvas_x + width, :] = \
                            zoomed[0, :height, :width, :]
            
            batch.append(canvas)
        
        return (torch.cat(batch, dim=0),)

NODE_CLASS_MAPPINGS = {
    "Hunyuan Video Image To Guider": ImageMotionGuider,
}