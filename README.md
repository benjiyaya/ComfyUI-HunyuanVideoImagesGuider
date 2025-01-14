# ComfyUI-HunyuanVideoImagesGuider
A specialized node for ComfyUI that enable motion and animation capabilities for image as guider for video processing In Hunyuan Video T2V model weights.

How to use this node , you can check it out in this video : https://youtu.be/fq95OLDVCdU

## Features

### Hunyuan Video Image To Guider
- Smooth camera panning effects (X and Y axis)
- Zoom in/out animations
- Seamless image tiling and repetition
- Customizable frame count and motion strength
- Support for various resize modes
- Optional center cropping

## Installation

1. Clone this repository into your ComfyUI custom nodes directory:
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/benjiyaya/ComfyUI-HunyuanVideoImagesGuider.git
```

2. Restart ComfyUI to load the new nodes

## Usage

### Hunyuan Video Image To Guider

Parameters:
- `image`: Input image
- `move_range_x`: Horizontal motion range (-1.0 to 1.0) (Best range in -0.05 - 0.05)
- `move_range_y`: Vertical motion range (-1.0 to 1.0) (Best range in -0.05 - 0.05)
- `zoom`: Zoom effect strength (0.0 to 0.5)
- `frame_num`: Number of frames to generate (2-150)
- `resize_mode`: Image resize options (disabled/custom/keep_ratio)
- `target_width`: Custom width for resize
- `target_height`: Custom height for resize
- `center_crop`: Enable/disable center cropping

*** For the sampler denoise, good range in 0.7-0.9 , below 0.5 almost no animation for object.

## Technical Details

The nodes utilize PyTorch for efficient tensor operations and implement various optimization techniques:
- Automatic mixed precision
- Efficient memory management
- Batched processing
- Error handling and recovery
- Progress tracking

![showcase](https://github.com/benjiyaya/ComfyUI-HunyuanVideoImagesGuider/blob/main/showcases/2.png?raw=true)


https://github.com/user-attachments/assets/7701fdec-74db-4277-a883-3c204037e5ba



![showcase](https://github.com/benjiyaya/ComfyUI-HunyuanVideoImagesGuider/blob/main/showcases/3.png?raw=true)


https://github.com/user-attachments/assets/e9bec99d-f87e-44b2-95c2-48113085e39b



![showcase](https://github.com/benjiyaya/ComfyUI-HunyuanVideoImagesGuider/blob/main/showcases/4.png?raw=true)



https://github.com/user-attachments/assets/0b88a0d3-9071-4cb8-adae-d47776f27cdd



![showcase](https://github.com/benjiyaya/ComfyUI-HunyuanVideoImagesGuider/blob/main/showcases/8.png?raw=true)


https://github.com/user-attachments/assets/e5a8d3bb-f43b-4a87-bdde-926afd03cd1b


![9](https://github.com/user-attachments/assets/1d0a9384-da46-4102-ab4e-269ee85abe2f)


https://github.com/user-attachments/assets/77bf3cbc-8292-466b-9fff-ae4b7ec2c835




## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use in your own projects.

## Credits

Created by Benji and DeepSeek AI Copilot
