# ComfyUI-HunyuanVideoImagesGuider
A specialized node for ComfyUI that enable advanced motion and animation capabilities for image as guider for video processing In Hunyuan Video.

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
git clone https://github.com/yourusername/comfyui-motion-nodes.git
```

2. Restart ComfyUI to load the new nodes

## Usage

### Hunyuan Video Image To Guider

Parameters:
- `image`: Input image
- `move_range_x`: Horizontal motion range (-1.0 to 1.0)
- `move_range_y`: Vertical motion range (-1.0 to 1.0)
- `zoom`: Zoom effect strength (0.0 to 0.5)
- `frame_num`: Number of frames to generate (2-150)
- `resize_mode`: Image resize options (disabled/custom/keep_ratio)
- `target_width`: Custom width for resize
- `target_height`: Custom height for resize
- `center_crop`: Enable/disable center cropping


## Technical Details

The nodes utilize PyTorch for efficient tensor operations and implement various optimization techniques:
- Automatic mixed precision
- Efficient memory management
- Batched processing
- Error handling and recovery
- Progress tracking

![showcase](https://github.com/benjiyaya/ComfyUI-HunyuanVideoImagesGuider/blob/main/showcases/2.png?raw=true)

![showcase](https://github.com/benjiyaya/ComfyUI-HunyuanVideoImagesGuider/blob/main/showcases/3.png?raw=true)

![showcase](https://github.com/benjiyaya/ComfyUI-HunyuanVideoImagesGuider/blob/main/showcases/4.png?raw=true)

![showcase](https://github.com/benjiyaya/ComfyUI-HunyuanVideoImagesGuider/blob/main/showcases/8.png?raw=true)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use in your own projects.

## Credits

Created by Benji and DeepSeek AI Copilot
